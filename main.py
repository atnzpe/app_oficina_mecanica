# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE ENTRADA DA APLICAÇÃO (main.py) - VERSÃO 2.0
#
# OBJETIVO: Atuar como o roteador central da aplicação. Configura a página,
#           inicia serviços de fundo e gere a navegação entre as diferentes Views.
# =================================================================================
import flet as ft
import threading
import logging

from src.views.login_view import LoginView
from src.views.dashboard_view import DashboardView
from src.services.task_queue_service import processar_fila_db
from src.database.database import inicializar_banco_de_dados
from utils import criar_pastas

# Configuração do logger.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(page: ft.Page):
    """
    Função principal que inicializa e configura a aplicação Flet.
    """
    # --- CONFIGURAÇÃO INICIAL DA PÁGINA ---
    page.title = "Sistema OS Oficina Mecânica - v2.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1000
    page.window_height = 700
    page.window_min_width = 800
    page.window_min_height = 600
    page.padding = 0

    # --- INICIALIZAÇÃO DE SERVIÇOS DE FUNDO ---
    logging.info("Iniciando serviços de fundo...")
    inicializar_banco_de_dados()
    thread_db = threading.Thread(target=processar_fila_db, args=(page,), daemon=True)
    thread_db.start()
    criar_pastas(".")

    # --- GERENCIADOR DE ROTAS ---
    def route_change(route):
        """
        O coração do roteador. Decide qual View mostrar com base na rota.
        """
        logging.info(f"Navegando para a rota: {page.route}")
        
        # Cria um contêiner base para todas as Views, garantindo consistência.
        app_container = ft.Container(
            width=page.window_width,
            height=page.window_height,
            padding=ft.padding.all(20),
            alignment=ft.alignment.center,
        )
        
        page.views.clear()

        # Mapeamento de rotas para as Views
        if page.route == "/login":
            app_container.content = LoginView(page)
            page.views.append(ft.View(route="/login", controls=[app_container]))
        elif page.route == "/dashboard":
            app_container.content = DashboardView(page)
            page.views.append(ft.View(route="/dashboard", controls=[app_container]))
        else:
            # Rota padrão: redireciona para o login
            page.go("/login")
            return # Retorna para evitar a atualização da página antes do redirecionamento

        page.update()

    page.on_route_change = route_change
    # Inicia a aplicação na rota de login.
    page.go("/login")

# Ponto de entrada para iniciar a aplicação.
if __name__ == "__main__":
    ft.app(target=main)
