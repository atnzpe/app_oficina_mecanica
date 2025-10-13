# =================================================================================
# MÓDULO DA VIEW DE EDIÇÃO DE MECÂNICO (editar_mecanico_view.py)
#
# OBJETIVO: Criar o formulário para a edição dos dados de um mecânico existente.
# =================================================================================
import flet as ft
import logging
from src.viewmodels.editar_mecanico_viewmodel import EditarMecanicoViewModel
from src.models.models import Mecanico
from src.styles.style import AppDimensions, AppFonts
from threading import Timer
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class EditarMecanicoView(ft.Column):
    def __init__(self, page: ft.Page, mecanico_id: int):
        super().__init__()
        self.page = page
        self.view_model = EditarMecanicoViewModel(page, mecanico_id)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount
        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

        # --- Layout ---
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.CENTER
        self.spacing = 15

        # --- Componentes ---
        self._nome_field = ft.TextField(label="Nome do Mecânico*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._cpf_field = ft.TextField(label="CPF*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS, keyboard_type=ft.KeyboardType.NUMBER)
        self._especialidade_field = ft.TextField(label="Especialidade", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._dialogo_feedback = ft.AlertDialog(modal=True, title=ft.Text(), content=ft.Text(), actions=[])

        self.controls = [
            ft.Text("Editando Mecânico", size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            self._nome_field, self._cpf_field, self._especialidade_field,
            ft.Row(
                [
                    ft.ElevatedButton("Cancelar", on_click=lambda _: self.page.go("/gerir_mecanicos")),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Salvar Alterações", icon=ft.Icons.SAVE, on_click=lambda _: self.view_model.salvar_alteracoes()),
                ],
                width=AppDimensions.FIELD_WIDTH
            )
        ]
        logger.debug("EditarMecanicoView inicializada.")

    def did_mount(self):
        logger.info(f"EditarMecanicoView montada para mecânico ID: {self.view_model.mecanico_id}. Carregando dados...")
        self.view_model.carregar_dados()

    def preencher_formulario(self, mecanico: Mecanico):
        logger.debug(f"View: Preenchendo formulário com dados de '{mecanico.nome}'.")
        self._nome_field.value = mecanico.nome or ""
        self._cpf_field.value = mecanico.cpf or ""
        self._especialidade_field.value = mecanico.especialidade or ""
        self.update()

    def obter_dados_formulario(self) -> dict:
        return {
            "nome": self._nome_field.value,
            "cpf": self._cpf_field.value,
            "especialidade": self._especialidade_field.value,
        }

    # --- Métodos de Diálogo ---
    def _fechar_dialogo_e_agir(self, e):
        self.fechar_dialogo()
        if self._acao_pos_dialogo:
            Timer(0.1, self._acao_pos_dialogo).start()

    def mostrar_dialogo_feedback(self, titulo: str, conteudo: str, acao_callback: Optional[Callable[[], None]] = None):
        self._acao_pos_dialogo = acao_callback
        self._dialogo_feedback.title.value = titulo
        self._dialogo_feedback.content.value = conteudo
        self._dialogo_feedback.actions = [ft.TextButton("OK", on_click=self._fechar_dialogo_e_agir)]
        if self._dialogo_feedback not in self.page.overlay: self.page.overlay.append(self._dialogo_feedback)
        self._dialogo_feedback.open = True
        self.page.update()

    def fechar_dialogo(self, e=None):
        if self._dialogo_feedback in self.page.overlay:
            self._dialogo_feedback.open = False
            self.page.update()

def EditarMecanicoViewFactory(page: ft.Page, mecanico_id: int) -> ft.View:
    return ft.View(
        route=f"/editar_mecanico/{mecanico_id}",
        appbar=ft.AppBar(
            title=ft.Text("Editar Mecânico"), center_title=True,
            bgcolor=page.theme.color_scheme.surface,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go("/gerir_mecanicos"), tooltip="Voltar para a Lista de Mecânicos")
        ),
        controls=[ft.SafeArea(content=ft.Container(content=EditarMecanicoView(page, mecanico_id), alignment=ft.alignment.center, expand=True), expand=True)],
        padding=0
    )