
# =================================================================================
# MÓDULO DA VIEW DE ONBOARDING DE CLIENTE (onboarding_cliente_view.py)
#
# OBJETIVO: Criar uma tela de boas-vindas para o primeiro cadastro de cliente.
# ARQUITETURA: Esta View REUTILIZA o `CadastroClienteViewModel` para evitar
#              duplicação de código, já que a lógica de salvar é idêntica.
# =================================================================================
import flet as ft
# Reutilizamos o ViewModel já existente, pois a lógica de negócio é a mesma.
from src.viewmodels.cadastro_cliente_viewmodel import CadastroClienteViewModel
from src.styles.style import AppDimensions


class OnboardingClienteView(ft.Column):
    """
    O conteúdo da página de onboarding do primeiro cliente.
    """

    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page
        # A View de Onboarding usa o mesmo ViewModel da View de Cadastro padrão.
        self.view_model = CadastroClienteViewModel(page)
        self.view_model.vincular_view(self)

        # --- Componentes Visuais (idênticos ao de cadastro, mas com textos diferentes) ---
        self._nome_field = ft.TextField(
            label="Nome do Cliente", width=AppDimensions.FIELD_WIDTH, autofocus=True)
        self._telefone_field = ft.TextField(
            label="Telefone", width=AppDimensions.FIELD_WIDTH)
        self._endereco_field = ft.TextField(
            label="Endereço", width=AppDimensions.FIELD_WIDTH)
        self._email_field = ft.TextField(
            label="Email", width=AppDimensions.FIELD_WIDTH)

        # --- Estrutura da Página ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20
        self.controls = [
            ft.Icon(ft.Icons.GROUP_ADD, size=40, color=ft.Colors.PRIMARY),
            ft.Text("Bem-vindo ao Sistema de Oficina!",
                    size=30, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Parece que você ainda não possui clientes. Vamos cadastrar o primeiro?"),
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            self._nome_field,
            self._telefone_field,
            self._endereco_field,
            self._email_field,
            ft.Row(
                [
                    # O botão Salvar delega a ação para o ViewModel reutilizado.
                    ft.ElevatedButton(
                        "Salvar Cliente e Continuar", on_click=self.view_model.salvar_cliente, icon=ft.Icons.SAVE),
                ],
                alignment=ft.MainAxisAlignment.END
            )
        ]

    def obter_dados_formulario(self) -> dict:
        """Fornece os dados dos campos para o ViewModel."""
        return {
            "nome": self._nome_field.value,
            "telefone": self._telefone_field.value,
            "endereco": self._endereco_field.value,
            "email": self._email_field.value,
        }

    def mostrar_feedback(self, mensagem: str, sucesso: bool):
        """Exibe uma SnackBar para feedback ao usuário."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700
        )
        self.page.snack_bar.open = True
        self.page.update()


def OnboardingClienteViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa de Onboarding de Cliente para o roteador."""
    view_content = OnboardingClienteView(page)

    # Esta tela não terá uma AppBar para dar uma sensação mais imersiva de "primeiro passo".
    return ft.View(
        route="/onboarding_cliente",
        controls=[
            ft.Container(
                content=view_content,
                alignment=ft.alignment.center,
                expand=True
            )
        ],
        padding=10
    )
