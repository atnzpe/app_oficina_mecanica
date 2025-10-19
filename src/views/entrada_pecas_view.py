# =================================================================================
# MÓDULO DA VIEW DE ENTRADA DE PEÇAS (entrada_pecas_view.py)
#
# ATUALIZAÇÃO (Issue #32 - Lote):
#   - UI refatorada para suportar a adição de múltiplos itens.
#   - Adicionado um ListView para mostrar os itens no lote.
# =================================================================================
import flet as ft
import logging
from src.viewmodels.entrada_pecas_viewmodel import EntradaPecasViewModel
from src.models.models import Peca
from src.styles.style import AppDimensions, AppFonts
from typing import Callable, Optional, List, Dict, Any
from threading import Timer

logger = logging.getLogger(__name__)


class EntradaPecasView(ft.Column):
    """
    A View para o formulário de Entrada de Peças em Lote.
    """

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = EntradaPecasViewModel(page)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount
        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

        # --- Layout ---
        self.alignment = ft.MainAxisAlignment.START  # Alinha ao topo
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 15
        self.scroll = ft.ScrollMode.ADAPTIVE  # Permite rolagem da página inteira

        # --- Componentes do Formulário (Item Único) ---
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
            hint_text="Ex: NF 12345",
            width=AppDimensions.FIELD_WIDTH,
            border_radius=AppDimensions.BORDER_RADIUS
        )
        self._add_item_button = ft.ElevatedButton(
            "Adicionar à Lista",
            icon=ft.Icons.ADD_SHOPPING_CART,
            on_click=lambda _: self.view_model.adicionar_item_ao_lote(),
            width=AppDimensions.FIELD_WIDTH
        )

        # --- Componente da Lista (Lote) ---
        self._lote_list_view = ft.ListView(expand=True, spacing=5, padding=10)

        # --- Botões de Ação Principais ---
        self._registrar_lote_button = ft.ElevatedButton(
            "Registrar Lote de Entrada",
            icon=ft.Icons.SAVE,
            on_click=lambda _: self.view_model.registrar_lote_entrada(),
        )
        self._cancelar_button = ft.ElevatedButton(
            "Cancelar",
            on_click=self.view_model.cancelar
        )

        self._dialogo_feedback = ft.AlertDialog(
            modal=True, title=ft.Text(), content=ft.Text(), actions=[])

        # --- Estrutura da View ---
        self.controls = [
            ft.Text("Registrar Entrada de Peças",
                    size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),

            ft.Divider(),
            ft.Text("Adicionar Item ao Lote", size=AppFonts.BODY_LARGE),
            self._peca_dropdown,
            self._quantidade_field,
            self._valor_custo_field,
            self._descricao_field,
            self._add_item_button,

            ft.Divider(),
            ft.Text("Itens no Lote de Entrada", size=AppFonts.BODY_LARGE),
            ft.Container(
                content=self._lote_list_view,
                border=ft.border.all(1, ft.Colors.OUTLINE),
                border_radius=ft.border_radius.all(
                    AppDimensions.BORDER_RADIUS),
                padding=5,
                width=AppDimensions.FIELD_WIDTH,
                height=200  # Altura fixa para a lista de itens
            ),

            ft.Row(
                [
                    self._cancelar_button,
                    self._registrar_lote_button,
                ],
                alignment=ft.MainAxisAlignment.END, width=AppDimensions.FIELD_WIDTH, spacing=10
            )
        ]

    def did_mount(self):
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

    def obter_dados_item_formulario(self) -> dict:
        """Coleta os dados do formulário de *item único*."""
        peca_id = int(
            self._peca_dropdown.value) if self._peca_dropdown.value else None

        try:
            quantidade = int(
                self._quantidade_field.value) if self._quantidade_field.value else 0
        except (ValueError, TypeError):
            quantidade = None

        try:
            valor_custo_str = self._valor_custo_field.value.replace(
                ",", ".") if self._valor_custo_field.value else None
            valor_custo = float(valor_custo_str) if valor_custo_str else None
        except (ValueError, TypeError):
            valor_custo = -1

        return {
            "peca_id": peca_id,
            "quantidade": quantidade,
            "valor_custo": valor_custo,
            "descricao": self._descricao_field.value,
        }

    def limpar_formulario_item(self):
        """Limpa os campos de adição de item."""
        self._peca_dropdown.value = None
        self._quantidade_field.value = ""
        self._valor_custo_field.value = ""
        self._descricao_field.value = ""
        self._peca_dropdown.focus()  # Foca no dropdown para o próximo item
        self.update()

    def atualizar_lista_lote(self, lote: List[Dict[str, Any]]):
        """Atualiza o ListView com os itens do lote."""
        self._lote_list_view.controls.clear()
        if not lote:
            self._lote_list_view.controls.append(
                ft.Text("Nenhum item adicionado ao lote."))
        else:
            for item in lote:
                self._lote_list_view.controls.append(
                    ft.ListTile(
                        title=ft.Text(
                            f"{item['nome_peca']} (Qtd: {item['quantidade']})"),
                        subtitle=ft.Text(
                            f"Custo: R$ {item['valor_custo'] or 0.0:.2f} - Desc: {item['descricao'] or 'N/A'}"),
                        trailing=ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.RED_400,
                            tooltip="Remover item do lote",
                            data=item,  # Armazena o dict do item no botão
                            on_click=lambda e: self.view_model.remover_item_do_lote(
                                e.control.data)
                        )
                    )
                )
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

    def mostrar_feedback_snackbar(self, mensagem: str, sucesso: bool):
        """Exibe uma SnackBar para feedback rápido (ex: validação de item)."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=self.page.theme.color_scheme.primary if sucesso else self.page.theme.color_scheme.error
        )
        self.page.snack_bar.open = True
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
            page), alignment=ft.alignment.center, expand=True, padding=AppDimensions.PAGE_PADDING), expand=True)],
        padding=0
    )
