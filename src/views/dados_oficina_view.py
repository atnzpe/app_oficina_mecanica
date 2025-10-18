# =================================================================================
# MÓDULO DA VIEW DE DADOS DA OFICINA (dados_oficina_view.py)
#
# ATUALIZAÇÃO (Issue #30):
#   - Adicionados controles `ft.Image` e `ft.ElevatedButton` para
#     exibir e fazer o upload da logo.
# =================================================================================
import flet as ft
import logging
from src.viewmodels.dados_oficina_viewmodel import DadosOficinaViewModel
from src.models.models import Estabelecimento
from src.styles.style import AppDimensions, AppFonts
from typing import Callable, Optional
from threading import Timer

logger = logging.getLogger(__name__)


class DadosOficinaView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = DadosOficinaViewModel(page)
        self.view_model.vincular_view(self)
        self.on_mount = self.did_mount
        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

        # --- Layout ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 15
        self.scroll = ft.ScrollMode.ADAPTIVE

        # --- NOVOS Componentes para Logo ---
        self._logo_image = ft.Image(
            src="assets/ico.png",  # Imagem padrão
            width=100,
            height=100,
            fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(50)  # Deixa a imagem redonda
        )
        self._upload_logo_button = ft.ElevatedButton(
            "Carregar Nova Logo",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.view_model.abrir_seletor_logo
        )

        # --- Componentes do Formulário ---
        self._nome_field = ft.TextField(
            label="Nome da Oficina*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._endereco_field = ft.TextField(
            label="Endereço", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._telefone_field = ft.TextField(label="Telefone", width=AppDimensions.FIELD_WIDTH,
                                            border_radius=AppDimensions.BORDER_RADIUS, keyboard_type=ft.KeyboardType.PHONE)
        self._responsavel_field = ft.TextField(
            label="Responsável", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._cpf_cnpj_field = ft.TextField(
            label="CPF ou CNPJ", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._chave_pix_field = ft.TextField(
            label="Chave PIX", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)

        self._dialogo_feedback = ft.AlertDialog(
            modal=True, title=ft.Text(), content=ft.Text(), actions=[])

        # --- Estrutura da View ---
        self.controls = [
            ft.Text("Dados da Oficina", size=AppFonts.TITLE_MEDIUM,
                    weight=ft.FontWeight.BOLD),

            # --- Seção da Logo Adicionada ---
            self._logo_image,
            self._upload_logo_button,
            ft.Divider(),

            # --- Formulário de Texto ---
            self._nome_field, self._endereco_field, self._telefone_field,
            self._responsavel_field, self._cpf_cnpj_field, self._chave_pix_field,
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Cancelar", on_click=lambda _: self.page.go("/dashboard")),
                    ft.ElevatedButton("Salvar Alterações", icon=ft.Icons.SAVE,
                                      on_click=lambda _: self.view_model.salvar_alteracoes()),
                ],
                alignment=ft.MainAxisAlignment.END, width=AppDimensions.FIELD_WIDTH, spacing=10
            )
        ]

    def did_mount(self):
        self.view_model.carregar_dados()

    def preencher_formulario(self, estabelecimento: Estabelecimento):
        self._nome_field.value = estabelecimento.nome or ""
        self._endereco_field.value = estabelecimento.endereco or ""
        self._telefone_field.value = estabelecimento.telefone or ""
        self._responsavel_field.value = estabelecimento.responsavel or ""
        self._cpf_cnpj_field.value = estabelecimento.cpf_cnpj or ""
        self._chave_pix_field.value = estabelecimento.chave_pix or ""
        self.update()

    # --- NOVO MÉTODO ---
    def atualizar_logo_exibida(self, caminho_logo: str):
        """Comandado pelo ViewModel para atualizar a imagem na tela."""
        logger.debug(
            f"View: Atualizando exibição da logo para: {caminho_logo}")
        self._logo_image.src = caminho_logo
        # Adiciona um timestamp para evitar problemas de cache do Flet
        self._logo_image.src_base64 = None
        self.update()

    def obter_dados_formulario(self) -> dict:
        return {
            "nome": self._nome_field.value,
            "endereco": self._endereco_field.value,
            "telefone": self._telefone_field.value,
            "responsavel": self._responsavel_field.value,
            "cpf_cnpj": self._cpf_cnpj_field.value,
            "chave_pix": self._chave_pix_field.value,
        }

    # --- Métodos de Diálogo (sem alteração) ---
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


def DadosOficinaViewFactory(page: ft.Page) -> ft.View:
    # (Factory permanece a mesma)
    return ft.View(
        route="/dados_oficina",
        appbar=ft.AppBar(
            title=ft.Text("Dados da Oficina"), center_title=True,
            bgcolor=page.theme.color_scheme.surface,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go(
                "/dashboard"), tooltip="Voltar ao Dashboard")
        ),
        controls=[ft.SafeArea(content=ft.Container(content=DadosOficinaView(
            page), alignment=ft.alignment.center, expand=True, padding=AppDimensions.PAGE_PADDING), expand=True)],
        padding=0
    )
