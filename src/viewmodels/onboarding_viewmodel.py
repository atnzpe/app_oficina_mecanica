
# =================================================================================
# MÓDULO DO VIEWMODEL DE ONBOARDING (onboarding_viewmodel.py)
# Local: src/viewmodels/onboarding_viewmodel.py
#
# OBJETIVO: Conter a lógica de negócio para a tela de configuração inicial.
# =================================================================================
import flet as ft
import logging
from src.database import queries

logger = logging.getLogger(__name__)

class OnboardingViewModel:
    """
    O ViewModel para a OnboardingView. Contém a lógica de validação e salvamento.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        # A referência à View é armazenada para poder comandá-la.
        self._view: 'OnboardingView' | None = None
        # O usuário logado é recuperado da sessão da página.
        self.user = self.page.session.get("usuario_logado")

    def vincular_view(self, view: 'OnboardingView'):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view

    def save_onboarding_data(self, e):
        """
        Pega os dados da View, valida, e comanda a atualização no banco de dados.
        """
        # Verificação de segurança: não faz nada se a View não estiver vinculada.
        if not self._view:
            return
        
        # 1. SOLICITA DADOS DA VIEW: O ViewModel pede os dados à View.
        dados = self._view.obter_dados_formulario()
        user_name = dados.get("user_name")
        establishment_name = dados.get("establishment_name")

        # 2. LÓGICA DE NEGÓCIO E VALIDAÇÃO.
        if not user_name or not establishment_name:
            # 3. COMANDA A VIEW: O ViewModel comanda a View para mostrar um erro.
            self._view.mostrar_erro("Todos os campos são obrigatórios.")
            return

        # 4. COMANDA A VIEW: Inicia o feedback visual de progresso.
        self._view.mostrar_progresso(True)
        
        # 5. INTERAÇÃO COM A CAMADA DE DADOS.
        logger.info(f"Salvando dados de onboarding para o usuário ID: {self.user.id}")
        queries.complete_onboarding(
            user_id=self.user.id,
            user_name=user_name,
            establishment_name=establishment_name,
        )

        # A lógica de negócio aqui poderia incluir atualizar o nome do usuário na sessão, se desejado.
        
        # 6. NAVEGAÇÃO: Após o sucesso, comanda a página para ir ao dashboard.
        self.page.go("/dashboard")