# =================================================================================
# MÓDULO DO VIEWMODEL DE DADOS DA OFICINA (dados_oficina_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de gerenciamento dos dados
#           do estabelecimento (Issue #30).
# =================================================================================
import flet as ft
import logging
from src.database import queries
from src.models.models import Estabelecimento
from typing import Optional

# Configura o logger para este módulo
logger = logging.getLogger(__name__)


class DadosOficinaViewModel:
    """
    ViewModel para a tela 'Dados da Oficina'.
    """

    def __init__(self, page: ft.Page):
        # Armazena a referência da página Flet para navegação e acesso à sessão
        self.page = page
        # Referência fraca à View (será vinculada pela própria View)
        self._view: 'DadosOficinaView' | None = None
        # Recupera o usuário logado da sessão da página
        self.usuario_logado = self.page.session.get("usuario_logado")
        # Armazena os dados do estabelecimento carregado para saber qual ID atualizar
        self.estabelecimento: Optional[Estabelecimento] = None
        logger.debug("DadosOficinaViewModel inicializado.")

    def vincular_view(self, view: 'DadosOficinaView'):
        """Permite que a View se vincule a este ViewModel."""
        self._view = view
        logger.debug("View 'Dados da Oficina' vinculada ao ViewModel.")

    def carregar_dados(self):
        """Busca os dados do estabelecimento e comanda a View para preencher o formulário."""
        # Verifica se a view e o usuário estão disponíveis
        if not self._view or not self.usuario_logado:
            logger.warning(
                "ViewModel: View ou Usuário não vinculados. Carregamento abortado.")
            return

        try:
            logger.info(
                f"ViewModel: buscando dados do estabelecimento para o usuário ID {self.usuario_logado.id}")
            # 1. INTERAÇÃO COM CAMADA DE DADOS
            self.estabelecimento = queries.obter_estabelecimento_por_id_usuario(
                self.usuario_logado.id)

            if self.estabelecimento:
                # 2. COMANDA A VIEW
                # Se encontrou, comanda a View para preencher os campos
                self._view.preencher_formulario(self.estabelecimento)
                logger.info(
                    f"ViewModel: Dados do estabelecimento '{self.estabelecimento.nome}' carregados.")
            else:
                logger.warning(
                    "ViewModel: Nenhum estabelecimento encontrado para o usuário logado.")
                self._view.mostrar_dialogo_feedback(
                    "Erro", "Nenhum estabelecimento encontrado.")
        except Exception as e:
            logger.error(
                f"Erro crítico ao carregar dados do estabelecimento: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Não foi possível carregar os dados.\nErro: {e}")

    def salvar_alteracoes(self):
        """Valida os dados do formulário e salva as alterações no banco de dados."""
        if not self._view or not self.estabelecimento:
            logger.error(
                "ViewModel: Tentativa de salvar sem View ou Estabelecimento carregado.")
            return

        try:
            # 1. SOLICITA DADOS DA VIEW
            dados = self._view.obter_dados_formulario()

            # 2. LÓGICA DE VALIDAÇÃO
            if not dados.get("nome", "").strip():
                self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "O campo 'Nome da Oficina' é obrigatório.")
                return

            logger.info(
                f"ViewModel: salvando alterações para o estabelecimento ID {self.estabelecimento.id}")

            # 3. INTERAÇÃO COM CAMADA DE DADOS
            sucesso = queries.atualizar_estabelecimento(
                self.estabelecimento.id, dados)

            # 4. PREPARA O FEEDBACK
            # Define a ação de navegação que será executada após o diálogo fechar
            def acao_navegacao(): return self.page.go("/dashboard")

            # 5. COMANDA A VIEW
            if sucesso:
                self._view.mostrar_dialogo_feedback(
                    "Sucesso!", "Dados da oficina atualizados com sucesso!", acao_navegacao)
            else:
                self._view.mostrar_dialogo_feedback(
                    "Atenção", "Nenhuma alteração foi salva (os dados podem ser os mesmos).")

        except Exception as e:
            logger.error(
                f"Erro crítico ao salvar alterações: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Não foi possível salvar as alterações.\nErro: {e}")
