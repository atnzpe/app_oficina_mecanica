# =================================================================================
# MÓDULO DA VIEW DE EDIÇÃO DE PEÇA (editar_peca_view.py)
#
# OBJETIVO: Criar o formulário para a edição dos dados de uma peça existente.
# =================================================================================
import flet as ft
import logging
from src.viewmodels.editar_peca_viewmodel import EditarPecaViewModel
from src.models.models import Peca
from src.styles.style import AppDimensions, AppFonts
from threading import Timer
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class EditarPecaView(ft.Column):
    def __init__(self, page: ft.Page, peca_id: int):
        super().__init__()
        self.page = page
        self.view_model = EditarPecaViewModel(page, peca_id)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount
        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

        # --- Layout ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 15
        self.scroll = ft.ScrollMode.ADAPTIVE

        # --- Componentes do Formulário ---
        self._nome_field = ft.TextField(label="Nome da Peça*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._referencia_field = ft.TextField(label="Referência*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._fabricante_field = ft.TextField(label="Fabricante", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._descricao_field = ft.TextField(label="Descrição", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._preco_compra_field = ft.TextField(label="Preço de Compra (R$)*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS, keyboard_type=ft.KeyboardType.NUMBER)
        self._preco_venda_field = ft.TextField(label="Preço de Venda (R$)*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS, keyboard_type=ft.KeyboardType.NUMBER)
        self._estoque_field = ft.TextField(label="Quantidade em Estoque*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS, keyboard_type=ft.KeyboardType.NUMBER)
        
        # --- Diálogo Genérico ---
        self._dialogo_feedback = ft.AlertDialog(modal=True, title=ft.Text(), content=ft.Text(), actions=[])

        self.controls = [
            ft.Text("Editando Peça", size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            self._nome_field, self._referencia_field, self._fabricante_field, self._descricao_field,
            self._preco_compra_field, self._preco_venda_field, self._estoque_field,
            ft.Row(
                [
                    ft.ElevatedButton("Cancelar", on_click=lambda _: self.page.go("/gerir_pecas")),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Salvar Alterações", icon=ft.Icons.SAVE, on_click=lambda _: self.view_model.salvar_alteracoes()),
                ],
                width=AppDimensions.FIELD_WIDTH
            )
        ]
        logger.debug("EditarPecaView inicializada.")

    def did_mount(self):
        """Chamado pelo Flet quando a view é montada."""
        logger.info(f"EditarPecaView montada para peça ID: {self.view_model.peca_id}. Carregando dados...")
        self.view_model.carregar_dados()

    def preencher_formulario(self, peca: Peca):
        """Preenche os campos do formulário com os dados da peça."""
        logger.debug(f"View: Preenchendo formulário com dados da peça '{peca.nome}'.")
        self._nome_field.value = peca.nome or ""
        self._referencia_field.value = peca.referencia or ""
        self._fabricante_field.value = peca.fabricante or ""
        self._descricao_field.value = peca.descricao or ""
        self._preco_compra_field.value = str(peca.preco_compra)
        self._preco_venda_field.value = str(peca.preco_venda)
        self._estoque_field.value = str(peca.quantidade_em_estoque)
        self.update()

    def obter_dados_formulario(self) -> dict:
        """Coleta, converte e retorna os dados do formulário."""
        try:
            preco_compra = float(self._preco_compra_field.value)
            preco_venda = float(self._preco_venda_field.value)
            estoque = int(self._estoque_field.value)
        except (ValueError, TypeError):
            preco_compra = preco_venda = estoque = None
        return {
            "nome": self._nome_field.value, "referencia": self._referencia_field.value,
            "fabricante": self._fabricante_field.value, "descricao": self._descricao_field.value,
            "preco_compra": preco_compra, "preco_venda": preco_venda,
            "quantidade_em_estoque": estoque
        }

    # --- Métodos de Diálogo ---
    def _fechar_dialogo_e_agir(self, e):
        self.fechar_dialogo()
        if self._acao_pos_dialogo:
            Timer(0.1, self._acao_pos_dialogo).start()

    def mostrar_dialogo_feedback(self, titulo: str, conteudo: str, acao_callback: Optional[Callable[[], None]] = None):
        self._acao_pos_dialogo = acao_callback
        self._dialogo_feedback.title.value = titulo
        self._dialogo_feedback.content.value = conteudo
        self._dialogo_feedback.actions = [ft.TextButton("OK", on_click=self._fechar_dialogo_e_agir)]
        if self._dialogo_feedback not in self.page.overlay: self.page.overlay.append(self._dialogo_feedback)
        self._dialogo_feedback.open = True
        self.page.update()

    def fechar_dialogo(self, e=None):
        if self._dialogo_feedback in self.page.overlay:
            self._dialogo_feedback.open = False
            self.page.update()

def EditarPecaViewFactory(page: ft.Page, peca_id: int) -> ft.View:
    """Cria a View completa de Edição de Peça para o roteador."""
    return ft.View(
        route=f"/editar_peca/{peca_id}",
        appbar=ft.AppBar(
            title=ft.Text("Editar Peça"), center_title=True,
            bgcolor=page.theme.color_scheme.surface,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go("/gerir_pecas"), tooltip="Voltar para a Lista de Peças")
        ),
        controls=[ft.SafeArea(content=ft.Container(content=EditarPecaView(page, peca_id), alignment=ft.alignment.center, expand=True), expand=True)],
        padding=0
    )