# =================================================================================
# MÓDULO DO VIEWMODEL DE ONBOARDING (onboarding_viewmodel.py)
#
# ATUALIZAÇÃO:
#   - A função `save_onboarding_data` foi refatorada para coletar todos os
#     campos detalhados do estabelecimento e passá-los para a query.
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
        self._view: 'OnboardingView' | None = None
        self.user = self.page.session.get("usuario_logado")

    def vincular_view(self, view: 'OnboardingView'):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view

    def save_onboarding_data(self, e):
        """
        Pega os dados da View, valida, e comanda a atualização no banco de dados.
        """
        if not self._view:
            return
        
        # 1. SOLICITA DADOS DA VIEW
        dados = self._view.obter_dados_formulario()
        user_name = dados.get("user_name").strip()
        establishment_name = dados.get("nome").strip() # O nome da oficina está em 'nome'

        # 2. LÓGICA DE VALIDAÇÃO (Campos obrigatórios)
        if not user_name or not establishment_name:
            self._view.mostrar_erro("Seu Nome e o Nome da Oficina são obrigatórios.")
            return

        self._view.mostrar_progresso(True)
        
        # 3. INTERAÇÃO COM A CAMADA DE DADOS
        logger.info(f"Salvando dados de onboarding para o usuário ID: {self.user.id}")
        
        # Prepara o dicionário de dados do estabelecimento para a query
        dados_estabelecimento = {
            "nome": establishment_name,
            "endereco": dados.get("endereco", "").strip(),
            "telefone": dados.get("telefone", "").strip(),
            "responsavel": dados.get("responsavel", "").strip(),
            "cpf_cnpj": dados.get("cpf_cnpj", "").strip(),
            "chave_pix": dados.get("chave_pix", "").strip(),
        }
        
        try:
            queries.complete_onboarding(
                user_id=self.user.id,
                user_name=user_name,
                dados_estabelecimento=dados_estabelecimento
            )
            
            # 4. NAVEGAÇÃO
            self.page.go("/dashboard")
            
        except Exception as e:
            logger.error(f"Falha ao salvar onboarding: {e}", exc_info=True)
            self._view.mostrar_progresso(False)
            self._view.mostrar_erro("Falha ao salvar os dados. Tente novamente.")