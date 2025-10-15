# =================================================================================
# MÓDULO DA VIEW DE CADASTRO DE SERVIÇO (cadastro_servico_view.py)
#
# ATUALIZAÇÃO:
#   - Adicionado campo de busca e lista rolável para a seleção de peças.
# =================================================================================
import flet as ft
from src.viewmodels.cadastro_servico_viewmodel import CadastroServicoViewModel
from src.styles.style import AppDimensions, AppFonts
from src.models.models import Peca
from typing import Callable, Optional, List
from threading import Timer
import logging

logger = logging.getLogger(__name__)


class CadastroServicoView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = CadastroServicoViewModel(page)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount
        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

        # Armazena a referência de todos os checkboxes criados
        self._todos_os_checkboxes: List[ft.Checkbox] = []

        # --- Layout ---
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 15
        self.scroll = ft.ScrollMode.ADAPTIVE

        # --- Componentes ---
        self._nome_field = ft.TextField(
            label="Nome do Serviço*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._descricao_field = ft.TextField(
            label="Descrição", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._valor_field = ft.TextField(label="Valor (R$)*", width=AppDimensions.FIELD_WIDTH,
                                         border_radius=AppDimensions.BORDER_RADIUS, keyboard_type=ft.KeyboardType.NUMBER)

        # Campo de busca para as peças
        self._busca_peca_field = ft.TextField(
            label="Buscar Peça por Nome ou Referência",
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: self.view_model.filtrar_pecas(e.control.value),
            width=AppDimensions.FIELD_WIDTH,
            border_radius=AppDimensions.BORDER_RADIUS
        )
        # Lista rolável que conterá os checkboxes
        self._lista_pecas_checkboxes = ft.ListView(
            expand=True, spacing=5, padding=10)

        self._dialogo_feedback = ft.AlertDialog(
            modal=True, title=ft.Text(), content=ft.Text(), actions=[])

        self.controls = [
            ft.Text("Cadastro de Novo Serviço",
                    size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            self._nome_field, self._descricao_field, self._valor_field,
            ft.Divider(),
            ft.Text("Peças Incluídas no Serviço (Opcional)"),
            self._busca_peca_field,  # Campo de busca
            ft.Container(
                content=self._lista_pecas_checkboxes,
                border=ft.border.all(1, ft.Colors.OUTLINE),
                border_radius=ft.border_radius.all(
                    AppDimensions.BORDER_RADIUS),
                width=AppDimensions.FIELD_WIDTH,
                height=200  # Altura fixa para a área rolável
            ),
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Cancelar", on_click=self.view_model.cancelar_cadastro),
                    ft.ElevatedButton("Salvar Serviço", icon=ft.Icons.SAVE,
                                      on_click=lambda _: self.view_model.salvar_servico()),
                ],
                alignment=ft.MainAxisAlignment.END, spacing=10, width=AppDimensions.FIELD_WIDTH
            )
        ]

    def did_mount(self):
        self.view_model.carregar_pecas_iniciais()

    def popular_lista_pecas(self, pecas: List[Peca]):
        """Cria a lista completa de checkboxes uma única vez."""
        self._todos_os_checkboxes.clear()
        if pecas:
            for peca in pecas:
                self._todos_os_checkboxes.append(
                    ft.Checkbox(
                        label=f"{peca.nome} (Ref: {peca.referencia})", data=peca.id, value=False)
                )
        # Exibe a lista completa inicialmente
        self.atualizar_lista_filtrada_pecas(pecas)

    def atualizar_lista_filtrada_pecas(self, pecas_filtradas: List[Peca]):
        """Atualiza a ListView com os checkboxes que correspondem ao filtro."""
        self._lista_pecas_checkboxes.controls.clear()
        ids_filtrados = {peca.id for peca in pecas_filtradas}

        if not ids_filtrados:
            self._lista_pecas_checkboxes.controls.append(
                ft.Text("Nenhuma peça encontrada."))
        else:
            for checkbox in self._todos_os_checkboxes:
                if checkbox.data in ids_filtrados:
                    self._lista_pecas_checkboxes.controls.append(checkbox)

        self.update()

    def obter_dados_formulario(self) -> dict:
        """Coleta e retorna os dados do formulário para o ViewModel."""
        try:
            valor = float(self._valor_field.value.replace(
                ",", ".")) if self._valor_field.value else 0.0
        except (ValueError, TypeError):
            valor = None

        pecas_selecionadas = [
            cb.data for cb in self._todos_os_checkboxes if cb.value
        ]

        return {
            "nome": self._nome_field.value,
            "descricao": self._descricao_field.value,
            "valor": valor,
            "pecas_selecionadas": pecas_selecionadas,
        }

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


def CadastroServicoViewFactory(page: ft.Page) -> ft.View:
    return ft.View(
        route="/cadastro_servico",
        appbar=ft.AppBar(
            title=ft.Text("Cadastrar Novo Serviço"), center_title=True,
            bgcolor=page.theme.color_scheme.surface,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go(
                "/gerir_servicos"), tooltip="Voltar")
        ),
        controls=[ft.SafeArea(content=ft.Container(content=CadastroServicoView(
            page), alignment=ft.alignment.center, expand=True, padding=AppDimensions.PAGE_PADDING), expand=True)],
        padding=0
    )
