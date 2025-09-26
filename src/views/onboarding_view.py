# Compartilhe aqui o CÓDIGO COMPLETO da View.
# O código deve estar comentado.

# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DA VIEW DE ONBOARDING (onboarding_view.py)
# Local: src/views/onboarding_view.py
#
# REATORAÇÃO:
#   - A lógica de negócio foi movida para o `OnboardingViewModel`.
#   - A View agora apenas delega ações e exibe informações.
#   - Adicionada a `OnboardingViewFactory` para integração com o roteador.
# =================================================================================

import flet as ft
import logging
# Importa o ViewModel recém-criado.
from src.viewmodels.onboarding_viewmodel import OnboardingViewModel
from src.styles.style import AppFonts, AppDimensions

logger = logging.getLogger(__name__)

# --- CONTEÚDO DA PÁGINA ---
class OnboardingView(ft.Column):
    """
    View para a tela de Onboarding. Delega toda a lógica para o OnboardingViewModel.
    """
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        # Instancia e vincula o ViewModel correspondente.
        self.view_model = OnboardingViewModel(page)
        self.view_model.vincular_view(self)

        # Se não houver usuário na sessão, o ViewModel lida com isso.
        # Mas uma verificação extra aqui pode evitar a renderização desnecessária.
        if not self.view_model.user:
            self.page.go("/login")
            return

        logger.info(f"Criando a view de onboarding para o usuário: {self.view_model.user.nome}")

        # --- Componentes Visuais ---
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.CENTER
        self.spacing = 15

        self._user_name_field = ft.TextField(
            label="Seu Nome Completo",
            value=self.view_model.user.nome or "",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.PERSON,
        )
        self._establishment_name_field = ft.TextField(
            label="Nome da Oficina",
            hint_text="Ex: Oficina do Gleyson",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.STORE,
            on_submit=self.view_model.save_onboarding_data # Delega o Enter para o ViewModel
        )
        self._error_text = ft.Text(value="", visible=False, color=ft.Colors.RED)
        self._progress_ring = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)
        self._save_button = ft.ElevatedButton(
            text="Salvar e Começar a Usar",
            width=AppDimensions.FIELD_WIDTH,
            height=45,
            icon=ft.Icons.SAVE,
            on_click=self.view_model.save_onboarding_data, # Delega o clique para o ViewModel
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

    def obter_dados_formulario(self) -> dict:
        """Envia os dados dos campos para o ViewModel quando solicitado."""
        return {
            "user_name": self._user_name_field.value.strip(),
            "establishment_name": self._establishment_name_field.value.strip()
        }

    def mostrar_progresso(self, visivel: bool):
        """Controla a visibilidade dos campos e do anel de progresso."""
        self._progress_ring.visible = visivel
        self._user_name_field.disabled = visivel
        self._establishment_name_field.disabled = visivel
        self._save_button.disabled = visivel
        self.update()

    def mostrar_erro(self, mensagem: str):
        """Exibe uma mensagem de erro na tela, conforme comandado pelo ViewModel."""
        self._error_text.value = mensagem
        self._error_text.visible = True
        self.update()

# --- FACTORY DA VIEW ---
def OnboardingViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa de Onboarding para o roteador."""
    return ft.View(
        route="/onboarding",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            OnboardingView(page)
        ]
    )