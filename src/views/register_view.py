# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DA VIEW DE REGISTRO (register_view.py)
#
# OBJETIVO: Definir a interface visual para o cadastro do primeiro usuário
#           administrador. Esta tela só é acessível se não houver nenhum
#           outro usuário no sistema.
# =================================================================================
import flet as ft
import logging
from src.services import auth_service

logger = logging.getLogger(__name__)

class RegisterView(ft.Column):
    """
    View para a tela de cadastro do primeiro administrador.
    """
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page

        # --- Componentes Visuais ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20

        self._username_field = ft.TextField(
            label="Nome de Usuário (Admin)",
            width=300,
            prefix_icon=ft.Icons.PERSON_ADD,
            border_radius=ft.border_radius.all(10),
            hint_text="Ex: admin@oficina.com"
        )
        self._password_field = ft.TextField(
            label="Senha",
            width=300,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            border_radius=ft.border_radius.all(10),
        )
        self._confirm_password_field = ft.TextField(
            label="Confirmar Senha",
            width=300,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            border_radius=ft.border_radius.all(10),
        )
        self._register_button = ft.ElevatedButton(
            text="Criar Administrador e Iniciar",
            width=300,
            height=45,
            icon=ft.Icons.APP_REGISTRATION,
            on_click=self._handle_register_click,
        )
        self._error_text = ft.Text(value="", visible=False, color=ft.Colors.RED_500)

        # --- Estrutura da View ---
        self.controls = [
            ft.Icon(
                ft.Icons.SHIELD, size=60, color=ft.Colors.BLUE_GREY_200
            ),
            ft.Text("Configuração Inicial do Sistema", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Crie o primeiro usuário administrador para começar a usar o sistema."),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self._username_field,
            self._password_field,
            self._confirm_password_field,
            self._error_text,
            self._register_button,
        ]

    def _handle_register_click(self, e):
        """
        Lógica executada ao clicar no botão de registrar.
        """
        self._error_text.visible = False

        # Validação dos campos de entrada.
        if not all([self._username_field.value, self._password_field.value, self._confirm_password_field.value]):
            self._show_error("Todos os campos são obrigatórios.")
            return
        if self._password_field.value != self._confirm_password_field.value:
            self._show_error("As senhas não coincidem.")
            return

        # Tentativa de registro via serviço de autenticação.
        success, message = auth_service.register_user(
            name=self._username_field.value.strip(),
            password=self._password_field.value,
            profile='admin'  # O primeiro usuário é sempre 'admin'.
        )

        if success:
            logger.info("Usuário administrador criado com sucesso. Redirecionando para o login.")
            # Mostra uma mensagem de sucesso antes de redirecionar.
            self.page.snack_bar = ft.SnackBar(ft.Text("Administrador criado! Faça o login para continuar."), bgcolor=ft.Colors.GREEN)
            self.page.snack_bar.open = True
            # Redireciona para a tela de login.
            self.page.go("/login")
        else:
            self._show_error(message)

    def _show_error(self, message: str):
        """Função auxiliar para exibir uma mensagem de erro na tela."""
        self._error_text.value = message
        self._error_text.visible = True
        self.update()