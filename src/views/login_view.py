# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DA VIEW DE LOGIN (login_view.py)
#
# ATUALIZAÇÃO:
#   - Adicionado o método `mostrar_progresso` para permitir que o ViewModel
#     controle o estado visual dos botões e do anel de progresso durante a
#     tentativa de login.
# =================================================================================
import flet as ft
from src.viewmodels.login_viewmodel import LoginViewModel
from src.styles.style import AppDimensions, AppFonts


class LoginView(ft.Column):
    """
    A View para a tela de login. Herda de `ft.Column` e organiza os controles.
    """
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = LoginViewModel(page)
        self.view_model.vincular_view(self)

        # --- Componentes Visuais ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 10

        self._username_field = ft.TextField(
            label="Nome de Usuário",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.PERSON,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
        )
        self._password_field = ft.TextField(
            label="Senha",
            width=AppDimensions.FIELD_WIDTH,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
            on_submit=self.view_model.login,
        )
        self._login_button = ft.ElevatedButton(
            text="Entrar",
            width=AppDimensions.FIELD_WIDTH,
            height=45,
            icon=ft.Icons.LOGIN,
            on_click=self.view_model.login,
        )
        self._google_login_button = ft.OutlinedButton(
            text="Login com Google",
            width=AppDimensions.FIELD_WIDTH,
            height=45,
            icon=ft.Icons.LANGUAGE,
            on_click=self.view_model.login_google, # Agora esta função existe no ViewModel
            tooltip="Funcionalidade futura",
        )
        self._error_text = ft.Text(value="", visible=False)
        self._progress_ring = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)

        # --- Estrutura da View ---
        self.controls = [
            ft.Icon(
                ft.Icons.CAR_REPAIR_ROUNDED, size=60, color=ft.Colors.BLUE_GREY_200
            ),
            ft.Text("Sistema de Gestão - Oficina", size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            ft.Text("Por favor, efetue o login para continuar."),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self._username_field,
            self._password_field,
            self._error_text,
            ft.Row(
                controls=[
                    self._login_button,
                    self._progress_ring, # Adicionado para feedback visual
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Text("ou"),
            self._google_login_button,
        ]

    def obter_dados_login(self) -> dict:
        """Método chamado pelo ViewModel para obter os dados dos campos."""
        return {
            "username": self._username_field.value,
            "password": self._password_field.value,
        }

    # --- MÉTODO ADICIONADO ---
    def mostrar_progresso(self, visivel: bool):
        """
        Controla a visibilidade dos campos e do anel de progresso.
        É comandado pelo ViewModel.

        :param visivel: True para mostrar o progresso, False para esconder.
        """
        # Mostra ou esconde o anel de carregamento.
        self._progress_ring.visible = visivel
        # Desabilita os campos e botões para evitar cliques duplos.
        self._username_field.disabled = visivel
        self._password_field.disabled = visivel
        self._login_button.disabled = visivel
        self._google_login_button.disabled = visivel
        # Atualiza a tela para refletir as mudanças.
        self.update()

    def mostrar_erro(self, mensagem: str):
        """Método chamado pelo ViewModel para exibir uma mensagem de erro."""
        self._error_text.value = mensagem
        self._error_text.color = ft.Colors.RED_500
        self._error_text.visible = True
        self.update()