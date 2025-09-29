# =================================================================================
# MÓDULO DO VIEWMODEL DE GERENCIAMENTO DE CLIENTES (gerir_clientes_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de gerenciamento de clientes,
#           incluindo busca e navegação para outras telas do CRUD.
# CORREÇÃO:
#   - Removida a importação circular que causava o `ImportError`. O arquivo
#     estava tentando importar a si mesmo, o que foi corrigido.
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

    def vincular_view(self, view: 'GerirClientesView'):
        """
        Estabelece a conexão de duas vias entre o ViewModel e a View.
        """
        self._view = view

    def carregar_clientes_iniciais(self):
        """
        Busca todos os clientes ativos para exibir inicialmente na tela.
        """
        # Chama o método de pesquisa com um termo vazio para listar todos os clientes.
        self.pesquisar_cliente("")

    def pesquisar_cliente(self, termo: str):
        """
        Busca clientes no banco de dados com base em um termo e comanda a
        View para exibir os resultados.
        """
        logger.info(f"ViewModel: pesquisando por clientes com o termo '{termo}'")
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
        logger.info(f"ViewModel: navegando para a tela de edição do cliente ID {cliente_id}")
        # 3. NAVEGAÇÃO: Comanda a página para ir para a rota de edição, passando o ID do cliente.
        self.page.go(f"/editar_cliente/{cliente_id}")
