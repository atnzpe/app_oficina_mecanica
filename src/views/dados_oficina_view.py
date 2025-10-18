# =================================================================================
# MÓDULO DA VIEW DE DADOS DA OFICINA (dados_oficina_view.py)
#
# OBJETIVO: Criar o formulário para a edição dos dados do estabelecimento
#           (Issue #30).
# =================================================================================
import flet as ft
import logging
from src.viewmodels.dados_oficina_viewmodel import DadosOficinaViewModel
from src.models.models import Estabelecimento
from src.styles.style import AppDimensions, AppFonts
from typing import Callable, Optional
from threading import Timer

# Configura o logger para este módulo
logger = logging.getLogger(__name__)

class DadosOficinaView(ft.Column):
    """
    A View para o formulário de "Dados da Oficina".
    """
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        # Instancia o ViewModel e se vincula a ele
        self.view_model = DadosOficinaViewModel(page)
        self.view_model.vincular_view(self)
        # Define a função que será chamada quando a view for montada na tela
        self.on_mount = self.did_mount
        # Atributo para armazenar a ação de callback (navegação)
        self._acao_pos_dialogo: Optional[Callable[[], None]] = None

        # --- Configuração do Layout da Coluna ---
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 15
        # Habilita rolagem caso a tela seja muito pequena
        self.scroll = ft.ScrollMode.ADAPTIVE

        # --- Componentes do Formulário ---
        self._nome_field = ft.TextField(label="Nome da Oficina*", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._endereco_field = ft.TextField(label="Endereço", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._telefone_field = ft.TextField(label="Telefone", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS, keyboard_type=ft.KeyboardType.PHONE)
        self._responsavel_field = ft.TextField(label="Responsável", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._cpf_cnpj_field = ft.TextField(label="CPF ou CNPJ", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        self._chave_pix_field = ft.TextField(label="Chave PIX", width=AppDimensions.FIELD_WIDTH, border_radius=AppDimensions.BORDER_RADIUS)
        
        # Diálogo genérico para feedback (será adicionado à overlay)
        self._dialogo_feedback = ft.AlertDialog(modal=True, title=ft.Text(), content=ft.Text(), actions=[])

        # --- Estrutura final da View ---
        self.controls = [
            ft.Text("Dados da Oficina", size=AppFonts.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
            self._nome_field,
            self._endereco_field,
            self._telefone_field,
            self._responsavel_field,
            self._cpf_cnpj_field,
            self._chave_pix_field,
            # (Futuramente, o upload de logo será adicionado aqui)
            ft.Row(
                [
                    # Botão para cancelar a edição e voltar ao dashboard
                    ft.ElevatedButton("Cancelar", on_click=lambda _: self.page.go("/dashboard")),
                    # Botão para salvar, delega a ação ao ViewModel
                    ft.ElevatedButton("Salvar Alterações", icon=ft.Icons.SAVE, on_click=lambda _: self.view_model.salvar_alteracoes()),
                ],
                alignment=ft.MainAxisAlignment.END,
                width=AppDimensions.FIELD_WIDTH,
                spacing=10
            )
        ]
        logger.debug("View 'Dados da Oficina' inicializada.")

    def did_mount(self):
        """Chamado pelo Flet quando a view é montada na tela."""
        logger.debug("View 'Dados da Oficina' montada. Carregando dados...")
        # Comanda o ViewModel a carregar os dados
        self.view_model.carregar_dados()

    def preencher_formulario(self, estabelecimento: Estabelecimento):
        """Preenche os campos do formulário com os dados carregados pelo ViewModel."""
        logger.debug(f"View: Preenchendo formulário com dados de '{estabelecimento.nome}'.")
        self._nome_field.value = estabelecimento.nome or ""
        self._endereco_field.value = estabelecimento.endereco or ""
        self._telefone_field.value = estabelecimento.telefone or ""
        self._responsavel_field.value = estabelecimento.responsavel or ""
        self._cpf_cnpj_field.value = estabelecimento.cpf_cnpj or ""
        self._chave_pix_field.value = estabelecimento.chave_pix or ""
        # Atualiza a interface da View
        self.update()

    def obter_dados_formulario(self) -> dict:
        """Coleta os dados atuais dos campos e os retorna como um dicionário."""
        return {
            "nome": self._nome_field.value,
            "endereco": self._endereco_field.value,
            "telefone": self._telefone_field.value,
            "responsavel": self._responsavel_field.value,
            "cpf_cnpj": self._cpf_cnpj_field.value,
            "chave_pix": self._chave_pix_field.value,
        }

    # --- Métodos de Diálogo (Padrão de UI com Overlay) ---
    
    def _fechar_dialogo_e_agir(self, e):
        """Fecha o diálogo e executa a ação de callback (navegação) com segurança."""
        self.fechar_dialogo()
        # Se uma ação de callback (como navegar) foi definida, executa-a
        if self._acao_pos_dialogo:
            logger.debug("View: Ação de callback (navegação) pós-diálogo agendada.")
            # Usamos um Timer para garantir que a UI processe o fechamento do diálogo antes da navegação
            Timer(0.1, self._acao_pos_dialogo).start()

    def mostrar_dialogo_feedback(self, titulo: str, conteudo: str, acao_callback: Optional[Callable[[], None]] = None):
        """Exibe um diálogo de feedback padronizado."""
        # Armazena a ação de callback (pode ser None)
        self._acao_pos_dialogo = acao_callback
        # Configura o diálogo genérico
        self._dialogo_feedback.title.value = titulo
        self._dialogo_feedback.content.value = conteudo
        self._dialogo_feedback.actions = [ft.TextButton("OK", on_click=self._fechar_dialogo_e_agir)]
        
        # Adiciona à overlay para estabilidade (padrão que definimos)
        if self._dialogo_feedback not in self.page.overlay:
            self.page.overlay.append(self._dialogo_feedback)
        
        self._dialogo_feedback.open = True
        self.page.update()

    def fechar_dialogo(self, e=None):
        """Fecha o diálogo de feedback."""
        if self._dialogo_feedback in self.page.overlay:
            self._dialogo_feedback.open = False
            self.page.update()

def DadosOficinaViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa de 'Dados da Oficina' para o roteador."""
    return ft.View(
        route="/dados_oficina",
        appbar=ft.AppBar(
            title=ft.Text("Dados da Oficina"), center_title=True,
            bgcolor=page.theme.color_scheme.surface,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go("/dashboard"), tooltip="Voltar ao Dashboard")
        ),
        controls=[
            ft.SafeArea(
                content=ft.Container(
                    content=DadosOficinaView(page), 
                    alignment=ft.alignment.center, 
                    expand=True,
                    padding=AppDimensions.PAGE_PADDING
                ), 
                expand=True
            )
        ],
        padding=0
    )