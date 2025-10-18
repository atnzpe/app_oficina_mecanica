# Local do Arquivo: main.py

# -*- coding: utf-8 -*-
# =================================================================================
# MÓDULO DE ENTRADA DA APLICAÇÃO (main.py)
#
# ATUALIZAÇÃO:
#   - Integração do módulo de estilos. Os temas claro e escuro agora são
#     carregados a partir de `src/styles/style.py` para uma UI consistente.
#   - Corrigida a aplicação de `extended_colors` para o tema.
# =================================================================================
import flet as ft
import threading
import logging
import re

# --- IMPORTAÇÃO DOS TEMAS E CORES PERSONALIZADAS ---
from src.styles.style import AppThemes, success_color_scheme

# Importações das View Factories
from src.views.login_view import LoginViewFactory
from src.views.dashboard_view import DashboardViewFactory
from src.views.register_view import RegisterViewFactory
from src.views.onboarding_view import OnboardingViewFactory
from src.views.cadastro_cliente_view import CadastroClienteViewFactory
from src.views.onboarding_cliente_view import OnboardingClienteViewFactory
from src.views.gerir_clientes_view import GerirClientesViewFactory
from src.views.editar_cliente_view import EditarClienteViewFactory
from src.views.gerir_carros_view import GerirCarrosViewFactory
from src.views.cadastro_carro_view import CadastroCarroViewFactory
from src.views.editar_carro_view import EditarCarroViewFactory
from src.views.gerir_pecas_view import GerirPecasViewFactory
from src.views.cadastro_peca_view import CadastroPecaViewFactory
from src.views.editar_peca_view import EditarPecaViewFactory
from src.views.gerir_mecanicos_view import GerirMecanicosViewFactory
from src.views.cadastro_mecanico_view import CadastroMecanicoViewFactory
from src.views.editar_mecanico_view import EditarMecanicoViewFactory
from src.views.gerir_servicos_view import GerirServicosViewFactory
from src.views.cadastro_servico_view import CadastroServicoViewFactory
from src.views.editar_servico_view import EditarServicoViewFactory
from src.views.minha_conta_view import MinhaContaViewFactory
from src.views.dados_oficina_view import DadosOficinaViewFactory
from src.views.entrada_pecas_view import EntradaPecasViewFactory

# Importações de Serviços e Banco de Dados
from src.services.task_queue_service import processar_fila_db
from src.database.database import initialize_database as inicializar_banco_de_dados
from src.database import queries
from utils import criar_pastas

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s')

# --- Factory Genérica para Telas em Desenvolvimento ---


def PlaceholderViewFactory(page: ft.Page, title: str) -> ft.View:
    return ft.View(
        route=page.route,
        appbar=ft.AppBar(title=ft.Text(title),
                         bgcolor=page.theme.color_scheme.surface_variant),
        controls=[ft.SafeArea(
            ft.Text(f"Tela de {title} em construção.", size=20))],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0
    )


