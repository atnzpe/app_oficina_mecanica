# =================================================================================
# MÓDULO DO VIEWMODEL DO DASHBOARD (dashboard_viewmodel.py)
#
# ATUALIZAÇÃO:
#   - `abrir_cadastro_cliente`: Agora, em vez de gerenciar um modal, simplesmente
#     navega para a rota '/cadastro_cliente'.
#   - A instância de `CadastroClienteView` foi removida, pois a criação da
#     view agora é responsabilidade do roteador.
# =================================================================================
import flet as ft
import logging
from src.models.models import Usuario
from src.views.editar_cliente_view import EditarClienteView
from src.views.os_formulario_view import OrdemServicoFormularioView
# A importação do CadastroClienteView não é mais necessária aqui.
from src.database import queries

class DashboardViewModel:
    """
    O ViewModel para a DashboardView. Contém o estado e a lógica da tela principal.
    """
    def __init__(self, page: ft.Page):
        """
        Construtor do ViewModel.
        """
        self.page = page
        self._view: 'DashboardView' | None = None
        self.usuario_atual: Usuario | None = self.page.session.get("usuario_logado")
        
        if self.usuario_atual:
            logging.info(f"DashboardViewModel iniciado para o usuário: {self.usuario_atual.nome}")
        else:
            logging.warning("DashboardViewModel iniciado sem um usuário na sessão.")

        # O DashboardViewModel continua orquestrando os componentes que SÃO modais.
        # O componente de cadastro de cliente foi removido daqui.
        self.editar_cliente_componente = EditarClienteView(page)
        self.os_formulario_componente = OrdemServicoFormularioView(page)

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
        self.page.session.clear() # Limpa toda a sessão por segurança.
        self.usuario_atual = None
        self.page.go("/login")

    # --- MÉTODO ATUALIZADO ---
    def abrir_cadastro_cliente(self, e):
        """
        Navega o usuário para a página de cadastro de cliente.
        """
        logging.info("ViewModel: Navegando para a rota /cadastro_cliente.")
        # Fecha qualquer diálogo aberto na página atual (como o de boas-vindas) antes de navegar.
        if self._view:
            self._view.fechar_dialogos()
        # Comando de navegação.
        self.page.go("/cadastro_cliente")

    # --- (O restante da classe permanece o mesmo) ---
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