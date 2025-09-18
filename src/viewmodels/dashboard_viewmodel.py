# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DO VIEWMODEL DO DASHBOARD (dashboard_viewmodel.py)
#
# CORREÇÃO (BUG FIX):
#   - O construtor `__init__` agora busca ativamente o usuário logado na
#     sessão da página (`page.session`). Isso permite que o ViewModel já
#     "nasça" sabendo se há um usuário logado, sem precisar de uma chamada
#     de atualização posterior.
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
        :param page: A referência à página principal do Flet.
        """
        self.page = page
        # Referência à View que este ViewModel controla.
        self._view: 'DashboardView' | None = None

        # --- LÓGICA ATUALIZADA ---
        # Ao ser criado, o ViewModel imediatamente verifica a sessão da página
        # para ver se um objeto 'usuario_logado' foi salvo pelo LoginViewModel.
        self.usuario_atual: Usuario | None = self.page.session.get("usuario_logado")
        if self.usuario_atual:
            logging.info(f"DashboardViewModel iniciado para o usuário: {self.usuario_atual.nome}")
        else:
            logging.warning("DashboardViewModel iniciado sem um usuário na sessão.")

        # Instancia os componentes de View que serão apresentados no Dashboard.
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
            
    def logout(self, e):
        """Executa o logout do usuário."""
        logging.info(f"Usuário '{self.usuario_atual.nome}' fazendo logout.")
        self.page.session.remove("usuario_logado")
        self.usuario_atual = None
        self.page.go("/login")

    # --- (O restante dos métodos permanece o mesmo) ---

    def abrir_cadastro_cliente(self, e):
        logging.info("ViewModel: Ação para abrir cadastro de cliente.")

    def abrir_cadastro_carro(self, e):
        logging.info("ViewModel: Ação para abrir cadastro de carro.")

    def abrir_edicao_cliente(self, e):
        logging.info("ViewModel: A delegar para EditarClienteView.")
        self.editar_cliente_componente.abrir_modal_pesquisa(e)

    def abrir_form_os(self, e):
        logging.info("ViewModel: A delegar para OrdemServicoFormularioView.")
        self.os_formulario_componente.abrir_modal(e)

    def sair_app(self, e):
        self.page.window.destroy()

    def abrir_cadastro_peca(self, e):
        logging.info("ViewModel: Ação para abrir cadastro de peça.")

    def abrir_saldo_estoque(self, e):
        logging.info("ViewModel: Ação para abrir saldo de estoque.")

    def abrir_relatorios(self, e):
        logging.info("ViewModel: Ação para abrir relatórios.")