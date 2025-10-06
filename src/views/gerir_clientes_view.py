# =================================================================================
# MÓDULO DA VIEW DE GERENCIAMENTO DE CLIENTES (gerir_clientes_view.py)
#
# OBJETIVO: Criar a tela para listar e buscar clientes (funcionalidade READ).
# ATUALIZAÇÃO (UX):
#   - A lista agora exibe clientes ativos e inativos.
#   - Clientes inativos são visualmente diferenciados (opacidade reduzida).
#   - Adicionado um botão de "reativar" (PERSON_ADD) para clientes inativos.
# =================================================================================
import flet as ft
from src.viewmodels.gerir_clientes_viewmodel import GerirClientesViewModel
from src.models.models import Cliente
from typing import List
# Importa as classes de estilo para fontes e dimensões.
from src.styles.style import AppDimensions, AppFonts
import logging


class GerirClientesView(ft.Column):
    """
    A View para a tela de gerenciamento de clientes, responsável por exibir
    a lista de clientes e permitir a busca.
    """

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = GerirClientesViewModel(page)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount

        self._campo_pesquisa = ft.TextField(
            label="Pesquisar por Nome, Telefone ou Placa do Carro",
            on_submit=lambda e: self.view_model.pesquisar_cliente(
                self._campo_pesquisa.value),
            prefix_icon=ft.Icons.SEARCH,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS)
        )
        self._resultados_pesquisa_listview = ft.ListView(
            expand=True, spacing=10)

        # Diálogo de Confirmação genérico.
        self._confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Ação"),
            content=ft.Text(),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_dialogo),
                ft.ElevatedButton("Confirmar") # Ação e texto serão definidos dinamicamente
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.controls = [
            self._campo_pesquisa,
            ft.Divider(),
            self._resultados_pesquisa_listview,
        ]

    def did_mount(self):
        """Método chamado pelo Flet quando a view é montada na página."""
        logging.info("GerirClientesView foi montada. Carregando clientes...")
        self.view_model.carregar_clientes_iniciais()

    def atualizar_lista_resultados(self, clientes: List[Cliente]):
        """Atualiza a ListView com os resultados da busca fornecidos pelo ViewModel."""
        self._resultados_pesquisa_listview.controls.clear()

        if not clientes:
            self._resultados_pesquisa_listview.controls.append(
                ft.Text("Nenhum cliente encontrado."))
        else:
            for cliente in clientes:
                # --- LÓGICA DE EXIBIÇÃO CONDICIONAL ---
                
                # Se o cliente estiver inativo, o ícone de ação será para reativar.
                if not cliente.ativo:
                    action_icon = ft.IconButton(
                        icon=ft.Icons.PERSON_ADD,
                        tooltip="Reativar Cliente",
                        on_click=lambda e, c=cliente: self.view_model.solicitar_ativacao(c.id, c.nome),
                        icon_color=ft.Colors.GREEN_400,
                    )
                # Se estiver ativo, o ícone será para desativar.
                else:
                    action_icon = ft.IconButton(
                        icon=ft.Icons.PERSON_OFF,
                        tooltip="Desativar Cliente",
                        on_click=lambda e, c=cliente: self.view_model.solicitar_desativacao(c.id, c.nome),
                        icon_color=ft.Colors.RED_400,
                    )

                list_item = ft.Container(
                    on_click=lambda _, c=cliente: self.view_model.editar_cliente(c.id),
                    border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
                    ink=True,
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    # Clientes inativos terão uma opacidade menor para diferenciação visual.
                    opacity=1.0 if cliente.ativo else 0.5,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                expand=True,
                                spacing=2,
                                controls=[
                                    ft.Text(cliente.nome, size=AppFonts.BODY_LARGE),
                                    ft.Text(f"Telefone: {cliente.telefone}", size=AppFonts.BODY_SMALL, color=ft.Colors.ON_SURFACE_VARIANT),
                                ]
                            ),
                            ft.Row(
                                spacing=0,
                                controls=[
                                    action_icon, # Ícone de ação (ativar/desativar)
                                    ft.Icon(ft.Icons.CHEVRON_RIGHT),
                                ]
                            )
                        ]
                    )
                )
                self._resultados_pesquisa_listview.controls.append(list_item)
        self.update()

    # --- MÉTODOS DA VIEW ---

    def mostrar_dialogo_confirmacao(self, nome_cliente: str, is_activating: bool):
        """Exibe um diálogo para confirmar a ativação ou desativação de um cliente."""
        self.page.overlay.append(self._confirm_dialog)
        
        # Personaliza o diálogo com base na ação (ativar ou desativar).
        if is_activating:
            self._confirm_dialog.content.value = f"Tem certeza de que deseja reativar o cliente '{nome_cliente}'?"
            self._confirm_dialog.actions[1].text = "Sim, Reativar"
            self._confirm_dialog.actions[1].on_click = lambda _: self.view_model.confirmar_ativacao()
            self._confirm_dialog.actions[1].bgcolor = ft.Colors.GREEN_700
        else:
            self._confirm_dialog.content.value = f"Tem certeza de que deseja desativar o cliente '{nome_cliente}'?\nEsta ação o removerá das listas ativas."
            self._confirm_dialog.actions[1].text = "Sim, Desativar"
            self._confirm_dialog.actions[1].on_click = lambda _: self.view_model.confirmar_desativacao()
            self._confirm_dialog.actions[1].bgcolor = ft.Colors.RED_700
            
        self._confirm_dialog.open = True
        self.page.update()

    def fechar_dialogo(self, e=None):
        """Fecha o diálogo de confirmação."""
        if self._confirm_dialog in self.page.overlay:
            self._confirm_dialog.open = False
            self.page.update()

    def mostrar_feedback(self, mensagem: str, sucesso: bool):
        """Exibe uma SnackBar para feedback ao usuário."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=self.page.theme.color_scheme.primary if sucesso else self.page.theme.color_scheme.error
        )
        self.page.snack_bar.open = True
        self.page.update()


def GerirClientesViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa para a rota /gerir_clientes."""
    view_content = GerirClientesView(page)

    return ft.View(
        route="/gerir_clientes",
        appbar=ft.AppBar(
            title=ft.Text("Gerenciar Clientes"),
            center_title=True,
            leading=None,
            automatically_imply_leading=False,
            bgcolor=page.theme.color_scheme.surface,
        ),
        floating_action_button=ft.Row(
            [
                ft.FloatingActionButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Voltar ao Dashboard",
                    on_click=lambda _: page.go("/dashboard")
                ),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    tooltip="Cadastrar Novo Cliente",
                    on_click=lambda _: page.go("/cadastro_cliente")
                )
            ],
            alignment=ft.MainAxisAlignment.END,
        ),
        controls=[
            ft.SafeArea(
                content=ft.Container(
                    content=view_content,
                    padding=AppDimensions.PAGE_PADDING
                ),
                expand=True
            )
        ],
        padding=0
    )