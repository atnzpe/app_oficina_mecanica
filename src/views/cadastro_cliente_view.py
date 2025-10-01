# =================================================================================
# MÓDULO DA VIEW DE CADASTRO DE CLIENTE (cadastro_cliente_view.py)
#
# ATUALIZAÇÃO (Bug Fix Final):
#   - Corrigido o fluxo de navegação pós-diálogo usando um Timer para
#     evitar conflitos de renderização e a "tela em branco".
# =================================================================================
import flet as ft
from src.viewmodels.cadastro_cliente_viewmodel import CadastroClienteViewModel
from src.styles.style import AppDimensions, AppFonts
from threading import Timer # Importa o Timer para agendar a navegação

class CadastroClienteView(ft.Column):
    """
    A View para o formulário de cadastro de clientes.
    """
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = CadastroClienteViewModel(page)
        self.view_model.vincular_view(self)

        # --- Componentes Visuais do Formulário ---
        self._nome_field = ft.TextField(label="Nome do Cliente", width=AppDimensions.FIELD_WIDTH, autofocus=True, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._telefone_field = ft.TextField(label="Telefone", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS), keyboard_type=ft.KeyboardType.PHONE)
        self._endereco_field = ft.TextField(label="Endereço", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._email_field = ft.TextField(label="Email (Opcional)", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS), keyboard_type=ft.KeyboardType.EMAIL)

        # --- Estrutura da Página ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20
        self.controls = [
            ft.Text("Cadastro de Novo Cliente", size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            self._nome_field, self._telefone_field, self._endereco_field, self._email_field,
            ft.Row(
                [
                    ft.ElevatedButton("Cancelar", on_click=self.view_model.cancelar_cadastro),
                    ft.ElevatedButton("Salvar Cliente", icon=ft.Icons.SAVE_OUTLINED, on_click=self.view_model.salvar_cliente),
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

    def _fechar_dialogo_e_agir(self, e):
        """
        Fecha o diálogo e, em seguida, agenda a ação de callback (navegação)
        para ocorrer após um pequeno atraso, evitando conflitos de renderização.
        """
        # 1. Fecha o diálogo e atualiza a UI imediatamente.
        self.page.dialog.open = False
        self.page.update()

        # 2. Se houver uma ação de navegação, agenda sua execução.
        
            # Atraso de 0.1 segundos é suficiente para a UI processar o fechamento do diálogo.
        t = Timer(0.1, lambda: self.page.go("/gerir_clientes"))
        t.start()

    def mostrar_dialogo_feedback(self, titulo: str, conteudo: str):
        """Exibe um AlertDialog para feedback explícito ao usuário."""
        
        # Atribui o diálogo à propriedade `dialog` da página.
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo),
            content=ft.Text(conteudo),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self._fechar_dialogo_e_agir(e))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog.open = True
        self.page.update()

def CadastroClienteViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa de Cadastro de Cliente para o roteador."""
    view_content = CadastroClienteView(page)
    appbar = ft.AppBar(
        title=ft.Text("Cadastrar Novo Cliente"), center_title=True,
        bgcolor=page.theme.color_scheme.surface,
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go("/gerir_clientes"),
            tooltip="Voltar para a Lista de Clientes"
        )
    )
    return ft.View(
        route="/cadastro_cliente", appbar=appbar,
        controls=[
            ft.SafeArea(
                content=ft.Container(content=view_content, alignment=ft.alignment.center, expand=True),
                expand=True
            )
        ],
        padding=0
    )