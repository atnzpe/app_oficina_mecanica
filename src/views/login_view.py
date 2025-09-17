# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DA VIEW DE LOGIN (login_view.py) - VERSÃO 2.0
#
# OBJETIVO: Definir a interface visual da tela de login, inspirada nos
#           exemplos de UX/UI profissionais.
# =================================================================================
import flet as ft
from src.viewmodels.login_viewmodel import LoginViewModel


class LoginView(ft.Column):
    """
    A View para a tela de login. Herda de `ft.Column` e organiza os controlos
    visuais de login.
    """

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = LoginViewModel(page)
        self.view_model.vincular_view(self)

        # --- Componentes Visuais ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20

        self._username_field = ft.TextField(
            label="Nome de Utilizador",
            width=300,
            prefix_icon=ft.Icons.PERSON,
            border_radius=ft.border_radius.all(10),
        )
        self._password_field = ft.TextField(
            label="Senha",
            width=300,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            border_radius=ft.border_radius.all(10),
            on_submit=self.view_model.login,
        )
        self._login_button = ft.ElevatedButton(
            text="Entrar",
            width=300,
            height=45,
            icon=ft.Icons.LOGIN,
            on_click=self.view_model.login,
        )
        self._google_login_button = ft.OutlinedButton(
            text="Login com Google",
            width=300,
            height=45,
            icon=ft.Icons.LANGUAGE,
            on_click=self.view_model.login_google,
            tooltip="Funcionalidade futura",
        )
        self._error_text = ft.Text(value="", visible=False, color=ft.Colors.RED_500)

        # --- Estrutura da View ---
        self.controls = [
            ft.Icon(
                ft.Icons.CAR_REPAIR_ROUNDED, size=60, color=ft.Colors.BLUE_GREY_200
            ),
            ft.Text("Sistema de Gestão - Oficina", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Por favor, efetue o login para continuar."),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self._username_field,
            self._password_field,
            self._error_text,
            ft.Row(
                controls=[
                    self._login_button,
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

    def mostrar_erro(self, mensagem: str):
        """Método chamado pelo ViewModel para exibir uma mensagem de erro."""
        self._error_text.value = mensagem
        self._error_text.visible = True
        self.update()
