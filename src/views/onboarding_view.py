# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DA VIEW DE ONBOARDING (onboarding_view.py)
# Local: src/views/onboarding_view.py
#
# OBJETIVO: Definir a interface visual para a configuração inicial do usuário,
#           como o nome da oficina.
# =================================================================================

import flet as ft
import logging
from src.database import queries
from src.styles.style import AppFonts, AppDimensions

logger = logging.getLogger(__name__)

class OnboardingView(ft.Column):
    """
    View para a tela de Onboarding. Coleta os dados iniciais do usuário e da oficina.
    """
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        # O usuário logado é passado através da sessão da página.
        self.user = self.page.session.get("usuario_logado")

        if not self.user:
            # Se, por algum motivo, não houver usuário na sessão, redireciona para o login.
            self.page.go("/login")
            return

        logger.info(f"Criando a view de onboarding para o usuário: {self.user.nome}")

        # --- Componentes Visuais ---
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.CENTER
        self.spacing = 15

        self._user_name_field = ft.TextField(
            label="Seu Nome Completo",
            value=self.user.nome or "",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.PERSON,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
        )
        self._establishment_name_field = ft.TextField(
            label="Nome da Oficina",
            hint_text="Ex: Oficina do Gleyson",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.STORE,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
        )
        self._error_text = ft.Text(value="", visible=False)
        self._progress_ring = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)

        self._save_button = ft.ElevatedButton(
            text="Salvar e Começar a Usar",
            width=AppDimensions.FIELD_WIDTH,
            height=45,
            icon=ft.Icons.SAVE,
            on_click=self._handle_save_click,
        )

        # --- Estrutura da View ---
        self.controls = [
            ft.Icon(ft.Icons.WAVING_HAND, size=AppFonts.TITLE_LARGE),
            ft.Text("Bem-vindo(a)!", size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            ft.Text("Vamos configurar sua oficina rapidamente.", size=AppFonts.BODY_MEDIUM),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            self._user_name_field,
            self._establishment_name_field,
            self._error_text,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Row([self._save_button, self._progress_ring], alignment=ft.MainAxisAlignment.CENTER),
        ]

    def _handle_save_click(self, e):
        """
        Valida os campos e salva os dados do onboarding no banco de dados.
        """
        user_name = self._user_name_field.value.strip()
        establishment_name = self._establishment_name_field.value.strip()

        if not user_name or not establishment_name:
            self._error_text.value = "Todos os campos são obrigatórios."
            self._error_text.color = self.page.theme.color_scheme.error
            self._error_text.visible = True
            self.update()
            return

        # Desabilita os campos durante o processamento
        for field in [self._user_name_field, self._establishment_name_field, self._save_button]:
            field.disabled = True
        self._progress_ring.visible = True
        self.update()

        # Chama a query para salvar os dados.
        queries.complete_onboarding(
            user_id=self.user.id,
            user_name=user_name,
            establishment_name=establishment_name,
        )

        # Redireciona para o dashboard após completar.
        self.page.go("/dashboard")