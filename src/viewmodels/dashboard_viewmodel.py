# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DO VIEWMODEL DO DASHBOARD (dashboard_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio e o estado da DashboardView.
#
# SEÇÕES ALTERADAS NESTA REATORAÇÃO (ISSUE #1 - INTEGRAÇÃO FINAL):
#   - O construtor `__init__` agora instancia as Views dos componentes filhos
#     (`EditarClienteView`, `OrdemServicoFormularioView`), tornando-as parte
#     do estado do Dashboard.
#   - Os métodos como `abrir_edicao_cliente` agora delegam a chamada diretamente
#     para os métodos públicos das instâncias das Views filhas (ex: `abrir_modal`).
#
# SEÇÕES SEM ALTERAÇÃO:
#   - A lógica de gestão de estado (`usuario_atual`) e a comunicação com a sua
#     própria View (`_view`) permanecem as mesmas.
# =================================================================================
import flet as ft
import logging
from src.models.models import Usuario

# Importa as Views dos componentes que este ViewModel irá controlar.
from src.views.editar_cliente_view import EditarClienteView
from src.views.os_formulario_view import OrdemServicoFormularioView

class DashboardViewModel:
    """
    O ViewModel para a DashboardView. Contém o estado e a lógica da tela principal.
    """
    def __init__(self, page: ft.Page):
        """
        Construtor do ViewModel.
        :param page: A referência à página principal do Flet para controlo de modais.
        """
        self.page = page
        # Estado: Armazena o utilizador que está logado.
        self.usuario_atual: Usuario | None = None
        # Referência à View que este ViewModel controla.
        self._view: 'DashboardView' | None = None

        # --- INTEGRAÇÃO DOS COMPONENTES FILHOS ---
        # Instancia os componentes de View que serão apresentados no Dashboard.
        # O DashboardViewModel é responsável por orquestrar quando estes são mostrados.
        self.editar_cliente_componente = EditarClienteView(page)
        self.os_formulario_componente = OrdemServicoFormularioView(page)

    def vincular_view(self, view: 'DashboardView'):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view

    def atualizar_estado_botoes_view(self):
        """Comunica à View que o estado dos botões precisa de ser atualizado."""
        if self._view:
            logado = bool(self.usuario_atual)
            self._view.atualizar_botoes(logado)

    # --- HANDLERS DE EVENTOS (Ações dos Botões) ---
    def simular_login(self, e):
        """Simula um login/logout para fins de teste e desenvolvimento."""
        if not self.usuario_atual:
            self.usuario_atual = Usuario(id=1, nome="admin", senha="...")
            logging.info(f"Utilizador '{self.usuario_atual.nome}' logado.")
        else:
            self.usuario_atual = None
            logging.info("Utilizador deslogado.")
        self.atualizar_estado_botoes_view()

    def abrir_cadastro_cliente(self, e):
        """Lógica para abrir o modal de cadastro de cliente."""
        logging.info("ViewModel: Ação para abrir cadastro de cliente.")
        # A lógica completa para este modal seria implementada aqui ou num ViewModel dedicado.

    def abrir_cadastro_carro(self, e):
        """Lógica para abrir o modal de cadastro de carro."""
        logging.info("ViewModel: Ação para abrir cadastro de carro.")

    def abrir_edicao_cliente(self, e):
        """Delega a ação de abrir o modal de pesquisa para o componente filho."""
        logging.info("ViewModel: A delegar para EditarClienteView.")
        self.editar_cliente_componente.abrir_modal_pesquisa(e)

    def abrir_form_os(self, e):
        """Delega a ação de abrir o formulário de OS para o componente filho."""
        logging.info("ViewModel: A delegar para OrdemServicoFormularioView.")
        self.os_formulario_componente.abrir_modal(e)

    def sair_app(self, e):
        """Fecha a janela da aplicação."""
        self.page.window_destroy()

    def abrir_cadastro_peca(self, e):
        logging.info("ViewModel: Ação para abrir cadastro de peça.")

    def abrir_saldo_estoque(self, e):
        logging.info("ViewModel: Ação para abrir saldo de estoque.")

    def abrir_relatorios(self, e):
        logging.info("ViewModel: Ação para abrir relatórios.")