# =================================================================================
# MÓDULO DA VIEW DE LOGIN (login_view.py)
#
# REATORAÇÃO:
#   - Adicionada a `LoginViewFactory` para alinhar com o padrão de roteamento
#     do projeto. A factory é responsável por construir o `ft.View` completo.
# =================================================================================
import flet as ft
from src.viewmodels.login_viewmodel import LoginViewModel
from src.styles.style import AppDimensions, AppFonts


# --- CONTEÚDO DA PÁGINA ---
# A classe LoginView agora funciona como o "recheio" da nossa página de login.
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
            on_click=self.view_model.login_google,
            tooltip="Funcionalidade futura",
        )
        self._error_text = ft.Text(value="", visible=False, color=ft.Colors.RED_500)
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

    def mostrar_progresso(self, visivel: bool):
        """
        Controla a visibilidade dos campos e do anel de progresso.
        """
        self._progress_ring.visible = visivel
        self._username_field.disabled = visivel
        self._password_field.disabled = visivel
        self._login_button.disabled = visivel
        self._google_login_button.disabled = visivel
        self.update()

    def mostrar_erro(self, mensagem: str):
        """Método chamado pelo ViewModel para exibir uma mensagem de erro."""
        self._error_text.value = mensagem
        self._error_text.visible = True
        self.update()

# --- FACTORY DA VIEW ---
# Esta é a função que o main.py irá importar e chamar.
def LoginViewFactory(page: ft.Page) -> ft.View:
    """
    Cria a View completa de Login para o roteador.
    """
    # 1. Cria a instância do conteúdo da view.
    view_content = LoginView(page)
    
    # 2. Retorna o objeto ft.View, que representa a tela inteira.
    return ft.View(
        route="/login",
        # Centraliza todo o conteúdo na tela.
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            # Coloca o conteúdo (nossa coluna LoginView) dentro da view.
            view_content
        ],
        padding=10
    )