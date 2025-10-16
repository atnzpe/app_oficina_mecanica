# =================================================================================
# MÓDULO DA VIEW DE MINHA CONTA (minha_conta_view.py)
#
# OBJETIVO: Construir a interface para o usuário alterar seus próprios dados,
#           começando pela senha.
# =================================================================================
import flet as ft
import logging
from src.viewmodels.minha_conta_viewmodel import MinhaContaViewModel
from src.styles.style import AppDimensions, AppFonts
from typing import Callable, Optional
from threading import Timer

logger = logging.getLogger(__name__)

class MinhaContaView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = MinhaContaViewModel(page)
        self.view_model.vincular_view(self)
        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

        # --- Layout ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 15

        # --- Componentes ---
        self._senha_atual_field = ft.TextField(label="Senha Atual", password=True, can_reveal_password=True, width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._nova_senha_field = ft.TextField(label="Nova Senha", password=True, can_reveal_password=True, width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._confirmar_senha_field = ft.TextField(label="Confirmar Nova Senha", password=True, can_reveal_password=True, width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        
        self._dialogo_feedback = ft.AlertDialog(modal=True, title=ft.Text(), content=ft.Text(), actions=[])

        self.controls = [
            ft.Text("Alterar Minha Senha", size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            self._senha_atual_field,
            self._nova_senha_field,
            self._confirmar_senha_field,
            ft.Row(
                [
                    ft.ElevatedButton("Salvar Alterações", icon=ft.Icons.SAVE, on_click=lambda _: self.view_model.alterar_senha()),
                ],
                alignment=ft.MainAxisAlignment.END, width=AppDimensions.FIELD_WIDTH
            )
        ]
        logger.debug("MinhaContaView inicializada.")

    def obter_dados_formulario(self) -> dict:
        """Coleta e retorna os dados do formulário."""
        return {
            "senha_atual": self._senha_atual_field.value,
            "nova_senha": self._nova_senha_field.value,
            "confirmar_senha": self._confirmar_senha_field.value,
        }
    
    def limpar_formulario(self):
        """Limpa todos os campos de senha."""
        logger.debug("View: Limpando campos do formulário de alteração de senha.")
        self._senha_atual_field.value = ""
        self._nova_senha_field.value = ""
        self._confirmar_senha_field.value = ""
        self.update()

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

def MinhaContaViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa de Minha Conta para o roteador."""
    return ft.View(
        route="/minha_conta",
        appbar=ft.AppBar(
            title=ft.Text("Minha Conta"), center_title=True,
            bgcolor=page.theme.color_scheme.surface,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go("/dashboard"), tooltip="Voltar ao Dashboard")
        ),
        controls=[ft.SafeArea(content=ft.Container(content=MinhaContaView(page), alignment=ft.alignment.center, expand=True), expand=True)],
        padding=0
    )