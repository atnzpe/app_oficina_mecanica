# =================================================================================
# MÓDULO DA VIEW DE GERENCIAMENTO DE PEÇAS (gerir_pecas_view.py)
#
# OBJETIVO: Criar a tela para listar, buscar, ativar e desativar peças.
# =================================================================================
import flet as ft
from src.viewmodels.gerir_pecas_viewmodel import GerirPecasViewModel
from src.models.models import Peca
from typing import List
from src.styles.style import AppDimensions, AppFonts
import logging

logger = logging.getLogger(__name__)


class GerirPecasView(ft.Column):
    """
    A View para a tela de gerenciamento de peças.
    """

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = GerirPecasViewModel(page)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount

        self._campo_pesquisa = ft.TextField(
            label="Pesquisar por Nome, Referência ou Fabricante",
            on_submit=lambda e: self.view_model.pesquisar_peca(
                self._campo_pesquisa.value),
            prefix_icon=ft.Icons.SEARCH,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS)
        )
        self._resultados_pesquisa_listview = ft.ListView(
            expand=True, spacing=10)

        self._confirm_dialog = ft.AlertDialog(
            modal=True, title=ft.Text("Confirmar Ação"), content=ft.Text(),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_dialogo),
                ft.ElevatedButton("Confirmar")
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.controls = [self._campo_pesquisa,
                         ft.Divider(), self._resultados_pesquisa_listview]
        logger.debug("GerirPecasView inicializada.")

    def did_mount(self):
        """Chamado pelo Flet quando a view é montada."""
        logger.info("GerirPecasView foi montada. Carregando peças...")
        self.view_model.carregar_pecas_iniciais()

    def atualizar_lista_resultados(self, pecas: List[Peca]):
        """Atualiza a ListView com os resultados da busca."""
        logger.debug(f"View: Atualizando a lista com {len(pecas)} peças.")
        self._resultados_pesquisa_listview.controls.clear()

        if not pecas:
            self._resultados_pesquisa_listview.controls.append(
                ft.Text("Nenhuma peça encontrada."))
        else:
            for peca in pecas:
                action_icon = (
                    ft.IconButton(
                        icon=ft.Icons.RESTORE_FROM_TRASH, tooltip="Reativar Peça",
                        on_click=lambda e, p=peca: self.view_model.solicitar_ativacao(
                            p.id, p.nome),
                        icon_color=ft.Colors.GREEN_400,
                    ) if not peca.ativo else ft.IconButton(
                        icon=ft.Icons.DELETE_FOREVER, tooltip="Desativar Peça",
                        on_click=lambda e, p=peca: self.view_model.solicitar_desativacao(
                            p.id, p.nome),
                        icon_color=ft.Colors.RED_400,
                    )
                )

                list_item = ft.Container(
                    on_click=lambda _, p=peca: self.view_model.editar_peca(
                        p.id),
                    border_radius=ft.border_radius.all(
                        AppDimensions.BORDER_RADIUS),
                    ink=True, padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    opacity=1.0 if peca.ativo else 0.5,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                expand=True, spacing=2,
                                controls=[
                                    ft.Text(
                                        f"{peca.nome} (Ref: {peca.referencia})", size=AppFonts.BODY_LARGE),
                                    ft.Text(f"Estoque: {peca.quantidade_em_estoque} | Venda: R$ {peca.preco_venda:.2f}",
                                            size=AppFonts.BODY_SMALL, color=ft.Colors.ON_SURFACE_VARIANT),
                                ]
                            ),
                            ft.Row(spacing=0, controls=[
                                   action_icon, ft.Icon(ft.Icons.CHEVRON_RIGHT)])
                        ]
                    )
                )
                self._resultados_pesquisa_listview.controls.append(list_item)
        self.update()

    def mostrar_dialogo_confirmacao(self, peca_info: str, is_activating: bool):
        """Exibe um diálogo de confirmação usando a overlay."""
        logger.info(
            f"View: Exibindo diálogo de confirmação para {'ATIVAÇÃO' if is_activating else 'DESATIVAÇÃO'} da peça '{peca_info}'.")
        if self._confirm_dialog not in self.page.overlay:
            self.page.overlay.append(self._confirm_dialog)

        if is_activating:
            self._confirm_dialog.content.value = f"Tem certeza de que deseja reativar a peça '{peca_info}'?"
            self._confirm_dialog.actions[1].text = "Sim, Reativar"
            self._confirm_dialog.actions[1].on_click = lambda _: self.view_model.confirmar_ativacao(
            )
            self._confirm_dialog.actions[1].bgcolor = ft.Colors.GREEN_700
        else:
            self._confirm_dialog.content.value = f"Tem certeza de que deseja desativar a peça '{peca_info}'?"
            self._confirm_dialog.actions[1].text = "Sim, Desativar"
            self._confirm_dialog.actions[1].on_click = lambda _: self.view_model.confirmar_desativacao(
            )
            self._confirm_dialog.actions[1].bgcolor = self.page.theme.color_scheme.error

        self._confirm_dialog.open = True
        self.page.update()

    def fechar_dialogo(self, e=None):
        if self._confirm_dialog in self.page.overlay:
            self._confirm_dialog.open = False
            self.page.update()

    def mostrar_feedback(self, mensagem: str, sucesso: bool):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=self.page.theme.color_scheme.primary if sucesso else self.page.theme.color_scheme.error
        )
        self.page.snack_bar.open = True
        self.page.update()


def GerirPecasViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa para a rota /gerir_pecas."""
    return ft.View(
        route="/gerir_pecas",
        appbar=ft.AppBar(title=ft.Text("Gerenciar Peças e Estoque"),
                         center_title=True, bgcolor=page.theme.color_scheme.surface),
        floating_action_button=ft.Row(
            [
                ft.FloatingActionButton(
                    icon=ft.Icons.ARROW_BACK, tooltip="Voltar ao Dashboard", on_click=lambda _: page.go("/dashboard")),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD, tooltip="Cadastrar Nova Peça", on_click=lambda _: page.go("/cadastro_peca"))
            ],
            alignment=ft.MainAxisAlignment.END,
        ),
        controls=[
            ft.SafeArea(
                content=ft.Container(content=GerirPecasView(
                    page), padding=AppDimensions.PAGE_PADDING),
                expand=True
            )
        ],
        padding=0
    )
