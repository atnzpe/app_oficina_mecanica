# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DO VIEWMODEL DO DASHBOARD (dashboard_viewmodel.py)
#
# ATUALIZAÇÃO:
#   - O ViewModel agora cria e mantém uma instância do novo
#     `CadastroClienteView`.
#   - O método `abrir_cadastro_cliente` agora delega a chamada para o
#     componente de cadastro, implementando a funcionalidade real.
# =================================================================================
import flet as ft
import logging
from src.models.models import Usuario
from src.views.editar_cliente_view import EditarClienteView
from src.views.os_formulario_view import OrdemServicoFormularioView
# --- NOVO: Importa a nova View de Cadastro de Cliente ---
from src.views.cadastro_cliente_view import CadastroClienteView
from src.database import queries

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
        self._view: 'DashboardView' | None = None
        self.usuario_atual: Usuario | None = self.page.session.get("usuario_logado")
        
        if self.usuario_atual:
            logging.info(f"DashboardViewModel iniciado para o usuário: {self.usuario_atual.nome}")
        else:
            logging.warning("DashboardViewModel iniciado sem um usuário na sessão.")

        # Instancia os componentes filhos que o Dashboard controla.
        # O DashboardViewModel atua como um "orquestrador" destes componentes.
        self.editar_cliente_componente = EditarClienteView(page)
        self.os_formulario_componente = OrdemServicoFormularioView(page)
        # --- NOVO: Instancia o componente de cadastro de cliente ---
        self.cadastro_cliente_componente = CadastroClienteView(page)

    def vincular_view(self, view: 'DashboardView'):
        """
        Vincula a View ao ViewModel e dispara a verificação inicial.
        """
        self._view = view
        self.verificar_primeiro_cliente()
        
    def verificar_primeiro_cliente(self):
        """
        Verifica se existem clientes e, se não, comanda a View para mostrar o diálogo.
        """
        logging.info("ViewModel: Verificando a existência de clientes para o prompt de boas-vindas.")
        if not queries.verificar_existencia_cliente():
            if self._view:
                logging.info("Nenhum cliente encontrado. Comandando a View para exibir o diálogo.")
                self._view.mostrar_dialogo_primeiro_cliente()
                
    def logout(self, e):
        """
        Executa o logout do usuário, limpando a sessão e redirecionando para o login.
        """
        logging.info(f"Usuário '{self.usuario_atual.nome}' fazendo logout.")
        self.page.session.remove("usuario_logado")
        self.usuario_atual = None
        self.page.go("/login")

    # --- MÉTODO ATUALIZADO ---
    def abrir_cadastro_cliente(self, e):
        """
        Delega a ação de abrir o modal para o componente de cadastro de cliente.
        """
        logging.info("ViewModel: Delegando para CadastroClienteView.")
        # Primeiro, comanda a sua própria View para fechar qualquer diálogo que esteja aberto
        # (como o de boas-vindas), para evitar sobreposição de modais.
        if self._view:
            self._view.fechar_dialogos()
        # Em seguida, chama o método público do nosso novo componente especialista.
        self.cadastro_cliente_componente.abrir_modal(e)

    # --- (O restante da classe permanece o mesmo, atuando como placeholders) ---
    def abrir_cadastro_carro(self, e):
        logging.info("ViewModel: Ação para abrir cadastro de carro.")
        if self._view: self._view.mostrar_feedback("Funcionalidade 'Novo Veículo' a ser implementada.", True)

    def abrir_edicao_cliente(self, e):
        logging.info("ViewModel: Delegando para EditarClienteView.")
        self.editar_cliente_componente.abrir_modal_pesquisa(e)

    def abrir_form_os(self, e):
        logging.info("ViewModel: Delegando para OrdemServicoFormularioView.")
        self.os_formulario_componente.abrir_modal(e)
    
    def abrir_cadastro_peca(self, e):
        logging.info("ViewModel: Ação para abrir cadastro de peça.")
        if self._view: self._view.mostrar_feedback("Funcionalidade 'Nova Peça' a ser implementada.", True)

    def abrir_saldo_estoque(self, e):
        logging.info("ViewModel: Ação para abrir saldo de estoque.")
        if self._view: self._view.mostrar_feedback("Funcionalidade 'Verificar Estoque' a ser implementada.", True)

    def abrir_relatorios(self, e):
        logging.info("ViewModel: Ação para abrir relatórios.")
        if self._view: self._view.mostrar_feedback("Funcionalidade 'Gerar Relatórios' a ser implementada.", True)
