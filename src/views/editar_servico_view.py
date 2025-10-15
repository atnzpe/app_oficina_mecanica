# =================================================================================
# MÓDULO DA VIEW DE EDIÇÃO DE SERVIÇO (editar_servico_view.py)
# =================================================================================
import flet as ft
import logging
from src.viewmodels.editar_servico_viewmodel import EditarServicoViewModel
from src.models.models import Servico, Peca
from src.styles.style import AppDimensions, AppFonts
from threading import Timer
from typing import Callable, Optional, List

logger = logging.getLogger(__name__)

class EditarServicoView(ft.Column):
    def __init__(self, page: ft.Page, servico_id: int):
        super().__init__()
        self.page = page
        self.view_model = EditarServicoViewModel(page, servico_id)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount
        self._acao_pos_dialogo: Optional[Callable[[], None]] = None
        self._todos_os_checkboxes: List[ft.Checkbox] = []

        # --- Layout ---
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 15
        self.scroll = ft.ScrollMode.ADAPTIVE

        # --- Componentes ---
        self._nome_field = ft.TextField(label="Nome do Serviço*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._descricao_field = ft.TextField(label="Descrição", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._valor_field = ft.TextField(label="Valor (R$)*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS, keyboard_type=ft.KeyboardType.NUMBER)
        self._lista_pecas_checkboxes = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=10)
        self._dialogo_feedback = ft.AlertDialog(modal=True, title=ft.Text(), content=ft.Text(), actions=[])

        self.controls = [
            ft.Text("Editando Serviço", size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            self._nome_field, self._descricao_field, self._valor_field,
            ft.Divider(),
            ft.Text("Peças Incluídas no Serviço (Kit)"),
            ft.Container(
                content=self._lista_pecas_checkboxes,
                border=ft.border.all(1, ft.Colors.OUTLINE),
                border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
                padding=10, width=AppDimensions.FIELD_WIDTH, height=200
            ),
            ft.Row(
                [
                    ft.ElevatedButton("Cancelar", on_click=lambda _: self.page.go("/gerir_servicos")),
                    ft.ElevatedButton("Salvar Alterações", icon=ft.Icons.SAVE, on_click=lambda _: self.view_model.salvar_alteracoes()),
                ],
                alignment=ft.MainAxisAlignment.END, spacing=10, width=AppDimensions.FIELD_WIDTH
            )
        ]

    def did_mount(self):
        self.view_model.carregar_dados_iniciais()

    def popular_lista_pecas(self, pecas: List[Peca]):
        """Cria a lista completa de checkboxes uma única vez."""
        self._todos_os_checkboxes.clear()
        if pecas:
            for peca in pecas:
                self._todos_os_checkboxes.append(
                    ft.Checkbox(label=f"{peca.nome} (Ref: {peca.referencia})", data=peca.id, value=False)
                )
        self._lista_pecas_checkboxes.controls = self._todos_os_checkboxes
        self.update()

    def preencher_formulario(self, servico: Servico):
        """Preenche o formulário com os dados do serviço a ser editado."""
        logger.debug(f"View: Preenchendo formulário para o serviço '{servico.nome}'.")
        self._nome_field.value = servico.nome
        self._descricao_field.value = servico.descricao or ""
        self._valor_field.value = str(servico.valor)
        
        # Marca os checkboxes das peças que já estão associadas ao serviço
        ids_pecas_associadas = {peca.id for peca in servico.pecas}
        for checkbox in self._todos_os_checkboxes:
            if checkbox.data in ids_pecas_associadas:
                checkbox.value = True
        
        self.update()

    def obter_dados_formulario(self) -> dict:
        """Coleta e retorna os dados do formulário."""
        try:
            valor = float(self._valor_field.value.replace(",", ".")) if self._valor_field.value else 0.0
        except (ValueError, TypeError):
            valor = None

        pecas_selecionadas = [cb.data for cb in self._todos_os_checkboxes if cb.value]
        
        return {
            "nome": self._nome_field.value, "descricao": self._descricao_field.value,
            "valor": valor, "pecas_selecionadas": pecas_selecionadas,
        }

    # --- Métodos de Diálogo ---
    def _fechar_dialogo_e_agir(self, e):
        self.fechar_dialogo()
        if self._acao_pos_dialogo: Timer(0.1, self._acao_pos_dialogo).start()

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

def EditarServicoViewFactory(page: ft.Page, servico_id: int) -> ft.View:
    return ft.View(
        route=f"/editar_servico/{servico_id}",
        appbar=ft.AppBar(
            title=ft.Text("Editar Serviço"), center_title=True,
            bgcolor=page.theme.color_scheme.surface,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go("/gerir_servicos"), tooltip="Voltar")
        ),
        controls=[ft.SafeArea(content=ft.Container(content=EditarServicoView(page, servico_id), alignment=ft.alignment.center, expand=True, padding=AppDimensions.PAGE_PADDING), expand=True)],
        padding=0
    )