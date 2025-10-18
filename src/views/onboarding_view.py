# =================================================================================
# MÓDULO DA VIEW DE ONBOARDING (onboarding_view.py)
#
# ATUALIZAÇÃO (CRUD Estabelecimento):
#   - O formulário foi expandido para incluir todos os campos detalhados
#     do estabelecimento (Endereço, Telefone, CPF/CNPJ, etc.).
# =================================================================================

import flet as ft
import logging
from src.viewmodels.onboarding_viewmodel import OnboardingViewModel
from src.styles.style import AppFonts, AppDimensions

logger = logging.getLogger(__name__)


class OnboardingView(ft.Column):
    """
    View para a tela de Onboarding. Delega toda a lógica para o OnboardingViewModel.
    """

    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page
        self.view_model = OnboardingViewModel(page)
        self.view_model.vincular_view(self)

        if not self.view_model.user:
            self.page.go("/login")
            return

        logger.info(
            f"Criando a view de onboarding para o usuário: {self.view_model.user.nome}")

        # --- Configurações de Layout ---
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        # Mudar para START para formulários longos
        self.alignment = ft.MainAxisAlignment.START
        self.spacing = 15
        # Habilita a rolagem
        self.scroll = ft.ScrollMode.ADAPTIVE

        # --- Componentes Visuais ---

        # --- Seção 1: Dados do Usuário ---
        self._user_name_field = ft.TextField(
            label="Seu Nome Completo*",
            value=self.view_model.user.nome or "",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.PERSON,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS)
        )

        # --- Seção 2: Dados do Estabelecimento ---
        self._establishment_name_field = ft.TextField(
            label="Nome da Oficina*",
            hint_text="Ex: Oficina do João",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.STORE,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
        )

        self._endereco_field = ft.TextField(
            label="Endereço",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.LOCATION_ON_OUTLINED,
            border_radius=AppDimensions.BORDER_RADIUS
        )
        self._telefone_field = ft.TextField(
            label="Telefone",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.PHONE_OUTLINED,
            keyboard_type=ft.KeyboardType.PHONE,
            border_radius=AppDimensions.BORDER_RADIUS
        )
        self._responsavel_field = ft.TextField(
            label="Responsável",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
            border_radius=AppDimensions.BORDER_RADIUS
        )
        self._cpf_cnpj_field = ft.TextField(
            label="CPF ou CNPJ",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.POLICY_OUTLINED,
            border_radius=AppDimensions.BORDER_RADIUS
        )
        self._chave_pix_field = ft.TextField(
            label="Chave PIX",
            hint_text="Telefone, e-mail, CNPJ ou chave aleatória",
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.PAYMENT,
            border_radius=AppDimensions.BORDER_RADIUS
        )

        self._error_text = ft.Text(value="", visible=False, color="red")
        self._progress_ring = ft.ProgressRing(
            width=20, height=20, stroke_width=2, visible=False)

        self._save_button = ft.ElevatedButton(
            text="Salvar e Começar a Usar",
            width=AppDimensions.FIELD_WIDTH,
            height=45,
            icon=ft.Icons.SAVE_AS,
            on_click=self.view_model.save_onboarding_data,
        )

        # --- Estrutura da View ---
        self.controls = [
            ft.Icon(ft.Icons.WAVING_HAND, size=AppFonts.TITLE_LARGE,
                    color=page.theme.color_scheme.primary),
            ft.Text("Bem-vindo(a)!", size=AppFonts.TITLE_MEDIUM,
                    weight=ft.FontWeight.BOLD),
            ft.Text("Vamos configurar sua oficina rapidamente.",
                    size=AppFonts.BODY_MEDIUM),
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),

            ft.Text("Seus Dados Pessoais", size=AppFonts.BODY_LARGE),
            self._user_name_field,

            ft.Divider(height=15),

            ft.Text("Dados da Oficina", size=AppFonts.BODY_LARGE),
            self._establishment_name_field,
            self._endereco_field,
            self._telefone_field,
            self._responsavel_field,
            self._cpf_cnpj_field,
            self._chave_pix_field,

            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self._error_text,
            ft.Row([self._save_button, self._progress_ring],
                   alignment=ft.MainAxisAlignment.CENTER),
        ]

    def obter_dados_formulario(self) -> dict:
        """Envia os dados dos campos para o ViewModel quando solicitado."""
        return {
            "user_name": self._user_name_field.value,
            "nome": self._establishment_name_field.value,
            "endereco": self._endereco_field.value,
            "telefone": self._telefone_field.value,
            "responsavel": self._responsavel_field.value,
            "cpf_cnpj": self._cpf_cnpj_field.value,
            "chave_pix": self._chave_pix_field.value,
        }

    def mostrar_progresso(self, visivel: bool):
        """Controla a visibilidade dos campos e do anel de progresso."""
        self._progress_ring.visible = visivel
        self_save_button_disabled = visivel
        # Desabilita todos os campos durante o progresso
        for control in self.controls:
            if isinstance(control, ft.TextField):
                control.disabled = visivel
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
        padding=AppDimensions.PAGE_PADDING,
        controls=[
            OnboardingView(page)
        ]
    )
