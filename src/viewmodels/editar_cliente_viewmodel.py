
# =================================================================================
# MÓDULO DO VIEWMODEL DE EDIÇÃO DE CLIENTE (editar_cliente_viewmodel.py)
#
# REATORAÇÃO (CRUD):
#   - O ViewModel agora é inicializado com um `cliente_id` vindo da rota.
#   - Adicionado método `carregar_dados_cliente` para buscar os dados e
#     comandar a View a preencher o formulário.
#   - Ações de sucesso (salvar, desativar) agora navegam de volta para a lista.
# =================================================================================
import flet as ft
import logging
from src.database import queries
from src.models.models import Cliente # Supondo que o modelo seja importado

class EditarClienteViewModel:
    """
    O ViewModel para a tela de edição de um cliente específico.
    """
    def __init__(self, page: ft.Page, cliente_id: int):
        """
        Construtor do ViewModel.
        :param page: A referência à página principal do Flet.
        :param cliente_id: O ID do cliente a ser editado, vindo da URL.
        """
        self.page = page
        self.cliente_id = cliente_id
        self._view: 'EditarClienteView' | None = None
        # O estado `cliente_em_edicao` pode ser útil se precisarmos do objeto completo.
        self.cliente_em_edicao: Cliente | None = None

    def vincular_view(self, view: 'EditarClienteView'):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view

    def carregar_dados_cliente(self):
        """Busca os dados do cliente no DB e comanda a View para preencher o form."""
        logging.info(f"ViewModel: buscando dados para o cliente ID {self.cliente_id}")
        cliente = queries.obter_cliente_por_id(self.cliente_id)
        if cliente and self._view:
            self.cliente_em_edicao = cliente # Armazena o objeto cliente no estado do ViewModel
            self._view.preencher_formulario(cliente)
        elif self._view:
            # Caso o cliente não seja encontrado (ex: URL inválida), mostra um erro e oferece para voltar.
            self._view.mostrar_feedback("Cliente não encontrado.", False)
            # Poderia adicionar um botão de "Voltar" na view em caso de erro.

    def salvar_alteracoes(self, novos_dados: dict):
        """Salva as alterações e navega de volta para a lista de gerenciamento."""
        logging.info(f"ViewModel: salvando alterações para o cliente ID {self.cliente_id}")
        sucesso = queries.atualizar_cliente(self.cliente_id, novos_dados)
        if self._view:
            if sucesso:
                self._view.mostrar_feedback("Cliente atualizado com sucesso!", True)
                self.page.go("/gerir_clientes") # Navega de volta para a lista
            else:
                self._view.mostrar_feedback("Erro ao salvar alterações.", False)

    def solicitar_desativacao_cliente(self):
        """Comanda a View para abrir o diálogo de confirmação."""
        logging.info(f"ViewModel: Solicitação de desativação para o cliente ID {self.cliente_id}.")
        if self._view:
            self._view.abrir_modal_confirmacao_desativar()

    def confirmar_desativacao_cliente(self, e):
        """Desativa o cliente e navega de volta para a lista de gerenciamento."""
        logging.info(f"ViewModel: Confirmado! Desativando cliente ID: {self.cliente_id}")
        sucesso = queries.desativar_cliente_por_id(self.cliente_id)
        if self._view:
            self._view.fechar_todos_os_modais() # Fecha o diálogo de confirmação
            if sucesso:
                self._view.mostrar_feedback("Cliente desativado com sucesso!", True)
                self.page.go("/gerir_clientes") # Navega de volta para a lista
            else:
                self._view.mostrar_feedback("Erro ao desativar o cliente.", False)