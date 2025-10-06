# =================================================================================
# MÓDULO DO VIEWMODEL DE EDIÇÃO DE CLIENTE (editar_cliente_viewmodel.py)
#
# ATUALIZAÇÃO (Robustez e UX):
#   - O fluxo de navegação foi refatorado para ocorrer apenas APÓS o usuário
#     fechar o diálogo de feedback, evitando travamentos na interface.
# =================================================================================
import flet as ft
import logging
from src.database import queries
from src.models.models import Cliente

logger = logging.getLogger(__name__)


class EditarClienteViewModel:
    def __init__(self, page: ft.Page, cliente_id: int):
        self.page = page
        self.cliente_id = cliente_id
        self._view: 'EditarClienteView' | None = None
        self.cliente_em_edicao: Cliente | None = None

    def vincular_view(self, view: 'EditarClienteView'):
        self._view = view

    def carregar_dados_cliente(self):
        """Busca os dados do cliente e comanda a View para preencher o formulário."""
        try:
            logging.info(
                f"ViewModel: buscando dados para o cliente ID {self.cliente_id}")
            cliente = queries.obter_cliente_por_id(self.cliente_id)
            if cliente and self._view:
                self.cliente_em_edicao = cliente
                self._view.preencher_formulario(cliente)
            elif self._view:
                # Se o cliente não for encontrado, mostra um feedback e navega de volta.
                def acao_navegacao(): return self.page.go("/gerir_clientes")
                self._view.mostrar_dialogo_feedback(
                    "Erro", "Cliente não encontrado.", acao_navegacao)
        except Exception as e:
            logging.error(
                f"Erro ao carregar dados do cliente: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Não foi possível carregar os dados do cliente.\nErro: {e}", None)

    def salvar_alteracoes(self, novos_dados: dict):
        """Salva as alterações e comanda a exibição de um diálogo de feedback."""
        try:
            logging.info(
                f"ViewModel: salvando alterações para o cliente ID {self.cliente_id}")
            sucesso = queries.atualizar_cliente(self.cliente_id, novos_dados)
            if self._view:
                # Define a ação de navegação que será executada após o diálogo.
                def acao_navegacao(): return self.page.go("/gerir_clientes")
                if sucesso:
                    self._view.mostrar_dialogo_feedback(
                        "Sucesso!", "Cliente atualizado com sucesso!", acao_navegacao)
                else:
                    self._view.mostrar_dialogo_feedback(
                        "Atenção", "Nenhuma alteração foi salva. Os dados podem ser os mesmos.", None)
        except Exception as e:
            logging.error(
                f"Erro ao salvar alterações do cliente: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Não foi possível salvar as alterações.\nErro: {e}", None)

    def solicitar_desativacao_cliente(self):
        if self._view:
            self._view.abrir_modal_confirmacao_desativar()

    def confirmar_desativacao_cliente(self, e):
        """Desativa o cliente e comanda a exibição de um diálogo de feedback."""
        try:
            logging.info(
                f"ViewModel: Confirmado! Desativando cliente ID: {self.cliente_id}")
            sucesso = queries.desativar_cliente_por_id(self.cliente_id)
            if self._view:
                self._view.fechar_todos_os_modais()
                def acao_navegacao(): return self.page.go("/gerir_clientes")
                if sucesso:
                    self._view.mostrar_dialogo_feedback(
                        "Sucesso!", "Cliente desativado com sucesso!", acao_navegacao)
                else:
                    self._view.mostrar_dialogo_feedback(
                        "Erro", "Erro ao desativar o cliente.", None)
        except Exception as e:
            logging.error(
                f"Erro ao confirmar desativação do cliente: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Não foi possível desativar o cliente.\nErro: {e}", None)

    def solicitar_ativacao_cliente(self):
        if self._view:
            self._view.abrir_modal_confirmacao_ativar()

    def confirmar_ativacao_cliente(self, e):
        """ATIVA o cliente e comanda a exibição de um diálogo de feedback."""
        try:
            logging.info(
                f"ViewModel: Confirmado! ATIVANDO cliente ID: {self.cliente_id}")
            sucesso = queries.ativar_cliente_por_id(self.cliente_id)
            if self._view:
                self._view.fechar_todos_os_modais()
                def acao_navegacao(): return self.page.go("/gerir_clientes")
                if sucesso:
                    self._view.mostrar_dialogo_feedback(
                        "Sucesso!", "Cliente ativado com sucesso!", acao_navegacao)
                else:
                    self._view.mostrar_dialogo_feedback(
                        "Erro", "Erro ao ativar o cliente.", None)
        except Exception as e:
            logging.error(
                f"Erro ao confirmar ativação do cliente: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Não foi possível ativar o cliente.\nErro: {e}", None)
