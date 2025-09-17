# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DO VIEWMODEL DE LOGIN (login_viewmodel.py) - VERSÃO 2.0
#
# OBJETIVO: Conter a lógica de negócio e o estado da tela de login.
#
# SEÇÕES ALTERADAS NESTA REATORAÇÃO:
#   - Corrigido o import para `AuthService` e a sua instanciação.
#   - Adicionada a criação de uma conexão com a base de dados.
#   - O método `login` agora utiliza o `auth_service` para uma autenticação real,
#     em vez de uma simulação.
# =================================================================================
import flet as ft
import logging
from src.services.auth_service import AuthService
from src.database.database import criar_conexao_banco_de_dados, NOME_BANCO_DE_DADOS

class LoginViewModel:
    """O ViewModel para a LoginView."""

    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'LoginView' | None = None
        # O ViewModel agora gere a sua própria conexão com a base de dados.
        self.conexao = criar_conexao_banco_de_dados(NOME_BANCO_DE_DADOS)
        # Instancia o serviço de autenticação, passando a conexão.
        self.auth_service = AuthService(self.conexao)

    def vincular_view(self, view: 'LoginView'):
        self._view = view

    def login(self, e):
        """
        Lógica executada ao clicar no botão de login.
        """
        if not self._view:
            return

        dados = self._view.obter_dados_login()
        username = dados["username"]
        password = dados["password"]
        
        logging.info(f"ViewModel: Tentativa de login com utilizador='{username}'")
        
        # Validação simples
        if not username or not password:
            self._view.mostrar_erro("Utilizador e senha são obrigatórios.")
            return

        # --- LÓGICA DE AUTENTICAÇÃO REAL ---
        # Utiliza o serviço de autenticação para verificar o utilizador.
        utilizador_autenticado = self.auth_service.autenticar_usuario(username, password)

        if utilizador_autenticado:
            logging.info(f"ViewModel: Login bem-sucedido para '{username}'.")
            # Guarda o utilizador logado na sessão da página para que outras Views possam aceder.
            self.page.session.set("usuario_logado", utilizador_autenticado)
            # Navega para a próxima tela.
            self.page.go("/dashboard")
        else:
            logging.warning(f"ViewModel: Credenciais inválidas para '{username}'.")
            self._view.mostrar_erro("Utilizador ou senha inválidos.")
    
    def login_google(self, e):
        """Lógica para o futuro login com Google."""
        logging.info("ViewModel: Lógica para login com Google a ser implementada.")
        if self._view:
            self._view.mostrar_erro("Login com Google ainda não implementado.")