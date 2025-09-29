# Compartilhe aqui o CÓDIGO COMPLETO da View.
# O código deve estar comentado.

# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DA VIEW DE ONBOARDING (onboarding_view.py)
# Local: src/views/onboarding_view.py
#
# REATORAÇÃO:
#   - A lógica de negócio foi movida para o `OnboardingViewModel`.
#   - A View agora apenas delega ações e exibe informações.
#   - Adicionada a `OnboardingViewFactory` para integração com o roteador.
#   - Integrado o `style.py` para padronização da UI.
# =================================================================================

import flet as ft
import logging
# Importa o ViewModel correspondente que gerencia a lógica desta view.
from src.viewmodels.onboarding_viewmodel import OnboardingViewModel
# Importa as classes de estilo para fontes e dimensões.
from src.styles.style import AppFonts, AppDimensions

# Configura o logger para este módulo.
logger = logging.getLogger(__name__)

# --- CONTEÚDO DA PÁGINA ---
class OnboardingView(ft.Column):
    """
    View para a tela de Onboarding. Delega toda a lógica para o OnboardingViewModel.
    """
    def __init__(self, page: ft.Page):
        # Chama o construtor da classe pai (ft.Column).
        super().__init__()
        
        # Armazena a referência da página principal do Flet.
        self.page = page
        
        # Instancia e vincula o ViewModel correspondente.
        self.view_model = OnboardingViewModel(page)
        self.view_model.vincular_view(self)

        # Se não houver usuário na sessão, o ViewModel lida com o redirecionamento.
        if not self.view_model.user:
            self.page.go("/login")
            return

        # Log para registrar qual usuário está vendo a tela de onboarding.
        logger.info(f"Criando a view de onboarding para o usuário: {self.view_model.user.nome}")

        # --- Configurações de Layout da Coluna ---
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.CENTER
        self.spacing = 15

        # --- Componentes Visuais ---

        # Campo para o nome completo do usuário, pré-preenchido com o nome do login.
        self._user_name_field = ft.TextField(
            label="Seu Nome Completo",
            value=self.view_model.user.nome or "",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.PERSON,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS)
        )
        
        # Campo para o nome do estabelecimento (oficina).
        self._establishment_name_field = ft.TextField(
            label="Nome da Oficina",
            hint_text="Ex: Oficina do Gleyson",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.STORE,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
            # Delega a ação de submissão (pressionar Enter) para o ViewModel.
            on_submit=self.view_model.save_onboarding_data
        )
        
        # Texto para exibir mensagens de erro.
        self._error_text = ft.Text(value="", visible=False, color="red")
        
        # Anel de progresso para feedback visual durante o salvamento.
        self._progress_ring = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)
        
        # Botão principal para salvar os dados.
        self._save_button = ft.ElevatedButton(
            text="Salvar e Começar a Usar",
            width=AppDimensions.FIELD_WIDTH,
            height=45,
            icon=ft.Icons.SAVE_AS, # Ícone mais descritivo para salvar e continuar
            # Delega a ação de clique para o ViewModel.
            on_click=self.view_model.save_onboarding_data,
        )

        # --- Estrutura da View ---
        # Lista de todos os controles a serem exibidos na coluna.
        self.controls = [
            # Ícone de boas-vindas.
            ft.Icon(ft.Icons.WAVING_HAND, size=AppFonts.TITLE_LARGE),
            # Título principal da tela.
            ft.Text("Bem-vindo(a)!", size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            # Subtítulo com instruções.
            ft.Text("Vamos configurar sua oficina rapidamente.", size=AppFonts.BODY_MEDIUM),
            # Divisor invisível para criar espaçamento.
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            self._user_name_field,
            self._establishment_name_field,
            self._error_text,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            # Linha para alinhar o botão e o anel de progresso.
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
        padding=AppDimensions.PAGE_PADDING, # Adiciona padding padrão.
        controls=[
            OnboardingView(page)
        ]
    )