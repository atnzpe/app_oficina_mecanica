# =================================================================================
# MÓDULO DA VIEW DE ENTRADA DE PEÇAS (entrada_pecas_view.py)
#
# OBJETIVO: Criar o formulário para registrar a entrada de peças (Issue #32).
# =================================================================================
import flet as ft
import logging
from src.viewmodels.entrada_pecas_viewmodel import EntradaPecasViewModel
from src.models.models import Peca
from src.styles.style import AppDimensions, AppFonts
from typing import Callable, Optional, List
from threading import Timer

logger = logging.getLogger(__name__)


class EntradaPecasView(ft.Column):
    """
    A View para o formulário de Entrada de Peças.
    """

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = EntradaPecasViewModel(page)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount
        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

        # --- Layout ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 15

        # --- Componentes do Formulário ---
        self._peca_dropdown = ft.Dropdown(
            label="Selecione a Peça*",
            width=AppDimensions.FIELD_WIDTH,
            border_radius=AppDimensions.BORDER_RADIUS,
            hint_text="Digite para pesquisar a peça"
        )
        self._quantidade_field = ft.TextField(
            label="Quantidade de Entrada*",
            width=AppDimensions.FIELD_WIDTH,
            border_radius=AppDimensions.BORDER_RADIUS,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        self._valor_custo_field = ft.TextField(
            label="Valor de Custo Total (Opcional)",
            width=AppDimensions.FIELD_WIDTH,
            border_radius=AppDimensions.BORDER_RADIUS,
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_text="R$ "
        )
        self._descricao_field = ft.TextField(
            label="Descrição (Opcional)",
            hint_text="Ex: NF 12345, Compra avulsa",
            width=AppDimensions.FIELD_WIDTH,
            border_radius=AppDimensions.BORDER_RADIUS
        )

        self._dialogo_feedback = ft.AlertDialog(
            modal=True, title=ft.Text(), content=ft.Text(), actions=[])

        self.controls = [
            ft.Text("Registrar Entrada de Peças",
                    size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            self._peca_dropdown,
            self._quantidade_field,
            self._valor_custo_field,
            self._descricao_field,
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Cancelar", on_click=self.view_model.cancelar),
                    ft.ElevatedButton("Registrar Entrada", icon=ft.Icons.SAVE,
                                      on_click=lambda _: self.view_model.registrar_entrada()),
                ],
                alignment=ft.MainAxisAlignment.END, width=AppDimensions.FIELD_WIDTH, spacing=10
            )
        ]

    def did_mount(self):
        """Chamado pelo Flet quando a view é montada."""
        logger.debug("View 'Entrada de Peças' montada. Carregando peças...")
        self.view_model.carregar_pecas_ativas()

    def popular_dropdown_pecas(self, pecas: List[Peca]):
        """Preenche o dropdown com a lista de peças ativas."""
        self._peca_dropdown.options = [
            ft.dropdown.Option(
                key=peca.id, text=f"{peca.nome} (Ref: {peca.referencia})")
            for peca in pecas
        ]
        self.update()

    def obter_dados_formulario(self) -> dict:
        """Coleta, converte e retorna os dados do formulário."""
        peca_id = int(
            self._peca_dropdown.value) if self._peca_dropdown.value else None

        try:
            quantidade = int(
                self._quantidade_field.value) if self._quantidade_field.value else 0
        except (ValueError, TypeError):
            quantidade = None  # Sinaliza erro de tipo

        try:
            valor_custo = float(self._valor_custo_field.value.replace(
                ",", ".")) if self._valor_custo_field.value else None
        except (ValueError, TypeError):
            valor_custo = -1  # Sinaliza erro de tipo (diferente de None)

        return {
            "peca_id": peca_id,
            "quantidade": quantidade,
            "valor_custo": valor_custo,
            "descricao": self._descricao_field.value,
        }

    def limpar_formulario(self):
        """Limpa todos os campos do formulário após o sucesso."""
        logger.debug("View: Limpando formulário de entrada de peças.")
        self._peca_dropdown.value = None
        self._quantidade_field.value = ""
        self._valor_custo_field.value = ""
        self._descricao_field.value = ""
        self.update()

    # --- Métodos de Diálogo (Padrão com Overlay) ---
    def _fechar_dialogo_e_agir(self, e):
        self.fechar_dialogo()
        if self._acao_pos_dialogo:
            Timer(0.1, self._acao_pos_dialogo).start()

    def mostrar_dialogo_feedback(self, titulo: str, conteudo: str, acao_callback: Optional[Callable[[], None]] = None):
        self._acao_pos_dialogo = acao_callback
        self._dialogo_feedback.title.value = titulo
        self._dialogo_feedback.content.value = conteudo
        self._dialogo_feedback.actions = [ft.TextButton(
            "OK", on_click=self._fechar_dialogo_e_agir)]
        if self._dialogo_feedback not in self.page.overlay:
            self.page.overlay.append(self._dialogo_feedback)
        self._dialogo_feedback.open = True
        self.page.update()

    def fechar_dialogo(self, e=None):
        if self._dialogo_feedback in self.page.overlay:
            self._dialogo_feedback.open = False
            self.page.update()


def EntradaPecasViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa de Entrada de Peças para o roteador."""
    return ft.View(
        route="/entrada_pecas",
        appbar=ft.AppBar(
            title=ft.Text("Entrada de Peças no Estoque"), center_title=True,
            bgcolor=page.theme.color_scheme.surface,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go(
                "/dashboard"), tooltip="Voltar ao Dashboard")
        ),
        controls=[ft.SafeArea(content=ft.Container(content=EntradaPecasView(
            page), alignment=ft.alignment.center, expand=True), expand=True)],
        padding=0
    )
