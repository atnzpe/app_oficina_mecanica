# =================================================================================
# MÓDULO DO VIEWMODEL DE GERENCIAMENTO DE MECÂNICOS (gerir_mecanicos_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de gerenciamento de mecânicos.
# =================================================================================
import flet as ft
import logging
from src.database import queries

logger = logging.getLogger(__name__)


class GerirMecanicosViewModel:
    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'GerirMecanicosView' | None = None
        self._mecanico_para_acao_id: int | None = None
        logger.debug("GerirMecanicosViewModel inicializado.")

    def vincular_view(self, view: 'GerirMecanicosView'):
        self._view = view
        logger.debug("GerirMecanicosViewModel vinculado à sua View.")

    def carregar_mecanicos_iniciais(self):
        logger.info(
            "ViewModel: Carregando lista inicial de todos os mecânicos.")
        self.pesquisar_mecanico("")

    def pesquisar_mecanico(self, termo: str):
        if not self._view:
            return
        logger.info(
            f"ViewModel: pesquisando por mecânicos com o termo '{termo}'")
        mecanicos_encontrados = queries.buscar_mecanicos_por_termo(termo)
        self._view.atualizar_lista_resultados(mecanicos_encontrados)

    def editar_mecanico(self, mecanico_id: int):
        logger.info(
            f"ViewModel: Navegando para a tela de edição do mecânico ID {mecanico_id}")
        self.page.go(f"/editar_mecanico/{mecanico_id}")

    def solicitar_desativacao(self, mecanico_id: int, mecanico_nome: str):
        self._mecanico_para_acao_id = mecanico_id
        logger.info(
            f"ViewModel: Solicitação para desativar o mecânico ID {mecanico_id} ('{mecanico_nome}').")
        if self._view:
            self._view.mostrar_dialogo_confirmacao(
                mecanico_nome, is_activating=False)

    def confirmar_desativacao(self):
        if self._mecanico_para_acao_id is None:
            return
        try:
            sucesso = queries.desativar_mecanico_por_id(
                self._mecanico_para_acao_id)
            if self._view:
                self._view.fechar_dialogo()
                if sucesso:
                    self._view.mostrar_feedback(
                        "Mecânico desativado com sucesso!", True)
                    self.carregar_mecanicos_iniciais()
                else:
                    self._view.mostrar_feedback(
                        "Erro ao desativar o mecânico.", False)
        finally:
            self._mecanico_para_acao_id = None

    def solicitar_ativacao(self, mecanico_id: int, mecanico_nome: str):
        self._mecanico_para_acao_id = mecanico_id
        logger.info(
            f"ViewModel: Solicitação para ATIVAR o mecânico ID {mecanico_id} ('{mecanico_nome}').")
        if self._view:
            self._view.mostrar_dialogo_confirmacao(
                mecanico_nome, is_activating=True)

    def confirmar_ativacao(self):
        if self._mecanico_para_acao_id is None:
            return
        try:
            sucesso = queries.ativar_mecanico_por_id(
                self._mecanico_para_acao_id)
            if self._view:
                self._view.fechar_dialogo()
                if sucesso:
                    self._view.mostrar_feedback(
                        "Mecânico reativado com sucesso!", True)
                    self.carregar_mecanicos_iniciais()
                else:
                    self._view.mostrar_feedback(
                        "Erro ao reativar o mecânico.", False)
        finally:
            self._mecanico_para_acao_id = None
