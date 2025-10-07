# =================================================================================
# MÓDULO DA VIEW DE CADASTRO DE CARRO (cadastro_carro_view.py)
#
# OBJETIVO: Criar o formulário para o cadastro de novos veículos.
# PADRÃO: Segue o mesmo padrão de UI e interação dos outros formulários.
# =================================================================================
import flet as ft
from src.viewmodels.cadastro_carro_viewmodel import CadastroCarroViewModel
from src.styles.style import AppDimensions, AppFonts
from src.models.models import Cliente
from typing import List, Callable, Optional
from threading import Timer
import logging

logger = logging.getLogger(__name__)

class CadastroCarroView(ft.Column):
    """
    A View para o formulário de cadastro de carros.
    """
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = CadastroCarroViewModel(page)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount
        
        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

        # --- Componentes Visuais do Formulário ---
        self._cliente_dropdown = ft.Dropdown(label="Proprietário*", hint_text="Selecione o proprietário do veículo", border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._modelo_field = ft.TextField(label="Modelo*", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._placa_field = ft.TextField(label="Placa*", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._ano_field = ft.TextField(label="Ano", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS), keyboard_type=ft.KeyboardType.NUMBER)
        self._cor_field = ft.TextField(label="Cor", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))

        # Diálogo genérico que será adicionado à overlay.
        self._dialogo_feedback = ft.AlertDialog(modal=True, title=ft.Text(), content=ft.Text(), actions=[])

        # --- Estrutura da Página ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20
        self.controls = [
            ft.Text("Cadastro de Novo Veículo", size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            self._cliente_dropdown, self._modelo_field, self._placa_field, self._ano_field, self._cor_field,
            ft.Row(
                [
                    ft.ElevatedButton("Cancelar", on_click=self.view_model.cancelar_cadastro),
                    ft.ElevatedButton("Salvar Veículo", icon=ft.Icons.SAVE_OUTLINED, on_click=self.view_model.salvar_carro),
                ],
                alignment=ft.MainAxisAlignment.END, spacing=10, width=AppDimensions.FIELD_WIDTH
            )
        ]
        logger.debug("CadastroCarroView inicializada.")

    def did_mount(self):
        """Chamado pelo Flet quando a view é montada."""
        logger.info("CadastroCarroView montada. Carregando clientes...")
        self.view_model.carregar_clientes()

    def obter_dados_formulario(self) -> dict:
        """Envia os dados dos campos para o ViewModel."""
        logger.debug("View: Coletando dados do formulário.")
        return {
            "cliente_id": self._cliente_dropdown.value,
            "modelo": self._modelo_field.value,
            "placa": self._placa_field.value,
            "ano": self._ano_field.value,
            "cor": self._cor_field.value,
        }

    def popular_dropdown_clientes(self, clientes: List[Cliente]):
        """Preenche o dropdown com a lista de clientes."""
        logger.debug(f"View: Populando dropdown com {len(clientes)} clientes.")
        self._cliente_dropdown.options = [
            ft.dropdown.Option(key=str(cliente.id), text=cliente.nome) for cliente in clientes
        ]
        self.update()

    # --- Métodos de Diálogo ---

    def _fechar_dialogo_e_agir(self, e):
        self.fechar_dialogo()
        if self._acao_pos_dialogo:
            t = Timer(0.1, self._acao_pos_dialogo)
            t.start()
            logger.debug("View: Ação de callback (navegação) pós-diálogo agendada.")

    def mostrar_dialogo_feedback(self, titulo: str, conteudo: str, acao_callback: Optional[Callable[[], None]] = None):
        """Exibe um diálogo de feedback usando a overlay."""
        logger.info(f"View: Exibindo diálogo de feedback - Título: '{titulo}'.")
        self._acao_pos_dialogo = acao_callback
        
        self._dialogo_feedback.title.value = titulo
        self._dialogo_feedback.content.value = conteudo
        self._dialogo_feedback.actions = [ft.TextButton("OK", on_click=self._fechar_dialogo_e_agir)]
        
        if self._dialogo_feedback not in self.page.overlay:
            self.page.overlay.append(self._dialogo_feedback)
        
        self._dialogo_feedback.open = True
        self.page.update()

    def fechar_dialogo(self, e=None):
        logger.debug("View: Fechando diálogo.")
        if self._dialogo_feedback in self.page.overlay:
            self._dialogo_feedback.open = False
            self.page.update()

def CadastroCarroViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa de Cadastro de Carro para o roteador."""
    view_content = CadastroCarroView(page)
    return ft.View(
        route="/cadastro_carro",
        appbar=ft.AppBar(
            title=ft.Text("Cadastrar Novo Veículo"), center_title=True,
            bgcolor=page.theme.color_scheme.surface,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go("/gerir_carros"), tooltip="Voltar para a Lista de Veículos")
        ),
        controls=[
            ft.SafeArea(
                content=ft.Container(content=view_content, alignment=ft.alignment.center, expand=True),
                expand=True
            )
        ],
        padding=0
    )