# =================================================================================
# MÓDULO DO VIEWMODEL DE ENTRADA DE PEÇAS (entrada_pecas_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de registro de entrada
#           de peças no estoque (Issue #32).
# =================================================================================
import flet as ft
import logging
from src.database import queries
from src.models.models import Peca
from typing import List, Optional

# Configura o logger para este módulo.
logger = logging.getLogger(__name__)

class EntradaPecasViewModel:
    """
    ViewModel para a tela 'Entrada de Peças'.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'EntradaPecasView' | None = None
        self.pecas_disponiveis: List[Peca] = []
        logger.debug("EntradaPecasViewModel inicializado.")

    def vincular_view(self, view: 'EntradaPecasView'):
        """Vincula a View ao ViewModel."""
        self._view = view

    def carregar_pecas_ativas(self):
        """Busca a lista de peças ativas e comanda a View para popular o dropdown."""
        if not self._view: return
        logger.info("ViewModel: Carregando lista de peças ativas para o dropdown.")
        try:
            # Busca todas as peças e filtra apenas as ativas
            self.pecas_disponiveis = [p for p in queries.obter_pecas() if p.ativo]
            self._view.popular_dropdown_pecas(self.pecas_disponiveis)
        except Exception as e:
            logger.error(f"Erro ao carregar peças: {e}", exc_info=True)
            self._view.mostrar_dialogo_feedback("Erro Crítico", "Não foi possível carregar a lista de peças.")

    def registrar_entrada(self):
        """Pega dados da View, valida, e comanda o registro da entrada."""
        if not self._view:
            logger.error("ViewModel: Ação 'registrar_entrada' chamada sem uma View vinculada.")
            return

        try:
            dados = self._view.obter_dados_formulario()
            peca_id = dados.get("peca_id")
            quantidade = dados.get("quantidade")
            valor_custo = dados.get("valor_custo")
            descricao = dados.get("descricao", "").strip()

            # --- LÓGICA DE VALIDAÇÃO ---
            if not peca_id:
                self._view.mostrar_dialogo_feedback("Erro de Validação", "Você deve selecionar uma peça.")
                return
            if quantidade is None or quantidade <= 0:
                self._view.mostrar_dialogo_feedback("Erro de Validação", "A quantidade deve ser um número maior que zero.")
                return
            if valor_custo is not None and valor_custo < 0:
                self._view.mostrar_dialogo_feedback("Erro de Validação", "O valor de custo não pode ser negativo.")
                return

            # --- INTERAÇÃO COM A CAMADA DE DADOS ---
            logger.info(f"ViewModel: Tentando registrar entrada para a peça ID {peca_id}.")
            
            sucesso = queries.registrar_entrada_estoque(
                peca_id=peca_id,
                quantidade=quantidade,
                valor_custo=valor_custo,
                descricao=descricao
            )

            if sucesso:
                logger.info("Entrada de estoque registrada com sucesso.")
                # Prepara o callback para limpar o formulário
                acao_pos_dialogo = lambda: self._view.limpar_formulario()
                self._view.mostrar_dialogo_feedback("Sucesso!", "Entrada de estoque registrada com sucesso!", acao_pos_dialogo)
            else:
                logger.error("ViewModel: A query 'registrar_entrada_estoque' retornou False.")
                self._view.mostrar_dialogo_feedback("Erro no Banco", "Não foi possível registrar a entrada no banco de dados.")

        except Exception as e:
            logger.error(f"Erro inesperado ao registrar entrada: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback("Erro Crítico", f"Ocorreu uma falha inesperada:\n{e}")

    def cancelar(self, e):
        """Navega de volta para o dashboard."""
        logger.debug("ViewModel: Entrada de peças cancelada.")
        self.page.go("/dashboard")