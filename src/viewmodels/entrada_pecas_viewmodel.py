# =================================================================================
# MÓDULO DO VIEWMODEL DE ENTRADA DE PEÇAS (entrada_pecas_viewmodel.py)
#
# ATUALIZAÇÃO (Issue #32 - Lote):
#   - ViewModel agora é 'stateful', gerenciando uma lista de itens
#     para adicionar em lote.
# =================================================================================
import flet as ft
import logging
from src.database import queries
from src.models.models import Peca
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class EntradaPecasViewModel:
    """
    ViewModel para a tela 'Entrada de Peças' em Lote.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'EntradaPecasView' | None = None
        # Cache de peças carregadas do banco
        self.pecas_disponiveis: List[Peca] = []
        # Estado: Lista de itens que o usuário adicionou ao lote
        self.lote_para_entrada: List[Dict[str, Any]] = []
        logger.debug("EntradaPecasViewModel inicializado.")

    def vincular_view(self, view: 'EntradaPecasView'):
        self._view = view

    def carregar_pecas_ativas(self):
        """Busca a lista de peças ativas e comanda a View para popular o dropdown."""
        if not self._view: return
        logger.info("ViewModel: Carregando lista de peças ativas para o dropdown.")
        try:
            self.pecas_disponiveis = [p for p in queries.obter_pecas() if p.ativo]
            self._view.popular_dropdown_pecas(self.pecas_disponiveis)
        except Exception as e:
            logger.error(f"Erro ao carregar peças: {e}", exc_info=True)
            if self._view: self._view.mostrar_dialogo_feedback("Erro Crítico", "Não foi possível carregar a lista de peças.")

    def adicionar_item_ao_lote(self):
        """Valida e adiciona um item ao lote que será salvo."""
        if not self._view: return
        
        # 1. Pega os dados do *formulário de item*
        dados_item = self._view.obter_dados_item_formulario()
        peca_id = dados_item.get("peca_id")
        quantidade = dados_item.get("quantidade")

        # 2. Validação
        if not peca_id:
            self._view.mostrar_feedback_snackbar("Selecione uma peça.", False)
            return
        if quantidade is None or quantidade <= 0:
            self._view.mostrar_feedback_snackbar("Quantidade deve ser maior que zero.", False)
            return
        
        # Pega o nome da peça para exibição (do cache)
        peca_selecionada = next((p for p in self.pecas_disponiveis if p.id == peca_id), None)
        if not peca_selecionada:
            self._view.mostrar_feedback_snackbar("Peça não encontrada.", False)
            return

        # 3. Adiciona ao estado (lote)
        item_para_lote = {
            "peca_id": peca_id,
            "nome_peca": peca_selecionada.nome,
            "quantidade": quantidade,
            "valor_custo": dados_item.get("valor_custo"),
            "descricao": dados_item.get("descricao", "").strip()
        }
        self.lote_para_entrada.append(item_para_lote)
        
        # 4. Comanda a View
        logger.info(f"Item adicionado ao lote: {item_para_lote['nome_peca']} (Qtd: {quantidade})")
        self._view.atualizar_lista_lote(self.lote_para_entrada)
        self._view.limpar_formulario_item() # Limpa os campos para a próxima adição

    def remover_item_do_lote(self, item_para_remover: Dict[str, Any]):
        """Remove um item do lote antes de salvar."""
        if not self._view: return
        
        self.lote_para_entrada.remove(item_para_remover)
        logger.info(f"Item removido do lote: {item_para_remover['nome_peca']}")
        self._view.atualizar_lista_lote(self.lote_para_entrada)

    def registrar_lote_entrada(self):
        """Envia o lote completo para a camada de dados."""
        if not self._view: return

        # Validação do lote
        if not self.lote_para_entrada:
            self._view.mostrar_dialogo_feedback("Lote Vazio", "Adicione pelo menos uma peça à lista antes de salvar.")
            return

        logger.info(f"ViewModel: Tentando registrar lote com {len(self.lote_para_entrada)} itens.")
        
        try:
            # Chama a query transacional de lote
            sucesso = queries.registrar_entrada_estoque_lote(self.lote_para_entrada)

            if sucesso:
                logger.info("Lote de entrada registrado com sucesso.")
                self.lote_para_entrada.clear() # Limpa o estado
                # Prepara callback para limpar o formulário e a lista
                acao_pos_dialogo = lambda: (self._view.limpar_formulario_item(), self._view.atualizar_lista_lote(self.lote_para_entrada))
                self._view.mostrar_dialogo_feedback("Sucesso!", "Lote de entrada registrado com sucesso!", acao_pos_dialogo)
            else:
                logger.error("ViewModel: A query 'registrar_entrada_estoque_lote' retornou False.")
                self._view.mostrar_dialogo_feedback("Erro no Banco", "Não foi possível registrar o lote no banco de dados.")

        except Exception as e:
            logger.error(f"Erro inesperado ao registrar lote: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback("Erro Crítico", f"Ocorreu uma falha inesperada:\n{e}")

    def cancelar(self, e):
        """Navega de volta para o dashboard."""
        self.lote_para_entrada.clear() # Limpa o estado
        self.page.go("/dashboard")