# =================================================================================
# MÓDULO DA VIEW DE GERENCIAMENTO DE MECÂNICOS (gerir_mecanicos_view.py)
#
# OBJETIVO: Criar a tela para listar, buscar, ativar e desativar mecânicos.
# =================================================================================
import flet as ft
from src.viewmodels.gerir_mecanicos_viewmodel import GerirMecanicosViewModel
from src.models.models import Mecanico
from typing import List
from src.styles.style import AppDimensions, AppFonts
import logging

logger = logging.getLogger(__name__)


class GerirMecanicosView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = GerirMecanicosViewModel(page)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount

        self._campo_pesquisa = ft.TextField(
            label="Pesquisar por Nome, CPF ou Especialidade",
            on_submit=lambda e: self.view_model.pesquisar_mecanico(
                self._campo_pesquisa.value),
            prefix_icon=ft.Icons.SEARCH,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS)
        )
        self._resultados_pesquisa_listview = ft.ListView(
            expand=True, spacing=10)
        self._confirm_dialog = ft.AlertDialog(
            modal=True, title=ft.Text("Confirmar Ação"), content=ft.Text(),
            actions=[ft.TextButton(
                "Cancelar", on_click=self.fechar_dialogo), ft.ElevatedButton("Confirmar")],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.controls = [self._campo_pesquisa,
                         ft.Divider(), self._resultados_pesquisa_listview]
        logger.debug("GerirMecanicosView inicializada.")

    def did_mount(self):
        logger.info("GerirMecanicosView foi montada. Carregando mecânicos...")
        self.view_model.carregar_mecanicos_iniciais()

    def atualizar_lista_resultados(self, mecanicos: List[Mecanico]):
        logger.debug(
            f"View: Atualizando a lista com {len(mecanicos)} mecânicos.")
        self._resultados_pesquisa_listview.controls.clear()
        if not mecanicos:
            self._resultados_pesquisa_listview.controls.append(
                ft.Text("Nenhum mecânico encontrado."))
        else:
            for mecanico in mecanicos:
                action_icon = (
                    ft.IconButton(
                        icon=ft.Icons.PERSON_ADD, tooltip="Reativar Mecânico",
                        on_click=lambda e, m=mecanico: self.view_model.solicitar_ativacao(
                            m.id, m.nome),
                        icon_color=ft.Colors.GREEN_400,
                    ) if not mecanico.ativo else ft.IconButton(
                        icon=ft.Icons.PERSON_OFF, tooltip="Desativar Mecânico",
                        on_click=lambda e, m=mecanico: self.view_model.solicitar_desativacao(
                            m.id, m.nome),
                        icon_color=ft.Colors.RED_400,
                    )
                )
                list_item = ft.Container(
                    on_click=lambda _, m=mecanico: self.view_model.editar_mecanico(
                        m.id),
                    border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS), ink=True,
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    opacity=1.0 if mecanico.ativo else 0.5,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                expand=True, spacing=2,
                                controls=[
                                    ft.Text(mecanico.nome,
                                            size=AppFonts.BODY_LARGE),
                                    ft.Text(f"Especialidade: {mecanico.especialidade or 'N/A'}",
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

    def mostrar_dialogo_confirmacao(self, mecanico_nome: str, is_activating: bool):
        if self._confirm_dialog not in self.page.overlay:
            self.page.overlay.append(self._confirm_dialog)
        if is_activating:
            self._confirm_dialog.content.value = f"Tem certeza de que deseja reativar o mecânico '{mecanico_nome}'?"
            self._confirm_dialog.actions[1].text = "Sim, Reativar"
            self._confirm_dialog.actions[1].on_click = lambda _: self.view_model.confirmar_ativacao(
            )
            self._confirm_dialog.actions[1].bgcolor = ft.Colors.GREEN_700
        else:
            self._confirm_dialog.content.value = f"Tem certeza de que deseja desativar o mecânico '{mecanico_nome}'?"
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


def GerirMecanicosViewFactory(page: ft.Page) -> ft.View:
    return ft.View(
        route="/gerir_mecanicos",
        appbar=ft.AppBar(title=ft.Text("Gerenciar Mecânicos"),
                         center_title=True, bgcolor=page.theme.color_scheme.surface),
        floating_action_button=ft.Row(
            [
                ft.FloatingActionButton(
                    icon=ft.Icons.ARROW_BACK, tooltip="Voltar ao Dashboard", on_click=lambda _: page.go("/dashboard")),
                ft.FloatingActionButton(icon=ft.Icons.ADD, tooltip="Cadastrar Novo Mecânico",
                                        on_click=lambda _: page.go("/cadastro_mecanico"))
            ],
            alignment=ft.MainAxisAlignment.END,
        ),
        controls=[ft.SafeArea(content=ft.Container(content=GerirMecanicosView(
            page), padding=AppDimensions.PAGE_PADDING), expand=True)],
        padding=0
    )
