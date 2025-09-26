# =================================================================================
# MÓDULO DE ENTRADA DA APLICAÇÃO (main.py) - VERSÃO 3.2
#
# OBJETIVO: Atuar como o roteador central da aplicação.
#
# ATUALIZAÇÃO:
#   - Adicionada a rota '/cadastro_cliente' para a nova tela de cadastro.
#   - A View de cadastro de cliente agora é uma página completa, não mais um modal.
# =================================================================================
import flet as ft
import threading
import logging

# Importações das Views (Factories que criam as páginas completas)
from src.views.login_view import LoginViewFactory
from src.views.dashboard_view import DashboardViewFactory
from src.views.register_view import RegisterViewFactory
from src.views.cadastro_cliente_view import CadastroClienteViewFactory
from src.views.onboarding_cliente_view import OnboardingClienteViewFactory

# Importações de Serviços e Banco de Dados
from src.services.task_queue_service import processar_fila_db
from src.database.database import initialize_database as inicializar_banco_de_dados
from src.database import queries
from utils import criar_pastas

# Configuração básica do logging para monitorar a aplicação.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s')

def main(page: ft.Page):
    """
    Função principal que inicializa e configura a aplicação Flet.
    """
    page.title = "Sistema OS Oficina Mecânica - v3.3"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_maximizable = True
    page.window_maximized = True

    # --- INICIALIZAÇÃO DE SERVIÇOS DE FUNDO ---
    logging.info("Iniciando serviços de fundo...")
    inicializar_banco_de_dados()
    # A thread do banco de dados processa operações (INSERT, UPDATE) de forma assíncrona.
    thread_db = threading.Thread(target=processar_fila_db, args=(page,), daemon=True)
    thread_db.start()
    criar_pastas(".")

    # --- GERENCIADOR DE ROTAS ---
    def route_change(route):
        """
        Esta função é chamada toda vez que a URL (rota) da página muda.
        Ela é responsável por limpar a tela e renderizar a View correta.
        """
        logging.info(f"Navegando para a rota: {page.route}")
        # Limpa a pilha de visualizações anterior para renderizar a nova.
        page.views.clear()

        # Mapeamento de rotas para as "View Factories".
        # Cada Factory é responsável por construir o objeto ft.View completo para aquela rota.
        if page.route == "/login":
            view = LoginViewFactory(page)
            page.views.append(view)
        elif page.route == "/register":
            view = RegisterViewFactory(page)
            page.views.append(view)
        elif page.route == "/dashboard":
            # --- Rota para a tela de Dashboard ---
            view = DashboardViewFactory(page)
            page.views.append(view)
        
        elif page.route == "/cadastro_cliente":
            # --- Rota para a tela de cadastro de cliente ---
            view = CadastroClienteViewFactory(page)
            page.views.append(view)
        elif page.route == "/onboarding_cliente":
            view = OnboardingClienteViewFactory(page)
            page.views.append(view)
        
        # Atualiza a página para mostrar a nova view.
        page.update()

    # Define a função que será executada sempre que a rota mudar.
    page.on_route_change = route_change

    # --- LÓGICA DE ROTA INICIAL ---
    # Ao iniciar o app, verifica se algum usuário já foi criado no banco.
    if queries.verificar_existencia_usuario():
        # Se existe, a primeira tela é a de login.
        page.go("/login")
    else:
        # Se não existe, a primeira tela é a de registro de um novo usuário.
        page.go("/register")

if __name__ == "__main__":
    ft.app(target=main)