# =================================================================================
# MÓDULO DA VIEW DE CADASTRO DE CLIENTE (cadastro_cliente_view.py)
#
# REATORAÇÃO:
#   - A View foi transformada de um gerenciador de AlertDialog para um componente
#     de página completa (ft.Column).
#   - Foi criada a `CadastroClienteViewFactory` para construir o `ft.View`
#     completo que será usado pelo roteador em main.py.
#   - Integrado o `style.py` para padronização da UI.
# =================================================================================
import flet as ft
from src.viewmodels.cadastro_cliente_viewmodel import CadastroClienteViewModel
# Importa as classes de estilo para fontes e dimensões.
from src.styles.style import AppDimensions, AppFonts


class CadastroClienteView(ft.Column):
    """
    A View para o formulário de cadastro de clientes. Agora como um componente de página.
    """

    def __init__(self, page: ft.Page):
        # 1. Chamada ao construtor da classe pai (ft.Column).
        super().__init__()

        # 2. Referências e instanciação do ViewModel.
        self.page = page
        self.view_model = CadastroClienteViewModel(page)
        self.view_model.vincular_view(self)

        # --- Componentes Visuais do Formulário ---
        # Todos os campos agora usam as dimensões e raios de borda padronizados.
        self._nome_field = ft.TextField(
            label="Nome do Cliente",
            width=AppDimensions.FIELD_WIDTH,
            autofocus=True,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS)
        )
        self._telefone_field = ft.TextField(
            label="Telefone",
            width=AppDimensions.FIELD_WIDTH,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
            keyboard_type=ft.KeyboardType.PHONE
        )
        self._endereco_field = ft.TextField(
            label="Endereço",
            width=AppDimensions.FIELD_WIDTH,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS)
        )
        self._email_field = ft.TextField(
            label="Email",
            width=AppDimensions.FIELD_WIDTH,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
            keyboard_type=ft.KeyboardType.EMAIL
        )

        # --- Estrutura da Página ---
        # Define o alinhamento e a distribuição dos controles na tela.
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20
        # A lista de controles que compõem a view.
        self.controls = [
            # Título da página, utilizando a fonte padrão para títulos.
            ft.Text("Cadastro de Novo Cliente",
                    size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            self._nome_field,
            self._telefone_field,
            self._endereco_field,
            self._email_field,
            # Linha para agrupar os botões de ação.
            ft.Row(
                [
                    # Botão para cancelar a operação.
                    ft.ElevatedButton("Cancelar", on_click=self.view_model.cancelar_cadastro,
                                      # As cores devem vir do tema para bom contraste.
                                      # Exemplo de como usar cores do tema:
                                      # color=self.page.theme.color_scheme.on_error,
                                      # bgcolor=self.page.theme.color_scheme.error
                                      ),
                    # Botão para salvar, delega a ação para o ViewModel.
                    ft.ElevatedButton(
                        "Salvar Cliente",
                        icon=ft.Icons.SAVE_OUTLINED,
                        on_click=self.view_model.salvar_cliente),
                ],
                # Alinha os botões à direita.
                alignment=ft.MainAxisAlignment.END,
                spacing=10
            )
        ]

    def obter_dados_formulario(self) -> dict:
        """
        Envia os dados dos campos para o ViewModel.
        Este método não sofreu alterações.
        """
        return {
            "nome": self._nome_field.value,
            "telefone": self._telefone_field.value,
            "endereco": self._endereco_field.value,
            "email": self._email_field.value,
        }

    def mostrar_feedback(self, mensagem: str, sucesso: bool):
        """
        Exibe uma SnackBar para feedback ao usuário.
        Este método é chamado pelo ViewModel.
        """
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            # As cores de sucesso e erro são obtidas do tema para consistência.
            bgcolor=self.page.theme.color_scheme.primary if sucesso else self.page.theme.color_scheme.error
        )
        self.page.snack_bar.open = True
        self.page.update()

# --- NOVA FACTORY ---


def CadastroClienteViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa de Cadastro de Cliente para o roteador."""
    view_content = CadastroClienteView(page)

    # Cria a AppBar (barra de título) da página.
    appbar = ft.AppBar(
        title=ft.Text("Cadastrar Novo Cliente"),
        center_title=True,
        # A cor de fundo é a cor de superfície do tema atual.
        bgcolor=page.theme.color_scheme.surface,
        # Adiciona um botão de "voltar" à esquerda.
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_IOS_NEW,
            on_click=lambda _: page.go("/dashboard"),
            tooltip="Voltar ao Dashboard"
        )
    )

    return ft.View(
        route="/cadastro_cliente",
        appbar=appbar,
        controls=[
            # Garante que o conteúdo não sobreponha barras de status do sistema.
            ft.SafeArea(
                content=ft.Container(
                    content=view_content,
                    alignment=ft.alignment.center,
                    expand=True
                ),
                expand=True
            )
        ],
        # Remove o padding da View para o SafeArea gerenciar o espaçamento.
        padding=0
    )
