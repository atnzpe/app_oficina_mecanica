# =================================================================================
# MÓDULO DA VIEW DE EDIÇÃO DE CARRO (editar_carro_view.py)
#
# OBJETIVO: Criar o formulário para a edição dos dados de um veículo existente.
# PADRÃO: Segue o padrão de UI e interação com diálogos via `overlay`.
# =================================================================================
import flet as ft
import logging
from src.viewmodels.editar_carro_viewmodel import EditarCarroViewModel
from src.models.models import Cliente
from src.styles.style import AppDimensions, AppFonts
from threading import Timer
from typing import Callable, Optional, List

logger = logging.getLogger(__name__)

class EditarCarroView(ft.Column):
    def __init__(self, page: ft.Page, carro_id: int):
        super().__init__()
        self.page = page
        self.view_model = EditarCarroViewModel(page, carro_id)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount

        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

        # --- Layout ---
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.CENTER
        self.spacing = 15

        # --- Componentes do Formulário ---
        self._cliente_dropdown = ft.Dropdown(label="Proprietário*", hint_text="Selecione o proprietário", border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._modelo_field = ft.TextField(label="Modelo*", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._placa_field = ft.TextField(label="Placa*", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._ano_field = ft.TextField(label="Ano", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS), keyboard_type=ft.KeyboardType.NUMBER)
        self._cor_field = ft.TextField(label="Cor", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))

        # --- Botões de Ação ---
        self._salvar_btn = ft.ElevatedButton("Salvar Alterações", icon=ft.Icons.SAVE, on_click=lambda _: self.view_model.salvar_alteracoes())
        self._cancelar_btn = ft.ElevatedButton("Cancelar", on_click=lambda _: self.page.go("/gerir_carros"))

        # --- Diálogo Genérico ---
        self._dialogo_feedback = ft.AlertDialog(modal=True, title=ft.Text(), content=ft.Text(), actions=[])

        self.controls = [
            ft.Text("Editando Veículo", size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            self._cliente_dropdown, self._modelo_field, self._placa_field, self._ano_field, self._cor_field,
            ft.Row(
                [self._cancelar_btn, ft.Container(expand=True), self._salvar_btn],
                width=AppDimensions.FIELD_WIDTH
            )
        ]
        logger.debug("EditarCarroView inicializada.")

    def did_mount(self):
        """Chamado pelo Flet quando a view é montada."""
        logger.info(f"EditarCarroView montada para carro ID: {self.view_model.carro_id}. Carregando dados...")
        self.view_model.carregar_dados()

    def preencher_formulario(self, carro: dict):
        """Preenche os campos do formulário com os dados do carro."""
        logger.debug(f"View: Preenchendo formulário com dados da placa '{carro['placa']}'.")
        self._cliente_dropdown.value = str(carro['cliente_id'])
        self._modelo_field.value = carro['modelo'] or ""
        self._placa_field.value = carro['placa'] or ""
        self._ano_field.value = str(carro['ano']) if carro['ano'] is not None else ""
        self._cor_field.value = carro['cor'] or ""
        self.update()

    def popular_dropdown_clientes(self, clientes: List[Cliente]):
        """Preenche o dropdown com a lista de clientes."""
        logger.debug(f"View: Populando dropdown com {len(clientes)} clientes.")
        self._cliente_dropdown.options = [
            ft.dropdown.Option(key=str(cliente.id), text=cliente.nome) for cliente in clientes
        ]
        self.update()

    def obter_dados_formulario(self) -> dict:
        """Envia os dados dos campos para o ViewModel."""
        logger.debug("View: Coletando dados do formulário para salvar.")
        return {
            "cliente_id": int(self._cliente_dropdown.value) if self._cliente_dropdown.value else None,
            "modelo": self._modelo_field.value,
            "placa": self._placa_field.value,
            "ano": int(self._ano_field.value) if self._ano_field.value and self._ano_field.value.isdigit() else None,
            "cor": self._cor_field.value,
        }

    # --- Métodos de Diálogo ---
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
        self._dialogo_feedback.actions = [ft.TextButton("OK", on_click=self._fechar_dialogo_e_agir)]
        
        if self._dialogo_feedback not in self.page.overlay:
            self.page.overlay.append(self._dialogo_feedback)
        
        self._dialogo_feedback.open = True
        self.page.update()

    def fechar_dialogo(self, e=None):
        if self._dialogo_feedback in self.page.overlay:
            self._dialogo_feedback.open = False
            self.page.update()

def EditarCarroViewFactory(page: ft.Page, carro_id: int) -> ft.View:
    """Cria a View completa de Edição de Carro para o roteador."""
    view_content = EditarCarroView(page, carro_id)
    return ft.View(
        route=f"/editar_carro/{carro_id}",
        appbar=ft.AppBar(
            title=ft.Text("Editar Veículo"), center_title=True,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go("/gerir_carros"), tooltip="Voltar para a Lista de Veículos"),
            bgcolor=page.theme.color_scheme.surface,
        ),
        controls=[
            ft.SafeArea(
                content=ft.Container(content=view_content, alignment=ft.alignment.center, expand=True),
                expand=True
            )
        ],
        padding=0
    )