# =================================================================================
# MÓDULO DA VIEW DE CADASTRO DE CLIENTE (cadastro_cliente_view.py)
#
# ATUALIZAÇÃO (UX):
#   - Adicionado o método `mostrar_dialogo_feedback` para exibir um
#     CupertinoAlertDialog, tornando o feedback mais explícito e nativo.
#   - Garantido o uso de SafeArea na ViewFactory.
# =================================================================================
import flet as ft
from src.viewmodels.cadastro_cliente_viewmodel import CadastroClienteViewModel
from src.styles.style import AppDimensions, AppFonts


class CadastroClienteView(ft.Column):
    """
    A View para o formulário de cadastro de clientes. Agora como um componente de página.
    """

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = CadastroClienteViewModel(page)
        self.view_model.vincular_view(self)

        # --- Componentes Visuais do Formulário ---
        self._nome_field = ft.TextField(label="Nome do Cliente", width=AppDimensions.FIELD_WIDTH,
                                        autofocus=True, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._telefone_field = ft.TextField(label="Telefone", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(
            AppDimensions.BORDER_RADIUS), keyboard_type=ft.KeyboardType.PHONE)
        self._endereco_field = ft.TextField(
            label="Endereço", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._email_field = ft.TextField(label="Email (Opcional)", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(
            AppDimensions.BORDER_RADIUS), keyboard_type=ft.KeyboardType.EMAIL)

        # --- Estrutura da Página ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20
        self.controls = [
            ft.Text("Cadastro de Novo Cliente",
                    size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            self._nome_field, self._telefone_field, self._endereco_field, self._email_field,
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Cancelar", on_click=self.view_model.cancelar_cadastro),
                    ft.ElevatedButton(
                        "Salvar Cliente", icon=ft.Icons.SAVE_OUTLINED, on_click=self.view_model.salvar_cliente),
                ],
                alignment=ft.MainAxisAlignment.END, spacing=10, width=AppDimensions.FIELD_WIDTH
            )
        ]

    def obter_dados_formulario(self) -> dict:
        """Envia os dados dos campos para o ViewModel."""
        return {
            "nome": self._nome_field.value,
            "telefone": self._telefone_field.value,
            "endereco": self._endereco_field.value,
            "email": self._email_field.value,
        }

    # --- MÉTODO DE FEEDBACK COM DIÁLOGO CUPERTINO ---
    def mostrar_dialogo_feedback(self, titulo: str, conteudo: str, on_ok_action):
        """Exibe um CupertinoAlertDialog para feedback explícito ao usuário."""
        def fechar_dialogo_e_agir(e):
            # Fecha o diálogo na interface
            dialog.open = False
            self.page.update()
            # Se uma ação foi passada (como a navegação), executa-a.
            if on_ok_action:
                on_ok_action(e)

        dialog = ft.CupertinoAlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(conteudo),
            actions=[
                ft.CupertinoDialogAction("OK", on_click=fechar_dialogo_e_agir)
            ],
        )

        # O AlertDialog é adicionado ao `overlay` da página para ser exibido.
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()


def CadastroClienteViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa de Cadastro de Cliente para o roteador."""
    view_content = CadastroClienteView(page)
    appbar = ft.AppBar(
        title=ft.Text("Cadastrar Novo Cliente"), center_title=True,
        bgcolor=page.theme.color_scheme.surface,
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go(
                "/gerir_clientes"),
            tooltip="Voltar para a Lista de Clientes"
        )
    )
    return ft.View(
        route="/cadastro_cliente", appbar=appbar,
        controls=[
            ft.SafeArea(
                content=ft.Container(
                    content=view_content, alignment=ft.alignment.center, expand=True),
                expand=True
            )
        ],
        padding=0
    )
