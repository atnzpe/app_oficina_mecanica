# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DO VIEWMODEL DE LOGIN (login_viewmodel.py)
#
# ATUALIZAÇÃO:
#   - Após o login, o ViewModel agora verifica se o usuário precisa passar
#     pelo onboarding e o redireciona para a rota correta.
# =================================================================================
import flet as ft
import logging
from src.services import auth_service
from src.database import queries
from src.models.models import Usuario

logger = logging.getLogger(__name__)

class LoginViewModel:
    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'LoginView' | None = None

    def vincular_view(self, view: 'LoginView'):
        self._view = view

    def login(self, e):
        if not self._view: return

        dados = self._view.obter_dados_login()
        username = dados["username"]
        password = dados["password"]
        
        logger.info(f"ViewModel: Tentativa de login com usuário='{username}'")
        
        if not username or not password:
            self._view.mostrar_erro("Usuário e senha são obrigatórios.")
            return

        self._view.mostrar_progresso(True)

        utilizador_autenticado = auth_service.authenticate_user(username, password)

        self._view.mostrar_progresso(False)

        if utilizador_autenticado:
            logger.info(f"ViewModel: Login bem-sucedido para '{username}'.")
            # Guarda o usuário logado na sessão da página.
            self.page.session.set("usuario_logado", utilizador_autenticado)
            
            # --- NOVA LÓGICA DE ONBOARDING ---
            # Verifica se o usuário já configurou a oficina.
            if queries.has_establishment(utilizador_autenticado.id):
                # Se sim, vai para o dashboard.
                self.page.go("/dashboard")
            else:
                # Se não, vai para a tela de onboarding.
                self.page.go("/onboarding")
        else:
            logger.warning(f"ViewModel: Credenciais inválidas para '{username}'.")
            self._view.mostrar_erro("Usuário ou senha inválidos.")