# =================================================================================
# MÓDULO DO VIEWMODEL DE EDIÇÃO DE CLIENTE (editar_cliente_viewmodel.py)
#
# ATUALIZAÇÃO (Robustez e Depuração):
#   - O fluxo de navegação foi refatorado para ocorrer apenas APÓS o usuário
#     fechar o diálogo de feedback, evitando travamentos na interface.
#   - Adicionados logs detalhados para rastrear cada etapa da lógica.
#   - Simplificada a chamada de diálogos para um único método na View.
# =================================================================================
import flet as ft
import logging
from src.database import queries
from src.models.models import Cliente
from typing import Callable, Optional

# Cria uma instância de logger específica para este módulo.
logger = logging.getLogger(__name__)


class EditarClienteViewModel:
    def __init__(self, page: ft.Page, cliente_id: int):
        self.page = page
        self.cliente_id = cliente_id
        self._view: 'EditarClienteView' | None = None
        self.cliente_em_edicao: Cliente | None = None
        # Log de inicialização do ViewModel.
        logger.debug(f"ViewModel de Edição de Cliente inicializado para o ID: {self.cliente_id}")

    def vincular_view(self, view: 'EditarClienteView'):
        """Vincula a View ao ViewModel para comunicação."""
        self._view = view
        logger.debug("ViewModel de Edição vinculado à sua View.")

    def carregar_dados_cliente(self):
        """Busca os dados do cliente e comanda a View para preencher o formulário."""
        if not self._view:
            logger.error("ViewModel: Tentativa de carregar dados sem uma View vinculada.")
            return

        try:
            logger.info(f"ViewModel: buscando dados para o cliente ID {self.cliente_id}")
            cliente = queries.obter_cliente_por_id(self.cliente_id)
            if cliente:
                self.cliente_em_edicao = cliente
                self._view.preencher_formulario(cliente)
                logger.info(f"ViewModel: Dados do cliente '{cliente.nome}' carregados e enviados para a View.")
            else:
                logger.warning(f"ViewModel: Cliente com ID {self.cliente_id} não encontrado no banco.")
                # Prepara a ação de navegação para ser executada após o diálogo.
                acao_navegacao = lambda: self.page.go("/gerir_clientes")
                self._view.mostrar_dialogo_feedback("Erro", "Cliente não encontrado.", acao_navegacao)
        except Exception as e:
            logger.error(f"Erro crítico ao carregar dados do cliente: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback("Erro Crítico", f"Não foi possível carregar os dados do cliente.\nErro: {e}")

    def salvar_alteracoes(self, novos_dados: dict):
        """Salva as alterações e comanda a exibição de um diálogo de feedback."""
        if not self._view: return
        try:
            logger.info(f"ViewModel: salvando alterações para o cliente ID {self.cliente_id}")
            sucesso = queries.atualizar_cliente(self.cliente_id, novos_dados)
            # Define a ação de navegação que será passada como callback para a View.
            acao_navegacao = lambda: self.page.go("/gerir_clientes")
            if sucesso:
                logger.info(f"ViewModel: Cliente ID {self.cliente_id} atualizado com sucesso.")
                self._view.mostrar_dialogo_feedback("Sucesso!", "Cliente atualizado com sucesso!", acao_navegacao)
            else:
                logger.warning(f"ViewModel: Nenhuma linha foi alterada para o cliente ID {self.cliente_id}.")
                self._view.mostrar_dialogo_feedback("Atenção", "Nenhuma alteração foi salva. Os dados podem ser os mesmos.")
        except Exception as e:
            logger.error(f"Erro crítico ao salvar alterações do cliente: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback("Erro Crítico", f"Não foi possível salvar as alterações.\nErro: {e}")

    def solicitar_desativacao_cliente(self):
        """Comanda a View para mostrar o diálogo de confirmação para desativar."""
        if self._view:
            logger.debug(f"ViewModel: Solicitando à View que mostre o diálogo de desativação.")
            self._view.mostrar_dialogo_confirmacao(is_activating=False)

    def confirmar_desativacao_cliente(self):
        """Confirma a desativação do cliente."""
        if not self._view: return
        try:
            logger.info(f"ViewModel: Confirmando desativação do cliente ID: {self.cliente_id}")
            sucesso = queries.desativar_cliente_por_id(self.cliente_id)
            self._view.fechar_dialogo()
            acao_navegacao = lambda: self.page.go("/gerir_clientes")
            if sucesso:
                logger.info(f"ViewModel: Cliente ID {self.cliente_id} desativado com sucesso.")
                self._view.mostrar_dialogo_feedback("Sucesso!", "Cliente desativado com sucesso!", acao_navegacao)
            else:
                logger.error(f"ViewModel: Falha ao desativar cliente ID {self.cliente_id} no banco.")
                self._view.mostrar_dialogo_feedback("Erro", "Erro ao desativar o cliente.")
        except Exception as e:
            logger.error(f"Erro crítico ao confirmar desativação: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback("Erro Crítico", f"Não foi possível desativar o cliente.\nErro: {e}")

    def solicitar_ativacao_cliente(self):
        """Comanda a View para mostrar o diálogo de confirmação para ativar."""
        if self._view:
            logger.debug(f"ViewModel: Solicitando à View que mostre o diálogo de ativação.")
            self._view.mostrar_dialogo_confirmacao(is_activating=True)

    def confirmar_ativacao_cliente(self):
        """Confirma a ativação do cliente."""
        if not self._view: return
        try:
            logger.info(f"ViewModel: Confirmando ATIVAÇÃO do cliente ID: {self.cliente_id}")
            sucesso = queries.ativar_cliente_por_id(self.cliente_id)
            self._view.fechar_dialogo()
            acao_navegacao = lambda: self.page.go("/gerir_clientes")
            if sucesso:
                logger.info(f"ViewModel: Cliente ID {self.cliente_id} ativado com sucesso.")
                self._view.mostrar_dialogo_feedback("Sucesso!", "Cliente ativado com sucesso!", acao_navegacao)
            else:
                logger.error(f"ViewModel: Falha ao ativar cliente ID {self.cliente_id} no banco.")
                self._view.mostrar_dialogo_feedback("Erro", "Erro ao ativar o cliente.")
        except Exception as e:
            logger.error(f"Erro crítico ao confirmar ativação: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback("Erro Crítico", f"Não foi possível ativar o cliente.\nErro: {e}")