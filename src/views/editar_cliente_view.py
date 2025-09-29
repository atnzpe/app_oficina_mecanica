# =================================================================================
# MÓDULO DA VIEW DE EDIÇÃO DE CLIENTE (editar_cliente_view.py)
#
# ATUALIZAÇÃO (Layout Fix):
#   - Corrigido o layout da linha de botões para garantir que "Ativar" ou
#     "Desativar" sempre apareçam corretamente usando um spacer.
#   - Adicionado SafeArea na ViewFactory para garantir a responsividade em mobile.
# =================================================================================
import flet as ft
import logging
from src.viewmodels.editar_cliente_viewmodel import EditarClienteViewModel
from src.models.models import Cliente
from src.styles.style import AppDimensions, AppFonts


class EditarClienteView(ft.Column):
    """
    A View para o formulário de edição de clientes como uma página completa.
    """

    def __init__(self, page: ft.Page, cliente_id: int):
        super().__init__()
        self.page = page
        self.view_model = EditarClienteViewModel(page, cliente_id)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount

        # --- Componentes Visuais ---
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.CENTER
        self.spacing = 15

        self._campo_nome = ft.TextField(...)
        self._campo_telefone = ft.TextField(...)
        self._campo_endereco = ft.TextField(...)
        self._campo_email = ft.TextField(...)

        self._desativar_btn = ft.ElevatedButton(
            "Desativar Cliente",
            icon=ft.Icons.DELETE_FOREVER,
            color=self.page.theme.color_scheme.on_error,
            bgcolor=self.page.theme.color_scheme.error,
            on_click=lambda _: self.view_model.solicitar_desativacao_cliente(),
            visible=False
        )

        self._ativar_btn = ft.ElevatedButton(
            "Ativar Cliente",
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            color=self.page.theme.color_scheme.on_primary,
            bgcolor=self.page.theme.color_scheme.primary,
            on_click=lambda _: self.view_model.solicitar_ativacao_cliente(),
            visible=False
        )

        self._salvar_btn = ft.ElevatedButton(
            "Salvar Alterações", icon=ft.Icons.SAVE, on_click=self._on_salvar_click)

        # Diálogos de Confirmação (sem alterações)
        self._dlg_confirmar_desativacao = ft.AlertDialog(...)
        self._dlg_confirmar_ativacao = ft.AlertDialog(...)

        # --- Estrutura da View (com layout corrigido) ---
        self.controls = [
            ft.Text("Editando Cliente", size=AppFonts.TITLE_MEDIUM,
                    weight=ft.FontWeight.BOLD),
            self._campo_nome,
            self._campo_telefone,
            self._campo_endereco,
            self._campo_email,
            # --- LAYOUT CORRIGIDO ---
            # Usamos um Container com `expand=True` como um espaçador flexível.
            # Isso empurra os botões de estado (Ativar/Desativar) para a esquerda
            # e o botão de Salvar para a direita, de forma consistente.
            ft.Row(
                [
                    self._desativar_btn,
                    self._ativar_btn,
                    # Espaçador que empurra o botão Salvar
                    ft.Container(expand=True),
                    self._salvar_btn
                ],
                width=AppDimensions.FIELD_WIDTH
            )
        ]

    def did_mount(self):
        logging.info(
            "EditarClienteView foi montada. Carregando dados do cliente...")
        self.view_model.carregar_dados_cliente()

    def preencher_formulario(self, cliente: Cliente):
        self._campo_nome.value = cliente.nome or ""
        self._campo_telefone.value = cliente.telefone or ""
        self._campo_endereco.value = cliente.endereco or ""
        self._campo_email.value = cliente.email or ""
        self._desativar_btn.visible = cliente.ativo
        self._ativar_btn.visible = not cliente.ativo
        self.update()

    def _on_salvar_click(self, e):
        novos_dados = {
            "nome": self._campo_nome.value, "telefone": self._campo_telefone.value,
            "endereco": self._campo_endereco.value, "email": self._campo_email.value,
        }
        self.view_model.salvar_alteracoes(novos_dados)

    def abrir_modal_confirmacao_desativar(self):
        self.page.dialog = self._dlg_confirmar_desativacao
        self._dlg_confirmar_desativacao.open = True
        self.page.update()

    def abrir_modal_confirmacao_ativar(self):
        self.page.dialog = self._dlg_confirmar_ativacao
        self._dlg_confirmar_ativacao.open = True
        self.page.update()

    def fechar_todos_os_modais(self, e=None):
        if self.page.dialog:
            self.page.dialog.open = False
        self.page.update()

    def mostrar_feedback(self, mensagem: str, success: bool):
        self.page.snack_bar = ft.SnackBar(...)
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
                icon=ft.Icons.ARROW_BACK_IOS_NEW,
                on_click=lambda _: page.go("/gerir_clientes"),
                tooltip="Voltar para a Lista"
            ),
            bgcolor=page.theme.color_scheme.surface,
        ),
        controls=[
            # --- SAFEAREA APLICADO ---
            ft.SafeArea(
                content=ft.Container(
                    content=EditarClienteView(page, cliente_id),
                    alignment=ft.alignment.center,
                    expand=True
                ),
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0  # Padding é zerado para o SafeArea controlar
    )
