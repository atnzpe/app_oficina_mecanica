# =================================================================================
# MÓDULO DA VIEW DE EDIÇÃO DE CLIENTE (editar_cliente_view.py)
#
# ATUALIZAÇÃO (CRUD Cliente):
#   - Adicionado um botão "Ativar Cliente" que é exibido dinamicamente.
#   - A view agora mostra "Ativar" ou "Desativar" com base no status do cliente.
#   - Adicionado um diálogo de confirmação para a ação de ativar.
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

        self._campo_nome = ft.TextField(label="Nome", width=AppDimensions.FIELD_WIDTH,
                                        border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._campo_telefone = ft.TextField(
            label="Telefone", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._campo_endereco = ft.TextField(
            label="Endereço", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._campo_email = ft.TextField(label="Email", width=AppDimensions.FIELD_WIDTH,
                                         border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))

        # --- BOTÃO DE DESATIVAR ---
        # Fica invisível por padrão. Será exibido apenas para clientes ativos.
        self._desativar_btn = ft.ElevatedButton(
            "Desativar Cliente",
            icon=ft.Icons.DELETE_FOREVER,
            color=self.page.theme.color_scheme.on_error,
            bgcolor=self.page.theme.color_scheme.error,
            on_click=lambda _: self.view_model.solicitar_desativacao_cliente(),
            visible=False
        )

        # --- NOVO BOTÃO DE ATIVAR ---
        # Fica invisível por padrão. Será exibido apenas para clientes inativos.
        self._ativar_btn = ft.ElevatedButton(
            "Ativar Cliente",
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            color=self.page.theme.color_scheme.on_primary,
            # Usando a cor primária para destacar a ação positiva.
            bgcolor=self.page.theme.color_scheme.primary,
            on_click=lambda _: self.view_model.solicitar_ativacao_cliente(),
            visible=False
        )

        self._salvar_btn = ft.ElevatedButton(
            "Salvar Alterações", icon=ft.Icons.SAVE, on_click=self._on_salvar_click)

        # --- Diálogos de Confirmação ---
        self._dlg_confirmar_desativacao = ft.AlertDialog(
            modal=True, title=ft.Text("Confirmar Desativação"),
            content=ft.Text(
                "Tem certeza de que deseja desativar este cliente?"),
            actions=[
                ft.TextButton(
                    "Cancelar", on_click=self.fechar_todos_os_modais),
                ft.ElevatedButton("Sim, Desativar", on_click=self.view_model.confirmar_desativacao_cliente,
                                  bgcolor=self.page.theme.color_scheme.error),
            ], actions_alignment=ft.MainAxisAlignment.END
        )

        # --- NOVO DIÁLOGO DE ATIVAÇÃO ---
        self._dlg_confirmar_ativacao = ft.AlertDialog(
            modal=True, title=ft.Text("Confirmar Ativação"),
            content=ft.Text(
                "Tem certeza de que deseja reativar este cliente?"),
            actions=[
                ft.TextButton(
                    "Cancelar", on_click=self.fechar_todos_os_modais),
                ft.ElevatedButton(
                    "Sim, Ativar", on_click=self.view_model.confirmar_ativacao_cliente),
            ], actions_alignment=ft.MainAxisAlignment.END
        )

        # --- Estrutura da View ---
        self.controls = [
            ft.Text("Editando Cliente", size=AppFonts.TITLE_MEDIUM,
                    weight=ft.FontWeight.BOLD),
            self._campo_nome,
            self._campo_telefone,
            self._campo_endereco,
            self._campo_email,
            ft.Row(
                # Adiciona ambos os botões ao Row. A visibilidade controlará qual aparece.
                [self._desativar_btn, self._ativar_btn, self._salvar_btn],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                width=AppDimensions.FIELD_WIDTH
            )
        ]

    def did_mount(self):
        logging.info(
            "EditarClienteView foi montada. Carregando dados do cliente...")
        self.view_model.carregar_dados_cliente()

    def preencher_formulario(self, cliente: Cliente):
        """Preenche os campos e controla a visibilidade dos botões Ativar/Desativar."""
        self._campo_nome.value = cliente.nome or ""
        self._campo_telefone.value = cliente.telefone or ""
        self._campo_endereco.value = cliente.endereco or ""
        self._campo_email.value = cliente.email or ""

        # --- LÓGICA DE VISIBILIDADE DOS BOTÕES ---
        # Se o cliente estiver ativo, mostra o botão de desativar.
        # Se estiver inativo, mostra o botão de ativar.
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

    # --- NOVO MÉTODO PARA ABRIR MODAL DE ATIVAÇÃO ---
    def abrir_modal_confirmacao_ativar(self):
        self.page.dialog = self._dlg_confirmar_ativacao
        self._dlg_confirmar_ativacao.open = True
        self.page.update()

    def fechar_todos_os_modais(self, e=None):
        """Fecha qualquer modal de confirmação aberto por esta view."""
        # Fecha ambos os diálogos, se estiverem abertos.
        if self.page.dialog:
            self.page.dialog.open = False
        self.page.update()

    def mostrar_feedback(self, mensagem: str, success: bool):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=self.page.theme.color_scheme.primary if success else self.page.theme.color_scheme.error
        )
        self.page.snack_bar.open = True
        self.page.update()


def EditarClienteViewFactory(page: ft.Page, cliente_id: int) -> ft.View:
    return ft.View(
        route=f"/editar_cliente/{cliente_id}",
        appbar=ft.AppBar(
            title=ft.Text("Editar Cliente"), center_title=True,
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go(
                    "/gerir_clientes"),
                tooltip="Voltar para a Lista"
            ),
            bgcolor=page.theme.color_scheme.surface,
        ),
        controls=[
            ft.Container(
                content=EditarClienteView(page, cliente_id),
                alignment=ft.alignment.center, expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=AppDimensions.PAGE_PADDING
    )
