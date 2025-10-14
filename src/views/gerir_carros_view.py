# =================================================================================
# MÓDULO DA VIEW DE GERENCIAMENTO DE CARROS (gerir_carros_view.py)
#
# OBJETIVO: Criar a tela para listar, buscar, ativar e desativar carros.
# PADRÃO: Segue o mesmo padrão de UI e interação do GerirClientesView.
# =================================================================================
import flet as ft
from src.viewmodels.gerir_carros_viewmodel import GerirCarrosViewModel
from typing import List
from src.styles.style import AppDimensions, AppFonts
import logging

# Configura o logger para este módulo.
logger = logging.getLogger(__name__)


class GerirCarrosView(ft.Column):
    """
    A View para a tela de gerenciamento de carros.
    """

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = GerirCarrosViewModel(page)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount

        # --- Componentes Visuais ---
        self._campo_pesquisa = ft.TextField(
            label="Pesquisar por Modelo, Placa ou Proprietário",
            on_submit=lambda e: self.view_model.pesquisar_carro(
                self._campo_pesquisa.value),
            prefix_icon=ft.Icons.SEARCH,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS)
        )
        self._resultados_pesquisa_listview = ft.ListView(
            expand=True, spacing=10)

        # Diálogo de Confirmação genérico, será adicionado à overlay.
        self._confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Ação"),
            content=ft.Text(),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_dialogo),
                # Ação e texto serão definidos dinamicamente
                ft.ElevatedButton("Confirmar")
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.controls = [
            self._campo_pesquisa,
            ft.Divider(),
            self._resultados_pesquisa_listview,
        ]
        logger.debug("GerirCarrosView inicializada.")

    def did_mount(self):
        """Método chamado pelo Flet quando a view é montada na página."""
        logger.info("GerirCarrosView foi montada. Carregando carros...")
        self.view_model.carregar_carros_iniciais()

    def atualizar_lista_resultados(self, carros: List[dict]):
        """Atualiza a ListView com os resultados da busca."""
        logger.debug(f"View: Atualizando a lista com {len(carros)} carros.")
        self._resultados_pesquisa_listview.controls.clear()

        if not carros:
            self._resultados_pesquisa_listview.controls.append(
                ft.Text("Nenhum carro encontrado."))
        else:
            for carro in carros:
                # Lógica para exibir o ícone de ativar ou desativar
                if not carro['ativo']:
                    action_icon = ft.IconButton(
                        icon=ft.Icons.RESTORE_FROM_TRASH_OUTLINED,  # Ícone para reativar
                        tooltip="Reativar Carro",
                        on_click=lambda e, c=carro: self.view_model.solicitar_ativacao(
                            c['id'], f"{c['modelo']} - {c['placa']}"),
                        icon_color=ft.Colors.GREEN_400,
                    )
                else:
                    action_icon = ft.IconButton(
                        # Usando o ícone de deletar para desativar
                        icon=ft.Icons.DELETE_FOREVER_OUTLINED,
                        tooltip="Desativar Carro",
                        on_click=lambda e, c=carro: self.view_model.solicitar_desativacao(
                            c['id'], f"{c['modelo']} - {c['placa']}"),
                        icon_color=ft.Colors.RED_400,
                    )

                list_item = ft.Container(
                    on_click=lambda _, c=carro: self.view_model.editar_carro(
                        c['id']),
                    border_radius=ft.border_radius.all(
                        AppDimensions.BORDER_RADIUS),
                    ink=True,
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    # Diferenciação visual para inativos
                    opacity=1.0 if carro['ativo'] else 0.5,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                expand=True, spacing=2,
                                controls=[
                                    ft.Text(
                                        f"{carro['modelo']} - {carro['placa']}", size=AppFonts.BODY_LARGE),
                                    ft.Text(
                                        f"Proprietário: {carro['nome_cliente']}", size=AppFonts.BODY_SMALL, color=ft.Colors.ON_SURFACE_VARIANT),
                                ]
                            ),
                            ft.Row(spacing=0, controls=[
                                   action_icon, ft.Icon(ft.Icons.CHEVRON_RIGHT)])
                        ]
                    )
                )
                self._resultados_pesquisa_listview.controls.append(list_item)
        self.update()

    # --- Métodos de Gerenciamento de Diálogos ---

    def mostrar_dialogo_confirmacao(self, carro_info: str, is_activating: bool):
        """Exibe um diálogo para confirmar a ação, usando a overlay."""
        logger.info(
            f"View: Exibindo diálogo de confirmação para {'ATIVAÇÃO' if is_activating else 'DESATIVAÇÃO'} do carro '{carro_info}'.")
        if self._confirm_dialog not in self.page.overlay:
            self.page.overlay.append(self._confirm_dialog)

        if is_activating:
            self._confirm_dialog.content.value = f"Tem certeza de que deseja reativar o carro '{carro_info}'?"
            self._confirm_dialog.actions[1].text = "Sim, Reativar"
            self._confirm_dialog.actions[1].on_click = lambda _: self.view_model.confirmar_ativacao(
            )
            self._confirm_dialog.actions[1].bgcolor = ft.Colors.GREEN_700
        else:
            self._confirm_dialog.content.value = f"Tem certeza de que deseja desativar o carro '{carro_info}'?"
            self._confirm_dialog.actions[1].text = "Sim, Desativar"
            self._confirm_dialog.actions[1].on_click = lambda _: self.view_model.confirmar_desativacao(
            )
            self._confirm_dialog.actions[1].bgcolor = self.page.theme.color_scheme.error

        self._confirm_dialog.open = True
        self.page.update()

    def fechar_dialogo(self, e=None):
        """Fecha o diálogo de confirmação."""
        logger.debug("View: Fechando diálogo de confirmação.")
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


def GerirCarrosViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa para a rota /gerir_carros."""
    view_content = GerirCarrosView(page)

    return ft.View(
        route="/gerir_carros",
        appbar=ft.AppBar(
            title=ft.Text("Gerenciar Veículos"), center_title=True,
            leading=None, automatically_imply_leading=False,
            bgcolor=page.theme.color_scheme.surface,
        ),
        floating_action_button=ft.Row(
            [
                ft.FloatingActionButton(
                    icon=ft.Icons.ARROW_BACK, tooltip="Voltar ao Dashboard", on_click=lambda _: page.go("/dashboard")),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD, tooltip="Cadastrar Novo Veículo", on_click=lambda _: page.go("/cadastro_carro"))
            ],
            alignment=ft.MainAxisAlignment.END,
        ),
        controls=[
            ft.SafeArea(
                content=ft.Container(content=view_content,
                                     padding=AppDimensions.PAGE_PADDING),
                expand=True
            )
        ],
        padding=0
    )
