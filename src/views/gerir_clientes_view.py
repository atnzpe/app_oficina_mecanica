
# =================================================================================
# MÓDULO DA VIEW DE GERENCIAMENTO DE CLIENTES (gerir_clientes_view.py)
#
# OBJETIVO: Criar a tela para listar e buscar clientes (funcionalidade READ).
# =================================================================================
import flet as ft
from src.viewmodels.gerir_clientes_viewmodel import GerirClientesViewModel
from src.models.models import Cliente
from typing import List

class GerirClientesView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = GerirClientesViewModel(page)
        self.view_model.vincular_view(self)

        self._campo_pesquisa = ft.TextField(
            label="Pesquisar por Nome, Telefone ou Placa",
            on_submit=lambda e: self.view_model.pesquisar_cliente(self._campo_pesquisa.value),
            prefix_icon=ft.Icons.SEARCH,
        )
        self._resultados_pesquisa_listview = ft.ListView(expand=True, spacing=10)

        self.controls = [
            self._campo_pesquisa,
            ft.Divider(),
            self._resultados_pesquisa_listview,
        ]
        
        # Carrega a lista inicial de clientes ao abrir a tela.
        self.view_model.carregar_clientes_iniciais()

    def atualizar_lista_resultados(self, clientes: List[Cliente]):
        """Atualiza a ListView com os resultados da busca."""
        self._resultados_pesquisa_listview.controls.clear()
        if not clientes:
            self._resultados_pesquisa_listview.controls.append(ft.Text("Nenhum cliente encontrado."))
        else:
            for cliente in clientes:
                self._resultados_pesquisa_listview.controls.append(
                    ft.ListTile(
                        title=ft.Text(cliente.nome),
                        subtitle=ft.Text(f"Telefone: {cliente.telefone}"),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                        on_click=lambda _, c=cliente: self.view_model.editar_cliente(c.id),
                    )
                )
        self.update()

def GerirClientesViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa para a rota /gerir_clientes."""
    view_content = GerirClientesView(page)
    return ft.View(
        route="/gerir_clientes",
        appbar=ft.AppBar(
            title=ft.Text("Gerenciar Clientes"),
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard")),
        ),
        controls=[
            # --- SAFEAREA APLICADO ---
            ft.SafeArea(
                content=view_content,
                expand=True
            )
        ],
        padding=0
    )