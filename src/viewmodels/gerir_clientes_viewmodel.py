
# =================================================================================
# MÓDULO DO VIEWMODEL DE GERENCIAMENTO DE CLIENTES (gerir_clientes_viewmodel.py)
# =================================================================================
import flet as ft
import logging
from src.database import queries

class GerirClientesViewModel:
    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'GerirClientesView' | None = None

    def vincular_view(self, view: 'GerirClientesView'):
        self._view = view

    def carregar_clientes_iniciais(self):
        """Busca todos os clientes ativos para exibir inicialmente."""
        self.pesquisar_cliente("") # Pesquisar com termo vazio para listar todos.

    def pesquisar_cliente(self, termo: str):
        """Busca clientes e comanda a View para exibir os resultados."""
        logging.info(f"ViewModel: pesquisando por '{termo}'")
        clientes_encontrados = queries.obter_clientes_por_termo(termo)
        if self._view:
            self._view.atualizar_lista_resultados(clientes_encontrados)

    def editar_cliente(self, cliente_id: int):
        """Navega para a tela de edição do cliente selecionado."""
        logging.info(f"ViewModel: navegando para editar o cliente ID {cliente_id}")
        self.page.go(f"/editar_cliente/{cliente_id}")