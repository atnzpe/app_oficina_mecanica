# =================================================================================
# MÓDULO DO VIEWMODEL DE GERENCIAMENTO DE CLIENTES (gerir_clientes_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de gerenciamento de clientes,
#           incluindo busca e navegação para outras telas do CRUD.
# ATUALIZAÇÃO:
#   - Adicionados métodos para lidar com a desativação (exclusão lógica) de
#     clientes diretamente da tela de listagem, incluindo a confirmação.
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
        # Armazena a referência da página principal do Flet.
        self.page = page
        # Referência fraca à View, que será vinculada pelo método vincular_view.
        self._view: 'GerirClientesView' | None = None
        # Armazena o ID do cliente que está prestes a ser desativado.
        self._cliente_para_desativar_id: int | None = None

    def vincular_view(self, view: 'GerirClientesView'):
        """
        Estabelece a conexão de duas vias entre o ViewModel e a View.
        """
        self._view = view

    def carregar_clientes_iniciais(self):
        """
        Busca todos os clientes ativos para exibir inicialmente na tela.
        """
        # Log de início da operação.
        logger.info("ViewModel: Carregando lista inicial de clientes.")
        # Chama o método de pesquisa com um termo vazio para listar todos os clientes.
        self.pesquisar_cliente("")

    def pesquisar_cliente(self, termo: str):
        """
        Busca clientes no banco de dados com base em um termo e comanda a
        View para exibir os resultados.
        """
        logger.info(
            f"ViewModel: pesquisando por clientes com o termo '{termo}'")
        # 1. INTERAÇÃO COM A CAMADA DE DADOS (QUERIES).
        clientes_encontrados = queries.buscar_clientes_por_termo(termo)

        # 2. COMANDA A VIEW: Se a view estiver vinculada, comanda a atualização da lista.
        if self._view:
            self._view.atualizar_lista_resultados(clientes_encontrados)

    def editar_cliente(self, cliente_id: int):
        """
        Navega para a tela de edição do cliente selecionado.

        :param cliente_id: O ID do cliente a ser editado.
        """
        logger.info(
            f"ViewModel: navegando para a tela de edição do cliente ID {cliente_id}")
        # 3. NAVEGAÇÃO: Comanda a página para ir para a rota de edição, passando o ID do cliente.
        self.page.go(f"/editar_cliente/{cliente_id}")

    # --- NOVOS MÉTODOS ---

    def solicitar_desativacao(self, cliente_id: int, cliente_nome: str):
        """
        Armazena o ID do cliente e comanda a View para abrir o diálogo de confirmação.

        :param cliente_id: O ID do cliente a ser desativado.
        :param cliente_nome: O nome do cliente para exibição no diálogo.
        """
        # Armazena o ID do cliente que o usuário deseja desativar.
        self._cliente_para_desativar_id = cliente_id
        logger.info(
            f"ViewModel: Solicitação para desativar o cliente ID {cliente_id} ('{cliente_nome}').")
        # Comanda a View para exibir o modal de confirmação.
        if self._view:
            logger.info(
            f"Exibe a view desativar o cliente ID {cliente_id} ('{cliente_nome}').")
            self._view.mostrar_dialogo_confirmacao(cliente_nome)

    def confirmar_desativacao(self):
        """
        Confirma a desativação do cliente, interage com a camada de dados
        e atualiza a UI.
        """
        # Verifica se há um cliente selecionado para desativação.
        if self._cliente_para_desativar_id is None:
            logger.warning(
                "ViewModel: Tentativa de confirmar desativação sem um cliente ID selecionado.")
            return

        logger.info(
            f"ViewModel: Confirmando desativação para o cliente ID {self._cliente_para_desativar_id}.")
        try:
            # 1. INTERAÇÃO COM A CAMADA DE DADOS: Chama a query para desativar o cliente.
            sucesso = queries.desativar_cliente_por_id(
                self._cliente_para_desativar_id)

            # 2. COMANDA A VIEW: Fecha o diálogo e exibe feedback.
            if self._view:
                self._view.fechar_dialogo()
                if sucesso:
                    self._view.mostrar_feedback(
                        "Cliente desativado com sucesso!", True)
                    # Recarrega a lista de clientes para refletir a remoção.
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
            # Limpa o ID do cliente para desativar, independentemente do resultado.
            self._cliente_para_desativar_id = None
