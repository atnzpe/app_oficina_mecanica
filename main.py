
# =================================================================================
# MÓDULO DE ENTRADA DA APLICAÇÃO (main.py) - VERSÃO 3.4
#
# ATUALIZAÇÃO:
#   - Adicionada a rota '/onboarding' para a tela de configuração da oficina.
# =================================================================================
import flet as ft
import threading
import logging

# Importações das View Factories
from src.views.login_view import LoginViewFactory
from src.views.dashboard_view import DashboardViewFactory
from src.views.register_view import RegisterViewFactory
from src.views.cadastro_cliente_view import CadastroClienteViewFactory
from src.views.onboarding_cliente_view import OnboardingClienteViewFactory
from src.views.onboarding_view import OnboardingViewFactory

# Importações de Serviços e Banco de Dados
from src.services.task_queue_service import processar_fila_db
from src.database.database import initialize_database as inicializar_banco_de_dados
from src.database import queries
from utils import criar_pastas

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s')

def main(page: ft.Page):
    """
    Função principal que inicializa e configura a aplicação Flet.
    """
    page.title = "Sistema OS Oficina Mecânica - v3.4"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_maximizable = True
    page.window_maximized = True

    # --- INICIALIZAÇÃO DE SERVIÇOS DE FUNDO ---
    logging.info("Iniciando serviços de fundo...")
    inicializar_banco_de_dados()
    thread_db = threading.Thread(target=processar_fila_db, args=(page,), daemon=True)
    thread_db.start()
    criar_pastas(".")

    # --- GERENCIADOR DE ROTAS ---
    def route_change(route):
        """Renderiza a View correta com base na rota atual da página."""
        logging.info(f"Navegando para a rota: {page.route}")
        page.views.clear()

        # Mapeamento de rotas para as View Factories
        if page.route == "/login":
            page.views.append(LoginViewFactory(page))
        elif page.route == "/register":
            page.views.append(RegisterViewFactory(page))
        # --- NOVA ROTA DE ONBOARDING DA OFICINA ---
        elif page.route == "/onboarding":
            page.views.append(OnboardingViewFactory(page))
        elif page.route == "/dashboard":
            page.views.append(DashboardViewFactory(page))
        elif page.route == "/cadastro_cliente":
            page.views.append(CadastroClienteViewFactory(page))
        elif page.route == "/onboarding_cliente":
            page.views.append(OnboardingClienteViewFactory(page))
        
        page.update()

    page.on_route_change = route_change

    # --- LÓGICA DE ROTA INICIAL ---
    if queries.verificar_existencia_usuario():
        page.go("/login")
    else:
        page.go("/register")

if __name__ == "__main__":
    ft.app(target=main)