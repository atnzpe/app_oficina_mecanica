
# =================================================================================
# MÓDULO DA VIEW DE EDIÇÃO DE CLIENTE (editar_cliente_view.py)
#
# REATORAÇÃO (CRUD):
#   - A View foi transformada em uma tela completa, controlada pela rota
#     /editar_cliente/:id, substituindo o antigo sistema de modais.
# =================================================================================
import flet as ft
from src.viewmodels.editar_cliente_viewmodel import EditarClienteViewModel
from src.models.models import Cliente
from src.styles.style import AppDimensions

class EditarClienteView(ft.Column):
    """
    A View para o formulário de edição de clientes como uma página completa.
    """
    def __init__(self, page: ft.Page, cliente_id: int):
        super().__init__()
        self.page = page
        self.view_model = EditarClienteViewModel(page, cliente_id)
        self.view_model.vincular_view(self)

        # --- Componentes Visuais ---
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.CENTER
        self.spacing = 15

        self._campo_nome = ft.TextField(label="Nome", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._campo_telefone = ft.TextField(label="Telefone", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._campo_endereco = ft.TextField(label="Endereço", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._campo_email = ft.TextField(label="Email", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)

        self._desativar_btn = ft.ElevatedButton(
            "Desativar Cliente",
            icon=ft.Icons.DELETE_FOREVER,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_700,
            on_click=lambda _: self.view_model.solicitar_desativacao_cliente()
        )
        self._salvar_btn = ft.ElevatedButton("Salvar Alterações", icon=ft.Icons.SAVE, on_click=self._on_salvar_click)
        
        self._dlg_confirmar_desativacao = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Ação"),
            content=ft.Text("Tem certeza de que deseja desativar este cliente? Esta ação o removerá das listas ativas."),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_todos_os_modais),
                ft.ElevatedButton(
                    "Sim, Desativar", 
                    on_click=self.view_model.confirmar_desativacao_cliente,
                    bgcolor=ft.Colors.RED_700
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        # --- Estrutura da View ---
        self.controls = [
            ft.Text("Editando Cliente", size=30, weight=ft.FontWeight.BOLD),
            self._campo_nome,
            self._campo_telefone,
            self._campo_endereco,
            self._campo_email,
            ft.Row(
                [self._desativar_btn, self._salvar_btn],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                width=AppDimensions.FIELD_WIDTH
            )
        ]
        
        # Comanda o ViewModel para carregar os dados do cliente assim que a view for criada.
        self.view_model.carregar_dados_cliente()

    def preencher_formulario(self, cliente: Cliente):
        """Preenche os campos do formulário com os dados do cliente."""
        self._campo_nome.value = cliente.nome
        self._campo_telefone.value = cliente.telefone
        self._campo_endereco.value = cliente.endereco
        self._campo_email.value = cliente.email
        self.update()

    def _on_salvar_click(self, e):
        """Coleta os dados do formulário e os envia ao ViewModel para salvar."""
        novos_dados = {
            "nome": self._campo_nome.value,
            "telefone": self._campo_telefone.value,
            "endereco": self._campo_endereco.value,
            "email": self._campo_email.value,
        }
        self.view_model.salvar_alteracoes(novos_dados)

    def abrir_modal_confirmacao_desativar(self):
        """Abre o diálogo de confirmação para desativar o cliente."""
        self.page.dialog = self._dlg_confirmar_desativacao
        self._dlg_confirmar_desativacao.open = True
        self.page.update()

    def fechar_todos_os_modais(self, e=None):
        """Fecha qualquer modal aberto por esta view."""
        if self.page.dialog == self._dlg_confirmar_desativacao:
            self.page.dialog.open = False
            self.page.update()

    def mostrar_feedback(self, mensagem: str, success: bool):
        """Exibe uma SnackBar para feedback ao usuário."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=ft.Colors.GREEN_700 if success else ft.Colors.RED_700
        )
        self.page.snack_bar.open = True
        self.page.update()

def EditarClienteViewFactory(page: ft.Page, cliente_id: int) -> ft.View:
    """Cria a View completa para a rota /editar_cliente/:id."""
    return ft.View(
        route=f"/editar_cliente/{cliente_id}",
        appbar=ft.AppBar(
            title=ft.Text("Editar Cliente"),
            center_title=True,
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda _: page.go("/gerir_clientes"),
                tooltip="Voltar para a Lista"
            ),
        ),
        controls=[
            ft.Container(
                content=EditarClienteView(page, cliente_id),
                alignment=ft.alignment.center,
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=20
    )