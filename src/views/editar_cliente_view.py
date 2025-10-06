# =================================================================================
# MÓDULO DA VIEW DE EDIÇÃO DE CLIENTE (editar_cliente_view.py)
#
# ATUALIZAÇÃO (UX & Robustez):
#   - Refatorado para usar `page.overlay` em vez de `page.dialog`, garantindo
#     a exibição estável dos diálogos.
#   - Unificados os múltiplos diálogos em um único `AlertDialog` genérico,
#     simplificando o código e a manutenção.
#   - Adicionados logs detalhados para depuração do ciclo de vida dos diálogos.
# =================================================================================
import flet as ft
import logging
from src.viewmodels.editar_cliente_viewmodel import EditarClienteViewModel
from src.models.models import Cliente
from src.styles.style import AppDimensions, AppFonts
from threading import Timer
from typing import Callable, Optional

# Configura um logger específico para esta view
logger = logging.getLogger(__name__)


class EditarClienteView(ft.Column):
    def __init__(self, page: ft.Page, cliente_id: int):
        super().__init__()
        self.page = page
        self.view_model = EditarClienteViewModel(page, cliente_id)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount

        # Atributo para armazenar a ação a ser executada após o fechamento do diálogo de feedback
        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

        # --- Layout da Coluna ---
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.CENTER
        self.spacing = 15

        logger.debug("View de Edição de Cliente: __init__ concluído.")

        # --- Componentes do Formulário ---
        self._campo_nome = ft.TextField(label="Nome", width=AppDimensions.FIELD_WIDTH,
                                        border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._campo_telefone = ft.TextField(
            label="Telefone", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._campo_endereco = ft.TextField(
            label="Endereço", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._campo_email = ft.TextField(label="Email", width=AppDimensions.FIELD_WIDTH,
                                         border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))

        # --- Botões de Ação ---
        self._desativar_btn = ft.ElevatedButton("Desativar Cliente", icon=ft.Icons.DELETE_FOREVER,
                                                on_click=lambda _: self.view_model.solicitar_desativacao_cliente(), visible=False)
        self._ativar_btn = ft.ElevatedButton("Ativar Cliente", icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                                             on_click=lambda _: self.view_model.solicitar_ativacao_cliente(), visible=False)
        self._salvar_btn = ft.ElevatedButton(
            "Salvar Alterações", icon=ft.Icons.SAVE, on_click=self.on_salvar_click)
        self._cancelar_btn = ft.ElevatedButton(
            "Cancelar", on_click=lambda _: self.page.go("/gerir_clientes"))

        # --- Diálogo Único e Reutilizável ---
        # Em vez de múltiplos diálogos, usamos um que será configurado dinamicamente
        self._dialogo_generico = ft.AlertDialog(
            modal=True,
            title=ft.Text(),
            content=ft.Text(),
            actions=[],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.controls = [
            ft.Text("Editando Cliente", size=AppFonts.TITLE_MEDIUM,
                    weight=ft.FontWeight.BOLD),
            self._campo_nome, self._campo_telefone, self._campo_endereco, self._campo_email,
            ft.Row(
                [self._desativar_btn, self._ativar_btn, self._cancelar_btn,
                    ft.Container(expand=True), self._salvar_btn],
                width=AppDimensions.FIELD_WIDTH
            )
        ]

    def did_mount(self):
        """Chamado pelo Flet quando a view é adicionada à página."""
        logger.info(
            f"View de Edição montada para cliente ID: {self.view_model.cliente_id}. Carregando dados...")
        self.view_model.carregar_dados_cliente()

    def preencher_formulario(self, cliente: Cliente):
        """Preenche os campos do formulário com os dados do cliente."""
        logger.debug(
            f"View: Preenchendo formulário com dados de '{cliente.nome}'.")
        self._campo_nome.value = cliente.nome or ""
        self._campo_telefone.value = cliente.telefone or ""
        self._campo_endereco.value = cliente.endereco or ""
        self._campo_email.value = cliente.email or ""

        # Atualiza a visibilidade dos botões de ativar/desativar
        self._desativar_btn.visible = cliente.ativo
        self._ativar_btn.visible = not cliente.ativo

        # Aplica cores do tema aos botões
        if self.page.theme:
            self._desativar_btn.bgcolor = self.page.theme.color_scheme.error
            self._ativar_btn.bgcolor = ft.Colors.GREEN_700

        logger.debug(
            f"View: Visibilidade dos botões - Ativar: {self._ativar_btn.visible}, Desativar: {self._desativar_btn.visible}.")
        self.update()

    def on_salvar_click(self, e):
        """Coleta os dados do formulário e os envia para o ViewModel."""
        logger.debug("View: Botão 'Salvar Alterações' clicado.")
        novos_dados = {
            "nome": self._campo_nome.value,
            "telefone": self._campo_telefone.value,
            "endereco": self._campo_endereco.value,
            "email": self._campo_email.value
        }
        self.view_model.salvar_alteracoes(novos_dados)

    # --- Métodos de Gerenciamento de Diálogos (Refatorados) ---

    def _fechar_dialogo_e_agir(self, e):
        """Fecha o diálogo de feedback e executa a ação de callback (navegação) com segurança."""
        logger.debug(
            "View: Fechando diálogo de feedback e agendando ação de callback (se houver).")
        self.fechar_dialogo()
        if self._acao_pos_dialogo:
            t = Timer(0.1, self._acao_pos_dialogo)
            t.start()
            logger.debug("View: Ação de callback (navegação) agendada.")

    def mostrar_dialogo_feedback(self, titulo: str, conteudo: str, acao_callback: Optional[Callable[[], None]] = None):
        """Exibe um diálogo de feedback simples (OK)."""
        logger.info(
            f"View: Exibindo diálogo de feedback - Título: '{titulo}'.")
        self._acao_pos_dialogo = acao_callback

        self._dialogo_generico.title.value = titulo
        self._dialogo_generico.content.value = conteudo
        self._dialogo_generico.actions = [
            ft.TextButton("OK", on_click=self._fechar_dialogo_e_agir)
        ]

        self.abrir_dialogo()

    def mostrar_dialogo_confirmacao(self, is_activating: bool):
        """Exibe um diálogo de confirmação para ativar ou desativar."""
        logger.info(
            f"View: Exibindo diálogo de confirmação para {'ATIVAÇÃO' if is_activating else 'DESATIVAÇÃO'}.")

        if is_activating:
            self._dialogo_generico.title.value = "Confirmar Ativação"
            self._dialogo_generico.content.value = "Tem certeza de que deseja reativar este cliente?"
            self._dialogo_generico.actions = [
                ft.TextButton("Cancelar", on_click=self.fechar_dialogo),
                ft.ElevatedButton("Sim, Ativar", on_click=lambda _: self.view_model.confirmar_ativacao_cliente(
                ), bgcolor=ft.Colors.GREEN_700)
            ]
        else:
            self._dialogo_generico.title.value = "Confirmar Desativação"
            self._dialogo_generico.content.value = "Tem certeza de que deseja desativar este cliente?"
            self._dialogo_generico.actions = [
                ft.TextButton("Cancelar", on_click=self.fechar_dialogo),
                ft.ElevatedButton("Sim, Desativar", on_click=lambda _: self.view_model.confirmar_desativacao_cliente(
                ), bgcolor=self.page.theme.color_scheme.error)
            ]

        self.abrir_dialogo()

    def abrir_dialogo(self):
        """Adiciona o diálogo à overlay e o abre (método centralizado)."""
        if self._dialogo_generico not in self.page.overlay:
            self.page.overlay.append(self._dialogo_generico)
            logger.debug("View: Diálogo adicionado à camada de overlay.")

        self._dialogo_generico.open = True
        self.page.update()
        logger.debug("View: Diálogo aberto e UI atualizada.")

    def fechar_dialogo(self, e=None):
        """Fecha o diálogo genérico."""
        if self._dialogo_generico in self.page.overlay:
            self._dialogo_generico.open = False
            self.page.update()
            logger.debug("View: Diálogo fechado e UI atualizada.")


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
