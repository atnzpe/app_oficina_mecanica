# =================================================================================
# MÓDULO DO VIEWMODEL DE CADASTRO DE PEÇA (cadastro_peca_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de cadastro de peças,
#           incluindo validação de formulário e interação com a camada de dados.
# =================================================================================
import flet as ft
import logging
import sqlite3
from src.database import queries
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class CadastroPecaViewModel:
    """
    O ViewModel para a CadastroPecaView.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'CadastroPecaView' | None = None
        logger.debug("CadastroPecaViewModel inicializado.")

    def vincular_view(self, view: 'CadastroPecaView'):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view
        logger.debug("ViewModel de Cadastro de Peça vinculado à sua View.")

    def salvar_peca(self):
        """Pega dados da View, valida, e comanda a criação da nova peça."""
        if not self._view:
            logger.error(
                "ViewModel: Ação 'salvar_peca' chamada sem uma View vinculada.")
            return

        try:
            dados = self._view.obter_dados_formulario()

            # --- LÓGICA DE VALIDAÇÃO ---
            if not dados['nome'] or not dados['referencia']:
                self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "Os campos 'Nome' e 'Referência' são obrigatórios.")
                return
            if dados['preco_compra'] is None or dados['preco_venda'] is None or dados['quantidade_em_estoque'] is None:
                self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "Preço de Compra, Preço de Venda e Quantidade devem ser números válidos.")
                return
            if dados['quantidade_em_estoque'] < 0:
                self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "A quantidade em estoque não pode ser negativa.")
                return

            # --- INTERAÇÃO COM A CAMADA DE DADOS ---
            logger.info(
                f"ViewModel: Tentando salvar a nova peça '{dados['nome']}'.")
            nova_peca = queries.criar_peca(dados)

            if nova_peca:
                logger.info(f"Peça '{dados['nome']}' cadastrada com sucesso.")
                def acao_navegacao(): return self.page.go("/gerir_pecas")
                self._view.mostrar_dialogo_feedback(
                    "Sucesso!", "Peça cadastrada com sucesso!", acao_navegacao)

        except sqlite3.IntegrityError:
            logger.warning(
                f"Tentativa de cadastrar peça duplicada: {dados.get('nome')} / {dados.get('referencia')}")
            self._view.mostrar_dialogo_feedback(
                "Peça Duplicada", "Já existe uma peça cadastrada com este Nome e Referência.")
        except Exception as e:
            logger.error(f"Erro inesperado ao salvar peça: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Ocorreu uma falha inesperada:\n{e}")

    def cancelar_cadastro(self, e):
        """Navega de volta para a lista de peças."""
        logger.info(
            "Cadastro de peça cancelado. Redirecionando para /gerir_pecas.")
        self.page.go("/gerir_pecas")
