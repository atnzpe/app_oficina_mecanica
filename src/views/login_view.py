# =================================================================================
# MÓDULO DA VIEW DE LOGIN (login_view.py)
#
# REATORAÇÃO:
#   - Adicionada a `LoginViewFactory` para alinhar com o padrão de roteamento
#     do projeto. A factory é responsável por construir o `ft.View` completo.
#   - Integrado o `style.py` para usar constantes de design globais (AppDimensions, AppFonts).
# =================================================================================
import flet as ft
from src.viewmodels.login_viewmodel import LoginViewModel
# Importa as classes de estilo para fontes e dimensões.
from src.styles.style import AppDimensions, AppFonts


# --- CONTEÚDO DA PÁGINA ---
# A classe LoginView agora funciona como o "recheio" da nossa página de login.
class LoginView(ft.Column):
    """
    A View para a tela de login. Herda de `ft.Column` e organiza os controles.
    """
    def __init__(self, page: ft.Page):
        # Chama o construtor da classe pai (ft.Column).
        super().__init__()
        
        # Armazena a referência da página principal do Flet.
        self.page = page
        
        # Instancia o ViewModel, que conterá toda a lógica de negócio.
        self.view_model = LoginViewModel(page)
        # Vincula esta View ao ViewModel para comunicação bidirecional.
        self.view_model.vincular_view(self)

        # --- Componentes Visuais ---
        
        # Define o alinhamento principal dos controles para o centro da coluna.
        self.alignment = ft.MainAxisAlignment.CENTER
        # Define o alinhamento horizontal dos controles para o centro.
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        # Define o espaçamento vertical entre os controles.
        self.spacing = 15

        # Campo de texto para o nome de usuário.
        self._username_field = ft.TextField(
            label="Nome de Usuário",
            # Utiliza a largura de campo padrão definida em AppDimensions.
            width=AppDimensions.FIELD_WIDTH,
            prefix_icon=ft.Icons.PERSON,
            # Utiliza o raio de borda padrão definido em AppDimensions.
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
        )
        
        # Campo de texto para a senha.
        self._password_field = ft.TextField(
            label="Senha",
            # Utiliza a largura de campo padrão.
            width=AppDimensions.FIELD_WIDTH,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            # Utiliza o raio de borda padrão.
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
            # Delega a ação de submissão (pressionar Enter) para o ViewModel.
            on_submit=self.view_model.login,
        )
        
        # Botão principal de login.
        self._login_button = ft.ElevatedButton(
            text="Entrar",
            # Utiliza a largura de campo padrão para consistência.
            width=AppDimensions.FIELD_WIDTH,
            height=45,
            icon=ft.Icons.LOGIN,
            # Delega a ação de clique para o ViewModel.
            on_click=self.view_model.login,
        )
        
        # Botão secundário para login com Google (funcionalidade futura).
        self._google_login_button = ft.OutlinedButton(
            text="Login com Google",
            # Utiliza a largura de campo padrão.
            width=AppDimensions.FIELD_WIDTH,
            height=45,
            icon=ft.Icons.LANGUAGE_OUTLINED, # Ícone mais apropriado
            # Delega a ação de clique para o placeholder no ViewModel.
            on_click=self.view_model.login_google,
            tooltip="Funcionalidade futura",
        )
        
        # Texto para exibir mensagens de erro, inicialmente invisível.
        # A cor será herdada do `error` do tema, garantindo contraste.
        self._error_text = ft.Text(value="", visible=False, color="red")
        
        # Anel de progresso para feedback visual durante o login.
        self._progress_ring = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)

        # --- Estrutura da View ---
        # Lista de todos os controles que serão exibidos na coluna.
        self.controls = [
            ft.Icon(
                name=ft.Icons.CAR_REPAIR_ROUNDED, 
                size=60, 
                # A cor é herdada do tema para se adaptar ao modo claro/escuro.
            ),
            # Título principal da tela, usando fontes do style.py.
            ft.Text("Sistema de Gestão - Oficina", size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            # Subtítulo/instrução para o usuário.
            ft.Text("Por favor, efetue o login para continuar."),
            # Um divisor invisível para criar espaçamento vertical.
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self._username_field,
            self._password_field,
            self._error_text,
            # Linha para agrupar o botão de login e o anel de progresso.
            ft.Row(
                controls=[
                    self._login_button,
                    self._progress_ring,
                ],
                # Centraliza os itens na linha.
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
        # Atualiza a interface para refletir as mudanças.
        self.update()

    def mostrar_erro(self, mensagem: str):
        """Método chamado pelo ViewModel para exibir uma mensagem de erro."""
        self._error_text.value = mensagem
        self._error_text.visible = True
        # Atualiza a interface para exibir o erro.
        self.update()

# --- FACTORY DA VIEW ---
# Esta é a função que o main.py irá importar e chamar.
def LoginViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa de Login para o roteador."""
    # Instancia o conteúdo da view (a classe LoginView).
    view_content = LoginView(page)
    
    # Retorna o objeto ft.View, que representa a tela inteira.
    return ft.View(
        # Define a rota que ativa esta view.
        route="/login",
        # Centraliza verticalmente o conteúdo na tela.
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        # Centraliza horizontalmente o conteúdo na tela.
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        # Adiciona o conteúdo (nossa LoginView) à tela.
        controls=[
            # Garante que o conteúdo não sobreponha barras de status do sistema.
            ft.SafeArea(
                content=view_content,
                expand=True
            )
        ],
        # Remove o padding da View principal para o SafeArea controlar o espaçamento.
        padding=0
    )