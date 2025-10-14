# =================================================================================
# MÓDULO DA VIEW DE CADASTRO DE PEÇA (cadastro_peca_view.py)
#
# OBJETIVO: Criar o formulário para o cadastro de novas peças e itens de estoque.
# =================================================================================
import flet as ft
from src.viewmodels.cadastro_peca_viewmodel import CadastroPecaViewModel
from src.styles.style import AppDimensions, AppFonts
from typing import Callable, Optional
from threading import Timer
import logging

logger = logging.getLogger(__name__)


class CadastroPecaView(ft.Column):
    """
    A View para o formulário de cadastro de peças.
    """

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = CadastroPecaViewModel(page)
        self.view_model.vincular_view(self)

        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

        # --- Layout da Coluna ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 15
        self.scroll = ft.ScrollMode.ADAPTIVE

        # --- Componentes do Formulário ---
        self._nome_field = ft.TextField(
            label="Nome da Peça*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._referencia_field = ft.TextField(
            label="Referência*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._fabricante_field = ft.TextField(
            label="Fabricante", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._descricao_field = ft.TextField(
            label="Descrição", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._preco_compra_field = ft.TextField(label="Preço de Compra (R$)*", width=AppDimensions.FIELD_WIDTH,
                                                border_radius=AppDimensions.BORDER_RADIUS, keyboard_type=ft.KeyboardType.NUMBER)
        self._preco_venda_field = ft.TextField(label="Preço de Venda (R$)*", width=AppDimensions.FIELD_WIDTH,
                                               border_radius=AppDimensions.BORDER_RADIUS, keyboard_type=ft.KeyboardType.NUMBER)
        self._estoque_field = ft.TextField(label="Quantidade em Estoque*", width=AppDimensions.FIELD_WIDTH,
                                           border_radius=AppDimensions.BORDER_RADIUS, keyboard_type=ft.KeyboardType.NUMBER)

        # --- Diálogo Genérico ---
        self._dialogo_feedback = ft.AlertDialog(
            modal=True, title=ft.Text(), content=ft.Text(), actions=[])

        self.controls = [
            ft.Text("Cadastro de Nova Peça", size=AppFonts.TITLE_MEDIUM,
                    weight=ft.FontWeight.BOLD),
            self._nome_field, self._referencia_field, self._fabricante_field, self._descricao_field,
            self._preco_compra_field, self._preco_venda_field, self._estoque_field,
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Cancelar", on_click=self.view_model.cancelar_cadastro),
                    ft.ElevatedButton("Salvar Peça", icon=ft.Icons.SAVE,
                                      on_click=lambda _: self.view_model.salvar_peca()),
                ],
                alignment=ft.MainAxisAlignment.END, spacing=10, width=AppDimensions.FIELD_WIDTH
            )
        ]
        logger.debug("CadastroPecaView inicializada.")

    def obter_dados_formulario(self) -> dict:
        """Coleta, converte e retorna os dados do formulário para o ViewModel."""
        logger.debug("View: Coletando dados do formulário de peças.")
        try:
            preco_compra = float(
                self._preco_compra_field.value) if self._preco_compra_field.value else 0.0
            preco_venda = float(
                self._preco_venda_field.value) if self._preco_venda_field.value else 0.0
            estoque = int(
                self._estoque_field.value) if self._estoque_field.value else 0
        except (ValueError, TypeError):
            preco_compra = preco_venda = estoque = None  # Indica erro de conversão

        return {
            "nome": self._nome_field.value, "referencia": self._referencia_field.value,
            "fabricante": self._fabricante_field.value, "descricao": self._descricao_field.value,
            "preco_compra": preco_compra, "preco_venda": preco_venda,
            "quantidade_em_estoque": estoque
        }

    # --- Métodos de Diálogo (Padrão) ---
    def _fechar_dialogo_e_agir(self, e):
        self.fechar_dialogo()
        if self._acao_pos_dialogo:
            t = Timer(0.1, self._acao_pos_dialogo)
            t.start()

    def mostrar_dialogo_feedback(self, titulo: str, conteudo: str, acao_callback: Optional[Callable[[], None]] = None):
        """Exibe um diálogo de feedback usando a overlay."""
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


def CadastroPecaViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa de Cadastro de Peça para o roteador."""
    return ft.View(
        route="/cadastro_peca",
        appbar=ft.AppBar(
            title=ft.Text("Cadastrar Nova Peça"), center_title=True,
            bgcolor=page.theme.color_scheme.surface,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go(
                "/gerir_pecas"), tooltip="Voltar para a Lista de Peças")
        ),
        controls=[
            ft.SafeArea(
                content=ft.Container(content=CadastroPecaView(
                    page), alignment=ft.alignment.center, expand=True),
                expand=True
            )
        ],
        padding=0
    )
