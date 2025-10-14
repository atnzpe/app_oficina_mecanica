# =================================================================================
# MÓDULO DO VIEWMODEL DE GERENCIAMENTO DE CARROS (gerir_carros_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de gerenciamento de carros,
#           incluindo busca, ativação, desativação e navegação.
# =================================================================================
import flet as ft
import logging
from src.database import queries
from typing import List

# Configura o logger para este módulo.
logger = logging.getLogger(__name__)

class GerirCarrosViewModel:
    """
    O ViewModel para a GerirCarrosView. Lida com toda a lógica da tela.
    """
    def __init__(self, page: ft.Page):
        # Armazena a referência da página principal do Flet.
        self.page = page
        # A referência à View será vinculada para permitir a comunicação.
        self._view: 'GerirCarrosView' | None = None
        # Armazena o ID do carro que está sofrendo uma ação (ativar/desativar).
        self._carro_para_acao_id: int | None = None
        logger.debug("GerirCarrosViewModel inicializado.")

    def vincular_view(self, view: 'GerirCarrosView'):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view
        logger.debug("GerirCarrosViewModel vinculado à sua View.")

    def carregar_carros_iniciais(self):
        """Busca todos os carros (ativos e inativos) para exibir na tela."""
        logger.info("ViewModel: Carregando lista inicial de todos os carros.")
        # Chama a pesquisa com um termo vazio para listar todos.
        self.pesquisar_carro("")

    def pesquisar_carro(self, termo: str):
        """
        Busca carros no banco com base em um termo (placa, modelo, proprietário)
        e comanda a View para exibir os resultados.
        """
        if not self._view: return
        logger.info(f"ViewModel: pesquisando por carros com o termo '{termo}'")
        # 1. INTERAÇÃO COM A CAMADA DE DADOS (QUERIES).
        carros_encontrados = queries.buscar_carros_por_termo(termo)
        # 2. COMANDA A VIEW para atualizar a lista de resultados.
        self._view.atualizar_lista_resultados(carros_encontrados)

    def editar_carro(self, carro_id: int):
        """Navega para a tela de edição do carro selecionado."""
        logger.info(f"ViewModel: Navegando para a tela de edição do carro ID {carro_id}")
        self.page.go(f"/editar_carro/{carro_id}")

    # --- LÓGICA DE DESATIVAÇÃO ---

    def solicitar_desativacao(self, carro_id: int, carro_info: str):
        """Armazena o ID do carro e comanda a View para abrir o diálogo de confirmação."""
        self._carro_para_acao_id = carro_id
        logger.info(f"ViewModel: Solicitação para desativar o carro ID {carro_id} ('{carro_info}').")
        if self._view:
            self._view.mostrar_dialogo_confirmacao(carro_info, is_activating=False)

    def confirmar_desativacao(self):
        """Confirma a desativação do carro e atualiza a UI."""
        if self._carro_para_acao_id is None: return
        logger.info(f"ViewModel: Confirmando desativação para o carro ID {self._carro_para_acao_id}.")
        try:
            sucesso = queries.desativar_carro_por_id(self._carro_para_acao_id)
            if self._view:
                self._view.fechar_dialogo()
                if sucesso:
                    self._view.mostrar_feedback("Carro desativado com sucesso!", True)
                    self.carregar_carros_iniciais() # Recarrega a lista
                else:
                    self._view.mostrar_feedback("Erro ao desativar o carro.", False)
        except Exception as e:
            logger.error(f"ViewModel: Erro inesperado ao desativar carro: {e}", exc_info=True)
            if self._view: self._view.mostrar_feedback(f"Falha crítica: {e}", False)
        finally:
            self._carro_para_acao_id = None
            
    # --- LÓGICA DE ATIVAÇÃO ---
    
    def solicitar_ativacao(self, carro_id: int, carro_info: str):
        """Armazena o ID do carro e comanda a View para abrir o diálogo de confirmação de ativação."""
        self._carro_para_acao_id = carro_id
        logger.info(f"ViewModel: Solicitação para ATIVAR o carro ID {carro_id} ('{carro_info}').")
        if self._view:
            self._view.mostrar_dialogo_confirmacao(carro_info, is_activating=True)

    def confirmar_ativacao(self):
        """Confirma a ativação do carro e atualiza a UI."""
        if self._carro_para_acao_id is None: return
        logger.info(f"ViewModel: Confirmando ATIVAÇÃO para o carro ID {self._carro_para_acao_id}.")
        try:
            sucesso = queries.ativar_carro_por_id(self._carro_para_acao_id)
            if self._view:
                self._view.fechar_dialogo()
                if sucesso:
                    self._view.mostrar_feedback("Carro reativado com sucesso!", True)
                    self.carregar_carros_iniciais() # Recarrega a lista
                else:
                    self._view.mostrar_feedback("Erro ao reativar o carro.", False)
        except Exception as e:
            logger.error(f"ViewModel: Erro inesperado ao ativar carro: {e}", exc_info=True)
            if self._view: self._view.mostrar_feedback(f"Falha crítica ao reativar: {e}", False)
        finally:
            self._carro_para_acao_id = None