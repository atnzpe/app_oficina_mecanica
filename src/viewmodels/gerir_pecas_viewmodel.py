# =================================================================================
# MÓDULO DO VIEWMODEL DE GERENCIAMENTO DE PEÇAS (gerir_pecas_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de gerenciamento de peças,
#           incluindo busca, ativação, desativação e navegação.
# =================================================================================
import flet as ft
import logging
from src.database import queries

# Configura o logger para este módulo.
logger = logging.getLogger(__name__)


class GerirPecasViewModel:
    """
    O ViewModel para a GerirPecasView.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'GerirPecasView' | None = None
        self._peca_para_acao_id: int | None = None
        logger.debug("GerirPecasViewModel inicializado.")

    def vincular_view(self, view: 'GerirPecasView'):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view
        logger.debug("GerirPecasViewModel vinculado à sua View.")

    def carregar_pecas_iniciais(self):
        """Busca todas as peças para exibir inicialmente na tela."""
        logger.info("ViewModel: Carregando lista inicial de todas as peças.")
        self.pesquisar_peca("")

    def pesquisar_peca(self, termo: str):
        """Busca peças no banco e comanda a View para exibir os resultados."""
        if not self._view:
            return
        logger.info(f"ViewModel: pesquisando por peças com o termo '{termo}'")
        pecas_encontradas = queries.buscar_pecas_por_termo(termo)
        self._view.atualizar_lista_resultados(pecas_encontradas)

    def editar_peca(self, peca_id: int):
        """Navega para a tela de edição da peça selecionada."""
        logger.info(
            f"ViewModel: Navegando para a tela de edição da peça ID {peca_id}")
        self.page.go(f"/editar_peca/{peca_id}")

    def solicitar_desativacao(self, peca_id: int, peca_info: str):
        """Comanda a View para abrir o diálogo de confirmação de desativação."""
        self._peca_para_acao_id = peca_id
        logger.info(
            f"ViewModel: Solicitação para desativar a peça ID {peca_id} ('{peca_info}').")
        if self._view:
            self._view.mostrar_dialogo_confirmacao(
                peca_info, is_activating=False)

    def confirmar_desativacao(self):
        """Confirma a desativação da peça e atualiza a UI."""
        if self._peca_para_acao_id is None:
            return
        logger.info(
            f"ViewModel: Confirmando desativação para a peça ID {self._peca_para_acao_id}.")
        try:
            sucesso = queries.desativar_peca_por_id(self._peca_para_acao_id)
            if self._view:
                self._view.fechar_dialogo()
                if sucesso:
                    self._view.mostrar_feedback(
                        "Peça desativada com sucesso!", True)
                    self.carregar_pecas_iniciais()
                else:
                    self._view.mostrar_feedback(
                        "Erro ao desativar a peça.", False)
        finally:
            self._peca_para_acao_id = None

    def solicitar_ativacao(self, peca_id: int, peca_info: str):
        """Comanda a View para abrir o diálogo de confirmação de ativação."""
        self._peca_para_acao_id = peca_id
        logger.info(
            f"ViewModel: Solicitação para ATIVAR a peça ID {peca_id} ('{peca_info}').")
        if self._view:
            self._view.mostrar_dialogo_confirmacao(
                peca_info, is_activating=True)

    def confirmar_ativacao(self):
        """Confirma a ativação da peça e atualiza a UI."""
        if self._peca_para_acao_id is None:
            return
        logger.info(
            f"ViewModel: Confirmando ATIVAÇÃO para a peça ID {self._peca_para_acao_id}.")
        try:
            sucesso = queries.ativar_peca_por_id(self._peca_para_acao_id)
            if self._view:
                self._view.fechar_dialogo()
                if sucesso:
                    self._view.mostrar_feedback(
                        "Peça reativada com sucesso!", True)
                    self.carregar_pecas_iniciais()
                else:
                    self._view.mostrar_feedback(
                        "Erro ao reativar a peça.", False)
        finally:
            self._peca_para_acao_id = None