def main(page: ft.Page):
    """
    Função principal que inicializa e configura a aplicação Flet.
    """
    page.title = "Sistema OS Oficina Mecânica"

    # --- APLICAÇÃO DOS TEMAS GLOBAIS ---
    page.theme = AppThemes.light_theme
    page.dark_theme = AppThemes.dark_theme

    # --- CORREÇÃO: Aplica as cores estendidas DEPOIS de definir os temas ---
    page.theme.extended_colors = [success_color_scheme]
    page.dark_theme.extended_colors = [success_color_scheme]

    # Define o tema inicial como escuro
    page.theme_mode = ft.ThemeMode.DARK

    page.window_maximizable = True
    page.window_maximized = True

    # --- INICIALIZAÇÃO DE SERVIÇOS DE FUNDO ---
    logging.info("Iniciando serviços de fundo...")
    inicializar_banco_de_dados()
    thread_db = threading.Thread(
        target=processar_fila_db, args=(page,), daemon=True)
    thread_db.start()
    criar_pastas(".")

    # --- GERENCIADOR DE ROTAS ---
    def route_change(route):
        logging.info(f"Navegando para a rota: {page.route}")
        edit_cliente_route = re.match(r"/editar_cliente/(\d+)", page.route)
        edit_carro_route = re.match(r"/editar_carro/(\d+)", page.route)
        edit_peca_route = re.match(r"/editar_peca/(\d+)", page.route)
        edit_mecanico_route = re.match(r"/editar_mecanico/(\d+)", page.route)
        edit_servico_route = re.match(r"/editar_servico/(\d+)", page.route)
        page.views.clear()

        # Mapeamento de rotas para as View Factories
        if page.route == "/login":
            page.views.append(LoginViewFactory(page))
        elif page.route == "/register":
            page.views.append(RegisterViewFactory(page))
        elif page.route == "/onboarding":
            page.views.append(OnboardingViewFactory(page))
        elif page.route == "/dashboard":
            page.views.append(DashboardViewFactory(page))

        # --- Rotas de Cadastro ---
        elif page.route == "/gerir_clientes":
            page.views.append(GerirClientesViewFactory(page))
        elif page.route == "/cadastro_cliente":
            page.views.append(CadastroClienteViewFactory(page))
        elif edit_cliente_route:
            cliente_id = int(edit_cliente_route.group(1))
            page.views.append(EditarClienteViewFactory(
                page, cliente_id=cliente_id))

        # --- ROTAS DE CARRO ---
        # gerir Carros
        elif page.route == "/gerir_carros":
            page.views.append(GerirCarrosViewFactory(page))
        # Cadastro Carro
        elif page.route == "/cadastro_carro":
            page.views.append(CadastroCarroViewFactory(page))
        # Editar Carro
        elif edit_carro_route:
            carro_id = int(edit_carro_route.group(1))
            page.views.append(EditarCarroViewFactory(page, carro_id=carro_id))

        # --- Rotas de Peças, Serviços e Mecânicos ---

        # -- ROTAS DE PEÇAS ---
        elif page.route == "/gerir_pecas":
            page.views.append(GerirPecasViewFactory(page))
        elif page.route == "/cadastro_peca":
            page.views.append(CadastroPecaViewFactory(page))

        elif edit_peca_route:  # -> Rota ativada
            peca_id = int(edit_peca_route.group(1))
            page.views.append(EditarPecaViewFactory(page, peca_id=peca_id))

        # --- NOVAS ROTAS DE MECÂNICOS ---
        elif page.route == "/gerir_mecanicos":
            page.views.append(GerirMecanicosViewFactory(page))
        elif page.route == "/cadastro_mecanico":
            page.views.append(CadastroMecanicoViewFactory(page))
        elif edit_mecanico_route:
            mecanico_id = int(edit_mecanico_route.group(1))
            page.views.append(EditarMecanicoViewFactory(
                page, mecanico_id=mecanico_id))

        # --- NOVAS ROTAS DE SERVIÇOS ---
        elif page.route == "/gerir_servicos":
            page.views.append(GerirServicosViewFactory(page))
        elif page.route == "/cadastro_servico":
            page.views.append(CadastroServicoViewFactory(page))
        elif edit_servico_route:
            servico_id = int(edit_servico_route.group(1))
            page.views.append(EditarServicoViewFactory(page, servico_id=servico_id))

        # --- Rotas de Ordem de Serviços ---
        elif page.route == "/nova_os":
            page.views.append(PlaceholderViewFactory(
                page, "Nova Ordem de Serviço"))
        elif page.route == "/novo_orcamento":
            page.views.append(PlaceholderViewFactory(page, "Novo Orçamento"))
        elif page.route == "/venda_pecas":
            page.views.append(PlaceholderViewFactory(page, "Venda de Peças"))

        # --- Rotas de Consultas e Relatórios ---
        elif page.route == "/entrada_pecas":
            # --- ROTA ATIVADA ---
            page.views.append(EntradaPecasViewFactory(page))
        elif page.route == "/estoque":
            page.views.append(PlaceholderViewFactory(page, "Estoque"))
        elif page.route == "/relatorios":
            page.views.append(PlaceholderViewFactory(page, "Relatórios"))

        # --- Rotas Administrativas ---
        elif page.route == "/minha_conta":
            page.views.append(MinhaContaViewFactory(page))
        #elif page.route == "/usuarios":
            #page.views.append(PlaceholderViewFactory(
                #page, "Gerenciar Usuários"))
        elif page.route == "/dados_oficina":
            # --- ROTA ATIVADA ---
            # Substitui o placeholder pela factory real
            page.views.append(DadosOficinaViewFactory(page))

        else:
            # Rota de fallback caso nenhuma corresponda
            page.views.append(DashboardViewFactory(page))

        page.update()

    page.on_route_change = route_change

    # --- LÓGICA DE ROTA INICIAL ---
    if queries.verificar_existencia_usuario():
        page.go("/login")
    else:
        page.go("/register")


if __name__ == "__main__":
    ft.app(target=main)
