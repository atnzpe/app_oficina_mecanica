# =================================================================================
# MÓDULO DA VIEW DE REGISTRO (register_view.py)
#
# REATORAÇÃO:
#   - Adicionada a `RegisterViewFactory` para padronizar a criação da view
#     pelo roteador em main.py.
#   - Integrado o `style.py` para utilizar as constantes de design globais.
#   - A lógica de negócio permanece na view temporariamente, mas idealmente
#     seria movida para um `RegisterViewModel`.
# =================================================================================
import flet as ft
import logging
from src.services import auth_service
# Importa as classes de estilo para fontes e dimensões.
from src.styles.style import AppDimensions, AppFonts

# Configura o logger para este módulo.
logger = logging.getLogger(__name__)

# --- CONTEÚDO DA PÁGINA ---
class RegisterView(ft.Column):
    """
    View para a tela de cadastro do primeiro administrador do sistema.
    """
    def __init__(self, page: ft.Page):
        # Chama o construtor da classe pai (ft.Column).
        super().__init__()
        
        # Armazena a referência da página principal do Flet.
        self.page = page

        # --- Configurações de Layout da Coluna ---
        # Alinha todos os controles ao centro do eixo principal (vertical).
        self.alignment = ft.MainAxisAlignment.CENTER
        # Alinha todos os controles ao centro do eixo transversal (horizontal).
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        # Define o espaçamento padrão entre os controles.
        self.spacing = 20

        # --- Componentes Visuais ---

        # Campo de texto para o nome do usuário administrador.
        self._username_field = ft.TextField(
            label="Nome de Usuário (Admin)",
            # Utiliza a largura de campo padrão do AppDimensions.
            width=AppDimensions.FIELD_WIDTH,
            # Ícone que representa a adição de um novo usuário.
            prefix_icon=ft.Icons.PERSON_ADD,
            # Cantos arredondados padronizados.
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
            hint_text="Ex: admin"
        )
        
        # Campo de texto para a senha.
        self._password_field = ft.TextField(
            label="Senha",
            width=AppDimensions.FIELD_WIDTH,
            password=True,
            can_reveal_password=True,
            # Ícone universal para senhas.
            prefix_icon=ft.Icons.LOCK_OUTLINED,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
        )
        
        # Campo de texto para a confirmação da senha.
        self._confirm_password_field = ft.TextField(
            label="Confirmar Senha",
            width=AppDimensions.FIELD_WIDTH,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINED,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
            # Permite que o usuário envie o formulário pressionando Enter neste campo.
            on_submit=self._handle_register_click,
        )
        
        # Botão para submeter o formulário de registro.
        self._register_button = ft.ElevatedButton(
            text="Criar Administrador e Iniciar",
            width=AppDimensions.FIELD_WIDTH,
            height=45,
            # Ícone que representa o registro ou a criação de algo novo na aplicação.
            icon=ft.Icons.APP_REGISTRATION,
            on_click=self._handle_register_click,
        )
        
        # Texto para exibir mensagens de erro, inicialmente invisível.
        # A cor será herdada do tema (`error` color scheme).
        self._error_text = ft.Text(value="", visible=False, color="red")

        # --- Estrutura da View ---
        # A lista de controles que compõem a tela de registro.
        self.controls = [
            # Ícone principal da tela, representando segurança e configuração inicial.
            ft.Icon(
                name=ft.Icons.SHIELD_OUTLINED, 
                size=60, 
                # A cor se adaptará automaticamente ao tema (claro/escuro).
            ),
            # Título da página, utilizando as fontes padronizadas.
            ft.Text("Configuração Inicial do Sistema", size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            # Texto instrutivo para o usuário.
            ft.Text("Crie o primeiro usuário administrador para começar a usar o sistema."),
            # Divisor transparente para criar um espaçamento vertical.
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
        (Idealmente, esta lógica estaria em um RegisterViewModel).
        """
        # Esconde qualquer mensagem de erro anterior.
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

        # Lida com o resultado do registro.
        if success:
            logger.info("Usuário administrador criado com sucesso. Redirecionando para o login.")
            # Mostra uma mensagem de sucesso (SnackBar) antes de redirecionar.
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Administrador criado! Faça o login para continuar."), 
                # Usa a cor de sucesso personalizada do tema, se disponível, ou um verde padrão.
                bgcolor=ft.Colors.GREEN_700
            )
            self.page.snack_bar.open = True
            # Redireciona para a tela de login.
            self.page.go("/login")
        else:
            # Se falhar, mostra a mensagem de erro retornada pelo serviço.
            self._show_error(message)

    def _show_error(self, message: str):
        """Função auxiliar para exibir uma mensagem de erro na tela."""
        self._error_text.value = message
        self._error_text.visible = True
        # Atualiza a interface para mostrar o erro.
        self.update()

# --- FACTORY DA VIEW ---
def RegisterViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa de Registro para o roteador."""
    view_content = RegisterView(page)

    return ft.View(
        route="/register",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            # Envolve o conteúdo principal com o SafeArea para evitar sobreposições.
            ft.SafeArea(
                content=view_content,
                expand=True
            )
        ],
        padding=0
    )