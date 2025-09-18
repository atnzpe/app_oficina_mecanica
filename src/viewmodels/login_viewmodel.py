# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DO VIEWMODEL DE LOGIN (login_viewmodel.py)
#
# ATUALIZAÇÃO:
#   - Adicionado o método `login_google` como um placeholder para resolver o
#     `AttributeError` que ocorria na inicialização da LoginView.
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
        """Lógica executada ao clicar no botão de login principal."""
        if not self._view: return

        dados = self._view.obter_dados_login()
        username = dados["username"]
        password = dados["password"]
        
        logger.info(f"ViewModel: Tentativa de login com usuário='{username}'")
        
        if not username or not password:
            self._view.mostrar_erro("Usuário e senha são obrigatórios.")
            return

        # Notifica a View para mostrar o anel de progresso.
        self._view.mostrar_progresso(True)

        utilizador_autenticado = auth_service.authenticate_user(username, password)

        # Notifica a View para esconder o anel de progresso.
        self._view.mostrar_progresso(False)

        if utilizador_autenticado:
            logger.info(f"ViewModel: Login bem-sucedido para '{username}'.")
            self.page.session.set("usuario_logado", utilizador_autenticado)
            
            # Lógica de redirecionamento para Onboarding ou Dashboard.
            if queries.has_establishment(utilizador_autenticado.id):
                self.page.go("/dashboard")
            else:
                self.page.go("/onboarding")
        else:
            logger.warning(f"ViewModel: Credenciais inválidas para '{username}'.")
            self._view.mostrar_erro("Usuário ou senha inválidos.")

    # --- FUNÇÃO ADICIONADA ---
    def login_google(self, e):
        """
        Lógica para o futuro login com Google. Atualmente é um placeholder.
        """
        # Log para registrar que o botão foi clicado.
        logging.info("ViewModel: Botão 'Login com Google' clicado. Funcionalidade a ser implementada.")
        # Mostra uma mensagem informativa para o usuário na própria tela.
        if self._view:
            self._view.mostrar_erro("Login com Google ainda não implementado.")