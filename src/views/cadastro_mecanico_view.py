# =================================================================================
# MÓDULO DA VIEW DE CADASTRO DE MECÂNICO (cadastro_mecanico_view.py)
#
# OBJETIVO: Criar o formulário para o cadastro de novos mecânicos.
# =================================================================================
import flet as ft
from src.viewmodels.cadastro_mecanico_viewmodel import CadastroMecanicoViewModel
from src.styles.style import AppDimensions, AppFonts
from typing import Callable, Optional
from threading import Timer
import logging

logger = logging.getLogger(__name__)


class CadastroMecanicoView(ft.Column):
    """
    A View para o formulário de cadastro de mecânicos.
    """

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = CadastroMecanicoViewModel(page)
        self.view_model.vincular_view(self)

        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

        # --- Layout ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 15

        # --- Componentes do Formulário ---
        self._nome_field = ft.TextField(
            label="Nome do Mecânico*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._cpf_field = ft.TextField(label="CPF*", width=AppDimensions.FIELD_WIDTH,
                                       border_radius=AppDimensions.BORDER_RADIUS, keyboard_type=ft.KeyboardType.NUMBER)
        self._endereco_field = ft.TextField(
            label="Endereço", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)  # NOVO
        self._telefone_field = ft.TextField(label="Telefone", width=AppDimensions.FIELD_WIDTH,
                                            border_radius=AppDimensions.BORDER_RADIUS, keyboard_type=ft.KeyboardType.PHONE)  # NOVO
        self._especialidade_field = ft.TextField(label="Especialidade", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)        self._dialogo_feedback = ft.AlertDialog(
            modal=True, title=ft.Text(), content=ft.Text(), actions=[])

        self.controls = [
            ft.Text("Cadastro de Novo Mecânico",
                    size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            self._nome_field,
            self._cpf_field,
            self._endereco_field,  # NOVO
            self._telefone_field,  # NOVO
            self._especialidade_field,
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Cancelar", on_click=self.view_model.cancelar_cadastro),
                    ft.ElevatedButton("Salvar Mecânico", icon=ft.Icons.SAVE,
                                      on_click=lambda _: self.view_model.salvar_mecanico()),
                ],
                alignment=ft.MainAxisAlignment.END, spacing=10, width=AppDimensions.FIELD_WIDTH
            )
        ]
        logger.debug("CadastroMecanicoView inicializada.")

    def obter_dados_formulario(self) -> dict:
        """Coleta e retorna os dados do formulário para o ViewModel."""
        return {
            "nome": self._nome_field.value,
            "cpf": self._cpf_field.value,
            "endereco": self._endereco_field.value,  # NOVO
            "telefone": self._telefone_field.value,  # NOVO
            "especialidade": self._especialidade_field.value,
        }

    # --- Métodos de Diálogo (Padrão com Overlay) ---
    def _fechar_dialogo_e_agir(self, e):
        self.fechar_dialogo()
        if self._acao_pos_dialogo:
            Timer(0.1, self._acao_pos_dialogo).start()

    def mostrar_dialogo_feedback(self, titulo: str, conteudo: str, acao_callback: Optional[Callable[[], None]] = None):
        self._acao_pos_dialogo = acao_callback
        self._dialogo_feedback.title.value = titulo
        self._dialogo_feedback.content.value = conteudo
        self._dialogo_feedback.actions = [ft.TextButton(
            "OK", on_click=self._fechar_dialogo_e_agir)]

        if self._dialogo_feedback not in self.page.overlay:
            self.page.overlay.append(self._dialogo_feedback)

        self._dialogo_feedback.open = True
        self.page.update()

    def fechar_dialogo(self, e=None):
        if self._dialogo_feedback in self.page.overlay:
            self._dialogo_feedback.open = False
            self.page.update()


def CadastroMecanicoViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa de Cadastro de Mecânico para o roteador."""
    return ft.View(
        route="/cadastro_mecanico",
        appbar=ft.AppBar(
            title=ft.Text("Cadastrar Novo Mecânico"), center_title=True,
            bgcolor=page.theme.color_scheme.surface,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go(
                "/gerir_mecanicos"), tooltip="Voltar para a Lista de Mecânicos")
        ),
        controls=[ft.SafeArea(content=ft.Container(content=CadastroMecanicoView(
            page), alignment=ft.alignment.center, expand=True), expand=True)],
        padding=0
    )
