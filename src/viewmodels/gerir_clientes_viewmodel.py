# =================================================================================
# MÓDULO DO VIEWMODEL DE GERENCIAMENTO DE CLIENTES (gerir_clientes_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de gerenciamento de clientes.
# ATUALIZAÇÃO (CORREÇÃO):
#   - Adicionada a lógica para solicitar e confirmar a REATIVAÇÃO de um cliente.
#   - Corrigido o TypeError ao chamar `mostrar_dialogo_confirmacao` passando o
#     argumento `is_activating` que estava faltando.
# =================================================================================
import flet as ft
import logging
from src.database import queries

# Configura o logger para este módulo.
logger = logging.getLogger(__name__)


class GerirClientesViewModel:
    """
    O ViewModel para a GerirClientesView. Lida com a busca de clientes e
    comanda a navegação para as telas de edição e cadastro.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'GerirClientesView' | None = None
        # Armazena o ID do cliente sendo manipulado para qualquer ação (ativar/desativar).
        self._cliente_para_acao_id: int | None = None

    def vincular_view(self, view: 'GerirClientesView'):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view

    def carregar_clientes_iniciais(self):
        """Busca todos os clientes (ativos e inativos) para exibir na tela."""
        logger.info("ViewModel: Carregando lista inicial de todos os clientes.")
        self.pesquisar_cliente("")

    def pesquisar_cliente(self, termo: str):
        """Busca clientes no banco e comanda a View para exibir os resultados."""
        logger.info(
            f"ViewModel: pesquisando por clientes com o termo '{termo}'")
        clientes_encontrados = queries.buscar_clientes_por_termo(termo)
        if self._view:
            self._view.atualizar_lista_resultados(clientes_encontrados)

    def editar_cliente(self, cliente_id: int):
        """Navega para a tela de edição do cliente selecionado."""
        logger.info(
            f"ViewModel: navegando para a tela de edição do cliente ID {cliente_id}")
        self.page.go(f"/editar_cliente/{cliente_id}")

    # --- LÓGICA DE DESATIVAÇÃO (CORRIGIDA) ---

    def solicitar_desativacao(self, cliente_id: int, cliente_nome: str):
        """Armazena o ID do cliente e comanda a View para abrir o diálogo de confirmação."""
        self._cliente_para_acao_id = cliente_id
        logger.info(
            f"ViewModel: Solicitação para desativar o cliente ID {cliente_id} ('{cliente_nome}').")
        if self._view:
            # CORREÇÃO: Passando o argumento 'is_activating=False' para a view.
            self._view.mostrar_dialogo_confirmacao(
                cliente_nome, is_activating=False)

    def confirmar_desativacao(self):
        """Confirma a desativação do cliente e atualiza a UI."""
        if self._cliente_para_acao_id is None:
            return

        logger.info(
            f"ViewModel: Confirmando desativação para o cliente ID {self._cliente_para_acao_id}.")
        try:
            sucesso = queries.desativar_cliente_por_id(
                self._cliente_para_acao_id)
            if self._view:
                self._view.fechar_dialogo()
                if sucesso:
                    self._view.mostrar_feedback(
                        "Cliente desativado com sucesso!", True)
                    # Recarrega a lista para mostrar o status atualizado
                    self.carregar_clientes_iniciais()
                else:
                    self._view.mostrar_feedback(
                        "Erro ao desativar o cliente.", False)
        except Exception as e:
            logger.error(
                f"ViewModel: Erro inesperado ao desativar cliente: {e}", exc_info=True)
            if self._view:
                self._view.fechar_dialogo()
                self._view.mostrar_feedback(f"Falha crítica: {e}", False)
        finally:
            self._cliente_para_acao_id = None

    # --- LÓGICA DE ATIVAÇÃO (ADICIONADA) ---

    def solicitar_ativacao(self, cliente_id: int, cliente_nome: str):
        """
        Armazena o ID do cliente e comanda a View para abrir o diálogo de confirmação de ativação.
        """
        self._cliente_para_acao_id = cliente_id
        logger.info(
            f"ViewModel: Solicitação para ATIVAR o cliente ID {cliente_id} ('{cliente_nome}').")
        if self._view:
            # Passando o argumento 'is_activating=True' para a view.
            self._view.mostrar_dialogo_confirmacao(
                cliente_nome, is_activating=True)

    def confirmar_ativacao(self):
        """
        Confirma a ativação do cliente e atualiza a UI.
        """
        if self._cliente_para_acao_id is None:
            return

        logger.info(
            f"ViewModel: Confirmando ATIVAÇÃO para o cliente ID {self._cliente_para_acao_id}.")
        try:
            sucesso = queries.ativar_cliente_por_id(self._cliente_para_acao_id)
            if self._view:
                self._view.fechar_dialogo()
                if sucesso:
                    self._view.mostrar_feedback(
                        "Cliente reativado com sucesso!", True)
                    # Recarrega a lista para mostrar o status atualizado
                    self.carregar_clientes_iniciais()
                else:
                    self._view.mostrar_feedback(
                        "Erro ao reativar o cliente.", False)
        except Exception as e:
            logger.error(
                f"ViewModel: Erro inesperado ao ativar cliente: {e}", exc_info=True)
            if self._view:
                self._view.fechar_dialogo()
                self._view.mostrar_feedback(
                    f"Falha crítica ao reativar: {e}", False)
        finally:
            self._cliente_para_acao_id = None
