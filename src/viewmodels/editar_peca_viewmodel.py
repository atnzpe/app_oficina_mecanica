# =================================================================================
# MÓDULO DO VIEWMODEL DE EDIÇÃO DE PEÇA (editar_peca_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de edição de peças.
# =================================================================================
import flet as ft
import logging
import sqlite3
from src.database import queries
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class EditarPecaViewModel:
    def __init__(self, page: ft.Page, peca_id: int):
        self.page = page
        self.peca_id = peca_id
        self._view: 'EditarPecaView' | None = None
        logger.debug(f"ViewModel de Edição de Peça inicializado para o ID: {self.peca_id}")

    def vincular_view(self, view: 'EditarPecaView'):
        """Vincula a View ao ViewModel."""
        self._view = view
        logger.debug("ViewModel de Edição de Peça vinculado à sua View.")

    def carregar_dados(self):
        """Busca os dados da peça e comanda a View para preencher o formulário."""
        if not self._view: return
        try:
            logger.info(f"ViewModel: buscando dados para a peça ID {self.peca_id}")
            peca = queries.obter_peca_por_id(self.peca_id)
            if peca:
                self._view.preencher_formulario(peca)
                logger.info(f"ViewModel: Dados da peça '{peca.nome}' carregados.")
            else:
                logger.warning(f"ViewModel: Peça com ID {self.peca_id} não encontrada.")
                acao_navegacao = lambda: self.page.go("/gerir_pecas")
                self._view.mostrar_dialogo_feedback("Erro", "Peça não encontrada.", acao_navegacao)
        except Exception as e:
            logger.error(f"Erro crítico ao carregar dados da peça: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback("Erro Crítico", f"Não foi possível carregar os dados da peça.\nErro: {e}")

    def salvar_alteracoes(self):
        """Valida e salva as alterações no banco de dados."""
        if not self._view: return
        try:
            novos_dados = self._view.obter_dados_formulario()
            if not novos_dados['nome'] or not novos_dados['referencia']:
                self._view.mostrar_dialogo_feedback("Erro de Validação", "Os campos 'Nome' e 'Referência' são obrigatórios.")
                return
            if novos_dados['preco_compra'] is None or novos_dados['preco_venda'] is None or novos_dados['quantidade_em_estoque'] is None:
                self._view.mostrar_dialogo_feedback("Erro de Validação", "Preços e Quantidade devem ser números válidos.")
                return

            logger.info(f"ViewModel: salvando alterações para a peça ID {self.peca_id}")
            sucesso = queries.atualizar_peca(self.peca_id, novos_dados)
            acao_navegacao = lambda: self.page.go("/gerir_pecas")
            if sucesso:
                self._view.mostrar_dialogo_feedback("Sucesso!", "Peça atualizada com sucesso!", acao_navegacao)
            else:
                self._view.mostrar_dialogo_feedback("Atenção", "Nenhuma alteração foi salva.")
        except sqlite3.IntegrityError:
            self._view.mostrar_dialogo_feedback("Peça Duplicada", "Já existe outra peça com este Nome e Referência.")
        except Exception as e:
            logger.error(f"Erro crítico ao salvar alterações da peça: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback("Erro Crítico", f"Não foi possível salvar as alterações.\nErro: {e}")