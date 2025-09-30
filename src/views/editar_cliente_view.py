# =================================================================================
# MÓDULO DA VIEW DE EDIÇÃO DE CLIENTE (editar_cliente_view.py)
#
# ATUALIZAÇÃO (Bug Fix & UX):
#   - Corrigido o erro de ciclo de vida movendo a atribuição de cores dos botões
#     para o método `did_mount`.
#   - Substituído o feedback por `CupertinoAlertDialog`.
# =================================================================================
import flet as ft
import logging
from src.viewmodels.editar_cliente_viewmodel import EditarClienteViewModel
from src.models.models import Cliente
from src.styles.style import AppDimensions, AppFonts


class EditarClienteView(ft.Column):
    def __init__(self, page: ft.Page, cliente_id: int):
        super().__init__()
        self.page = page
        self.view_model = EditarClienteViewModel(page, cliente_id)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount

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

        self._desativar_btn = ft.ElevatedButton("Desativar Cliente", icon=ft.Icons.DELETE_FOREVER,
                                                on_click=lambda _: self.view_model.solicitar_desativacao_cliente(), visible=False)
        self._ativar_btn = ft.ElevatedButton("Ativar Cliente", icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                                             on_click=lambda _: self.view_model.solicitar_ativacao_cliente(), visible=False)
        self._salvar_btn = ft.ElevatedButton(
            "Salvar Alterações", icon=ft.Icons.SAVE, on_click=self._on_salvar_click)

        # Diálogos de Confirmação são definidos aqui. Suas cores também serão ajustadas em did_mount.
        self._dlg_confirmar_desativacao = ft.CupertinoAlertDialog(title=ft.Text("Confirmar Desativação"), content=ft.Text("Tem certeza de que deseja desativar este cliente?"), actions=[ft.CupertinoDialogAction(
            "Cancelar", on_click=self.fechar_todos_os_modais), ft.CupertinoDialogAction("Sim, Desativar", is_destructive_action=True, on_click=self.view_model.confirmar_desativacao_cliente)])
        self._dlg_confirmar_ativacao = ft.CupertinoAlertDialog(title=ft.Text("Confirmar Ativação"), content=ft.Text("Tem certeza de que deseja reativar este cliente?"), actions=[
                                                               ft.CupertinoDialogAction("Cancelar", on_click=self.fechar_todos_os_modais), ft.CupertinoDialogAction("Sim, Ativar", on_click=self.view_model.confirmar_ativacao_cliente)])

        self.controls = [
            ft.Text("Editando Cliente", size=AppFonts.TITLE_MEDIUM,
                    weight=ft.FontWeight.BOLD),
            self._campo_nome, self._campo_telefone, self._campo_endereco, self._campo_email,
            ft.Row(
                [self._desativar_btn, self._ativar_btn,
                    ft.Container(expand=True), self._salvar_btn],
                width=AppDimensions.FIELD_WIDTH
            )
        ]

    def did_mount(self):
        logging.info(
            "EditarClienteView foi montada. Aplicando cores do tema e carregando dados.")
        if self.page.theme:
            self._desativar_btn.color = self.page.theme.color_scheme.on_error
            self._desativar_btn.bgcolor = self.page.theme.color_scheme.error
            self._ativar_btn.color = self.page.theme.color_scheme.on_primary
            self._ativar_btn.bgcolor = self.page.theme.color_scheme.primary
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
        novos_dados = {"nome": self._campo_nome.value, "telefone": self._campo_telefone.value,
                       "endereco": self._campo_endereco.value, "email": self._campo_email.value}
        self.view_model.salvar_alteracoes(novos_dados)

    def mostrar_dialogo_feedback(self, titulo: str, conteudo: str, on_ok_action):
        def fechar_dialogo_e_agir(e):
            dialog.open = False
            self.page.update()
            if on_ok_action:
                on_ok_action(e)
        dialog = ft.CupertinoAlertDialog(
            title=ft.Text(titulo), content=ft.Text(conteudo),
            actions=[ft.CupertinoDialogAction(
                "OK", on_click=fechar_dialogo_e_agir)],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def abrir_modal_confirmacao_desativar(self):
        self.page.overlay.append(self._dlg_confirmar_desativacao)
        self._dlg_confirmar_desativacao.open = True
        self.page.update()

    def abrir_modal_confirmacao_ativar(self):
        self.page.overlay.append(self._dlg_confirmar_ativacao)
        self._dlg_confirmar_ativacao.open = True
        self.page.update()

    def fechar_todos_os_modais(self, e=None):
        # Itera sobre a cópia da lista de overlays para remover os diálogos
        for dlg in self.page.overlay[:]:
            if isinstance(dlg, ft.CupertinoAlertDialog):
                dlg.open = False
        self.page.update()


def EditarClienteViewFactory(page: ft.Page, cliente_id: int) -> ft.View:
    return ft.View(
        route=f"/editar_cliente/{cliente_id}",
        appbar=ft.AppBar(
            title=ft.Text("Editar Cliente"), center_title=True,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go(
                "/gerir_clientes"), tooltip="Voltar para a Lista"),
            bgcolor=page.theme.color_scheme.surface,
        ),
        controls=[
            ft.SafeArea(
                content=ft.Container(content=EditarClienteView(
                    page, cliente_id), alignment=ft.alignment.center, expand=True),
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0
    )
