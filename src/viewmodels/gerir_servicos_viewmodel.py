# =================================================================================
# MÓDULO DO VIEWMODEL DE GERENCIAMENTO DE SERVIÇOS (gerir_servicos_viewmodel.py)
# =================================================================================
import flet as ft
import logging
from src.database import queries

logger = logging.getLogger(__name__)

class GerirServicosViewModel:
    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'GerirServicosView' | None = None
        self._servico_para_acao_id: int | None = None
        logger.debug("GerirServicosViewModel inicializado.")

    def vincular_view(self, view: 'GerirServicosView'):
        self._view = view

    def carregar_servicos_iniciais(self):
        self.pesquisar_servico("")

    def pesquisar_servico(self, termo: str):
        if not self._view: return
        servicos_encontrados = queries.buscar_servicos_por_termo(termo)
        self._view.atualizar_lista_resultados(servicos_encontrados)

    def editar_servico(self, servico_id: int):
        self.page.go(f"/editar_servico/{servico_id}")

    def solicitar_desativacao(self, servico_id: int, servico_nome: str):
        self._servico_para_acao_id = servico_id
        if self._view:
            self._view.mostrar_dialogo_confirmacao(servico_nome, is_activating=False)

    def confirmar_desativacao(self):
        if self._servico_para_acao_id is None: return
        try:
            sucesso = queries.desativar_servico_por_id(self._servico_para_acao_id)
            if self._view:
                self._view.fechar_dialogo()
                if sucesso:
                    self._view.mostrar_feedback("Serviço desativado com sucesso!", True)
                    self.carregar_servicos_iniciais()
                else:
                    self._view.mostrar_feedback("Erro ao desativar o serviço.", False)
        finally:
            self._servico_para_acao_id = None
            
    def solicitar_ativacao(self, servico_id: int, servico_nome: str):
        self._servico_para_acao_id = servico_id
        if self._view:
            self._view.mostrar_dialogo_confirmacao(servico_nome, is_activating=True)

    def confirmar_ativacao(self):
        if self._servico_para_acao_id is None: return
        try:
            sucesso = queries.ativar_servico_por_id(self._servico_para_acao_id)
            if self._view:
                self._view.fechar_dialogo()
                if sucesso:
                    self._view.mostrar_feedback("Serviço reativado com sucesso!", True)
                    self.carregar_servicos_iniciais()
                else:
                    self._view.mostrar_feedback("Erro ao reativar o serviço.", False)
        finally:
            self._servico_para_acao_id = None
        if self._servico_para_acao_id is None: return
        try:
            sucesso = queries.ativar_servico_por_id(self._servico_para_acao_id)
            if self._view:
                self._view.fechar_dialogo()
                if sucesso:
                    self._view.mostrar_feedback("Serviço reativado com sucesso!", True)
                    self.carregar_servicos_iniciais()
                else:
                    self._view.mostrar_feedback("Erro ao reativar o serviço.", False)
        finally:
            self._servico_para_acao_id = None