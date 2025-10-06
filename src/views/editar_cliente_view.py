# =================================================================================
# MÓDULO DA VIEW DE EDIÇÃO DE CLIENTE (editar_cliente_view.py)
#
# ATUALIZAÇÃO (UX & Robustez):
#   - O método `mostrar_dialogo_feedback` agora aceita uma ação de callback
#     opcional para executar a navegação de forma segura após o fechamento
#     do diálogo, prevenindo travamentos.
# =================================================================================
import flet as ft
import logging
from src.viewmodels.editar_cliente_viewmodel import EditarClienteViewModel
from src.models.models import Cliente
from src.styles.style import AppDimensions, AppFonts
from threading import Timer
from typing import Callable, Optional # Importa Callable e Optional para a tipagem do callback

class EditarClienteView(ft.Column):
    def __init__(self, page: ft.Page, cliente_id: int):
        super().__init__()
        self.page = page
        self.view_model = EditarClienteViewModel(page, cliente_id)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount

        # Atributo para armazenar a ação de callback (navegação).
        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

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
            "Salvar Alterações", icon=ft.Icons.SAVE, on_click=self.on_salvar_click)
        self._cancelar_btn = ft.ElevatedButton(
            "Cancelar", on_click=lambda _: self.page.go("/gerir_clientes"))

        self._dlg_confirmar_desativacao = ft.AlertDialog(modal=True, title=ft.Text("Confirmar Desativação"), content=ft.Text("Tem certeza de que deseja desativar este cliente?"), actions=[ft.TextButton(
            "Cancelar", on_click=self.fechar_todos_os_modais), ft.ElevatedButton("Sim, Desativar", on_click=self.view_model.confirmar_desativacao_cliente)], actions_alignment=ft.MainAxisAlignment.END)
        self._dlg_confirmar_ativacao = ft.AlertDialog(modal=True, title=ft.Text("Confirmar Ativação"), content=ft.Text("Tem certeza de que deseja reativar este cliente?"), actions=[ft.TextButton(
            "Cancelar", on_click=self.fechar_todos_os_modais), ft.ElevatedButton("Sim, Ativar", on_click=self.view_model.confirmar_ativacao_cliente)], actions_alignment=ft.MainAxisAlignment.END)

        self.controls = [
            ft.Text("Editando Cliente", size=AppFonts.TITLE_MEDIUM,
                    weight=ft.FontWeight.BOLD),
            self._campo_nome, self._campo_telefone, self._campo_endereco, self._campo_email,
            ft.Row(
                [
                    self._desativar_btn,
                    self._ativar_btn,
                    self._cancelar_btn,
                    ft.Container(expand=True),
                    self._salvar_btn
                ],
                width=AppDimensions.FIELD_WIDTH
            )
        ]

    def did_mount(self):
        logging.info("EditarClienteView foi montada. Aplicando cores do tema e carregando dados.")
        # Aplica cores do tema aos botões de ação
        if self.page.theme:
            self._desativar_btn.bgcolor = self.page.theme.color_scheme.error
            self._ativar_btn.bgcolor = ft.colors.GREEN_700
            if self._dlg_confirmar_desativacao.actions:
                self._dlg_confirmar_desativacao.actions[1].bgcolor = self.page.theme.color_scheme.error
            if self._dlg_confirmar_ativacao.actions:
                self._dlg_confirmar_ativacao.actions[1].bgcolor = ft.colors.GREEN_700
        self.view_model.carregar_dados_cliente()

    def preencher_formulario(self, cliente: Cliente):
        self._campo_nome.value = cliente.nome or ""
        self._campo_telefone.value = cliente.telefone or ""
        self._campo_endereco.value = cliente.endereco or ""
        self._campo_email.value = cliente.email or ""
        self._desativar_btn.visible = cliente.ativo
        self._ativar_btn.visible = not cliente.ativo
        self.update()

    def on_salvar_click(self, e):
        novos_dados = {"nome": self._campo_nome.value, "telefone": self._campo_telefone.value,
                       "endereco": self._campo_endereco.value, "email": self._campo_email.value}
        self.view_model.salvar_alteracoes(novos_dados)

    def _fechar_dialogo_e_agir(self, e):
        """
        Fecha o diálogo e, se houver uma ação de callback, a executa com um atraso.
        """
        self.page.dialog.open = False
        self.page.update()
        if self._acao_pos_dialogo:
            # Usa um Timer para garantir que a UI processe o fechamento do diálogo antes da navegação
            t = Timer(0.1, self._acao_pos_dialogo)
            t.start()

    def mostrar_dialogo_feedback(self, titulo: str, conteudo: str, acao_callback: Optional[Callable[[], None]] = None):
        """
        Exibe um AlertDialog para feedback e armazena a ação de callback.
        """
        self._acao_pos_dialogo = acao_callback
        self.page.dialog = ft.AlertDialog(
            modal=True, title=ft.Text(titulo), content=ft.Text(conteudo),
            actions=[ft.TextButton(
                "OK", on_click=self._fechar_dialogo_e_agir)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

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