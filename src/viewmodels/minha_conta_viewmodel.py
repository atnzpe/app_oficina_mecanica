# =================================================================================
# MÓDULO DO VIEWMODEL DE MINHA CONTA (minha_conta_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela "Minha Conta", focada na
#           alteração de senha do usuário logado.
# =================================================================================
import flet as ft
import logging
from src.services import auth_service

logger = logging.getLogger(__name__)

class MinhaContaViewModel:
    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'MinhaContaView' | None = None
        # Recupera o usuário logado da sessão da página
        self.usuario_logado = self.page.session.get("usuario_logado")
        logger.debug("MinhaContaViewModel inicializado.")

    def vincular_view(self, view: 'MinhaContaView'):
        """Vincula a View ao ViewModel."""
        self._view = view
        logger.debug("ViewModel de Minha Conta vinculado à sua View.")

    def alterar_senha(self):
        """
        Orquestra a validação e a alteração da senha do usuário.
        """
        if not self._view:
            logger.error("ViewModel: Ação 'alterar_senha' chamada sem uma View vinculada.")
            return

        dados = self._view.obter_dados_formulario()
        senha_atual = dados.get("senha_atual")
        nova_senha = dados.get("nova_senha")
        confirmar_senha = dados.get("confirmar_senha")

        # --- Validações de Pré-condição ---
        if not all([senha_atual, nova_senha, confirmar_senha]):
            self._view.mostrar_dialogo_feedback("Erro de Validação", "Todos os campos são obrigatórios.")
            return
        
        if nova_senha != confirmar_senha:
            self._view.mostrar_dialogo_feedback("Erro de Validação", "A nova senha e a confirmação não coincidem.")
            return
        
        if not self.usuario_logado:
            self._view.mostrar_dialogo_feedback("Erro de Autenticação", "Nenhum usuário logado encontrado. Por favor, faça o login novamente.")
            return

        # --- Interação com a Camada de Serviço ---
        logger.info(f"ViewModel: Tentando alterar a senha para o usuário '{self.usuario_logado.nome}'.")
        sucesso, mensagem = auth_service.alterar_senha(
            usuario=self.usuario_logado,
            senha_atual=senha_atual,
            nova_senha=nova_senha
        )

        # --- Feedback para o Usuário ---
        if sucesso:
            # Em caso de sucesso, limpa o formulário e exibe a mensagem.
            acao_navegacao = lambda: self.page.go("/dashboard")
            self._view.limpar_formulario()
            self._view.mostrar_dialogo_feedback("Sucesso!", mensagem,acao_navegacao)
        else:
            # Em caso de falha, apenas exibe a mensagem de erro retornada pelo serviço.
            self._view.mostrar_dialogo_feedback("Falha na Alteração", mensagem)