# =================================================================================
# MÓDULO DA VIEW DE CADASTRO DE CLIENTE (cadastro_cliente_view.py)
#
# REATORAÇÃO:
#   - A View foi transformada de um gerenciador de AlertDialog para um componente
#     de página completa (ft.Column).
#   - Foi criada a `CadastroClienteViewFactory` para construir o `ft.View`
#     completo que será usado pelo roteador em main.py.
# =================================================================================
import flet as ft
from src.viewmodels.cadastro_cliente_viewmodel import CadastroClienteViewModel
from src.styles.style import AppDimensions

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
        # A definição dos campos permanece a mesma.
        self._nome_field = ft.TextField(label="Nome", width=AppDimensions.FIELD_WIDTH, autofocus=True)
        self._telefone_field = ft.TextField(label="Telefone", width=AppDimensions.FIELD_WIDTH)
        self._endereco_field = ft.TextField(label="Endereço", width=AppDimensions.FIELD_WIDTH)
        self._email_field = ft.TextField(label="Email", width=AppDimensions.FIELD_WIDTH)

        # --- Estrutura da Página ---
        # Define o alinhamento e a distribuição dos controles na tela.
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20
        # Os controles agora são os campos do formulário e os botões.
        self.controls = [
            ft.Text("Cadastro de Novo Cliente", size=30, weight=ft.FontWeight.BOLD),
            self._nome_field,
            self._telefone_field,
            self._endereco_field,
            self._email_field,
            ft.Row(
                [
                    # O botão Cancelar agora chama um método no ViewModel para navegar.
                    ft.ElevatedButton("Cancelar", on_click=self.view_model.cancelar_cadastro, color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_700),
                    # O botão Salvar continua delegando a ação para o ViewModel.
                    ft.ElevatedButton("Salvar", on_click=self.view_model.salvar_cliente),
                ],
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
            bgcolor=ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700
        )
        self.page.snack_bar.open = True
        self.page.update()

# --- NOVA FACTORY ---
def CadastroClienteViewFactory(page: ft.Page) -> ft.View:
    """
    Cria a View completa de Cadastro de Cliente para o roteador.
    """
    # 1. Cria o conteúdo principal da página.
    view_content = CadastroClienteView(page)
    
    # 2. Cria a AppBar (barra de título).
    appbar = ft.AppBar(
        title=ft.Text("Cadastrar Novo Cliente"),
        center_title=True,
        bgcolor=ft.Colors.SURFACE,
        # Adiciona um botão de voltar que também usa o sistema de rotas.
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda _: page.go("/dashboard"),
            tooltip="Voltar ao Dashboard"
        )
    )
    
    # 3. Retorna o objeto ft.View, que representa a tela inteira.
    return ft.View(
        route="/cadastro_cliente",
        controls=[
            # Coloca o conteúdo dentro de um container para centralizar na tela.
            ft.Container(
                content=view_content,
                alignment=ft.alignment.center,
                expand=True
            )
        ],
        appbar=appbar,
        padding=10
    )
