# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE ENTRADA DA APLICAÇÃO (main.py) - VERSÃO 3.1
#
# OBJETIVO: Atuar como o roteador central da aplicação.
#
# ATUALIZAÇÃO:
#   - Adicionada a rota '/onboarding' para a nova tela de configuração.
#   - A lógica do `LoginViewModel` agora irá verificar se o onboarding é
#     necessário e redirecionará o usuário para a rota correta.
# =================================================================================
import flet as ft
import threading
import logging

# Importações das Views
from src.views.login_view import LoginView
from src.views.dashboard_view import DashboardView
from src.views.register_view import RegisterView
from src.views.onboarding_view import OnboardingView # --- NOVO ---

# Importações de Serviços e Banco de Dados
from src.services.task_queue_service import processar_fila_db
from src.database.database import initialize_database as inicializar_banco_de_dados
from src.database import queries
from utils import criar_pastas

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(page: ft.Page):
    """
    Função principal que inicializa e configura a aplicação Flet.
    """
    page.title = "Sistema OS Oficina Mecânica - v3.1"
    page.theme_mode = ft.ThemeMode.DARK
    # ... (outras configurações de página)

    # --- INICIALIZAÇÃO ---
    logging.info("Iniciando serviços de fundo...")
    inicializar_banco_de_dados()
    thread_db = threading.Thread(target=processar_fila_db, args=(page,), daemon=True)
    thread_db.start()
    criar_pastas(".")

    # --- GERENCIADOR DE ROTAS ---
    def route_change(route):
        logging.info(f"Navegando para a rota: {page.route}")
        app_container = ft.Container(
            # ... (configurações do container)
            alignment=ft.alignment.center,
        )
        page.views.clear()

        # Mapeamento de rotas para as Views
        if page.route == "/login":
            app_container.content = LoginView(page)
            page.views.append(ft.View(route="/login", controls=[app_container]))
        elif page.route == "/register":
            app_container.content = RegisterView(page)
            page.views.append(ft.View(route="/register", controls=[app_container]))
        # --- NOVA ROTA DE ONBOARDING ---
        elif page.route == "/onboarding":
            app_container.content = OnboardingView(page)
            page.views.append(ft.View(route="/onboarding", controls=[app_container]))
        elif page.route == "/dashboard":
            app_container.content = DashboardView(page)
            page.views.append(ft.View(route="/dashboard", controls=[app_container]))
        else:
            page.go(page.route)
            return
        page.update()

    page.on_route_change = route_change

    # --- LÓGICA DE ROTA INICIAL ---
    if queries.verificar_existencia_usuario():
        page.go("/login")
    else:
        page.go("/register")

if __name__ == "__main__":
    ft.app(target=main)
