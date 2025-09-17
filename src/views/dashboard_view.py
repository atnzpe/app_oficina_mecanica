# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DA VIEW DO DASHBOARD (dashboard_view.py)
#
# OBJETIVO: Definir a interface visual da tela principal, com um design
#           moderno e responsivo.
#
# SEÇÕES ALTERADAS NESTA REATORAÇÃO:
#   - CORREÇÃO CRÍTICA: A classe `DashboardView` agora herda de `ft.Column` em vez
#     da classe descontinuada `ft.UserControl`, para se alinhar com as novas
#     melhores práticas da API do Flet.
#   - O método `build()` foi removido. A definição dos controlos visíveis
#     foi movida para o final do `__init__` e atribuída a `self.controls`.
# =================================================================================
import flet as ft
from src.viewmodels.dashboard_viewmodel import DashboardViewModel


class DashboardView(ft.Column):
    """
    A View para a tela principal. Responsável apenas pela apresentação da UI.
    Herda de `ft.Column` para se renderizar diretamente.
    """

    def __init__(self, page: ft.Page):
        """
        Construtor. Inicializa a UI e conecta-se ao seu ViewModel.
        """
        super().__init__()
        self.page = page
        # Cada View cria a sua própria instância do ViewModel correspondente.
        self.view_model = DashboardViewModel(page)
        # A View informa ao ViewModel quem ela é, para comunicação bidirecional.
        self.view_model.vincular_view(self)

        # --- Definição dos Botões e Componentes ---
        # A View define os botões, mas a AÇÃO (on_click) é delegada ao ViewModel.
        self.botoes_dashboard = {
            "ordem_servico": ft.ElevatedButton("Nova Ordem de Serviço", on_click=self.view_model.abrir_form_os, icon=ft.icons.RECEIPT_LONG),
            # O componente de gerir clientes é, ele próprio, uma View.
            "gerir_clientes": self.view_model.editar_cliente_componente,
            "cadastrar_cliente": ft.ElevatedButton("Novo Cliente", on_click=self.view_model.abrir_cadastro_cliente, icon=ft.icons.PERSON_ADD),
            "cadastrar_carro": ft.ElevatedButton("Novo Veículo", on_click=self.view_model.abrir_cadastro_carro, icon=ft.icons.DIRECTIONS_CAR_ADD),
            "cadastrar_pecas": ft.ElevatedButton("Nova Peça", on_click=self.view_model.abrir_cadastro_peca, icon=ft.icons.ADD_SHOPPING_CART),
            "saldo_estoque": ft.ElevatedButton("Verificar Estoque", on_click=self.view_model.abrir_saldo_estoque, icon=ft.icons.INVENTORY_2),
            "relatorio": ft.ElevatedButton("Gerar Relatórios", on_click=self.view_model.abrir_relatorios, icon=ft.icons.ASSESSMENT),
        }

        # Como "gerir_clientes" é um componente complexo, configuramos as suas
        # propriedades visuais aqui, na View principal.
        gerir_clientes_component = self.botoes_dashboard["gerir_clientes"]
        if hasattr(gerir_clientes_component, 'controls') and isinstance(gerir_clientes_component.controls[0], ft.ElevatedButton):
            gerir_clientes_component.controls[0].icon = ft.icons.MANAGE_ACCOUNTS
            gerir_clientes_component.controls[0].text = "Gerir Clientes"

        # --- Estrutura da UI ---
        # A UI é construída diretamente no construtor e atribuída a `self.controls`.
        self.alignment = ft.MainAxisAlignment.START
        self.spacing = 20
        self.controls = [
            ft.GridView(
                controls=[
                    self._criar_cartao_de_acao("Operações Principais", [
                        self.botoes_dashboard["ordem_servico"],
                        self.botoes_dashboard["gerir_clientes"],
                    ]),
                    self._criar_cartao_de_acao("Cadastros", [
                        self.botoes_dashboard["cadastrar_cliente"],
                        self.botoes_dashboard["cadastrar_carro"],
                        self.botoes_dashboard["cadastrar_pecas"],
                    ]),
                    self._criar_cartao_de_acao("Consultas e Relatórios", [
                        self.botoes_dashboard["saldo_estoque"],
                        self.botoes_dashboard["relatorio"],
                    ]),
                ],
                expand=True,
                runs_count=5,
                max_extent=300,
                child_aspect_ratio=1.2,
                spacing=10,
                run_spacing=10,
            )
        ]
        # Inicia a atualização do estado dos botões.
        self.view_model.atualizar_estado_botoes_view()

    def _criar_cartao_de_acao(self, titulo: str, controles: list):
        """
        Função auxiliar para criar um `ft.Card` padronizado.
        Zen of Python: "Don't repeat yourself." (Não se repita).
        """
        return ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Column(
                    controls=[
                        ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=10),
                        *controles,
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ),
            elevation=4,
        )

    def atualizar_botoes(self, logado: bool):
        """
        Método público chamado pelo ViewModel para atualizar o estado visual.
        """
        # Itera sobre todos os botões e componentes para os habilitar/desabilitar
        for nome, componente in self.botoes_dashboard.items():
            componente.disabled = not logado
        self.update()


def DashboardViewFactory(page: ft.Page) -> ft.View:
    """
    Cria a View completa do Dashboard para o roteador.
    """
    # Cria o conteúdo principal da View.
    dashboard_content = DashboardView(page)

    # A lógica de logout agora fica no AppBar, que é parte da View.
    # O AppBar usa a mesma instância do ViewModel criada pelo dashboard_content.
    appbar = ft.AppBar(
        title=ft.Text("Dashboard - Oficina Guarulhos"),
        center_title=True,
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[
            ft.IconButton(
                ft.icons.LOGOUT, on_click=dashboard_content.view_model.logout, tooltip="Sair")
        ]
    )

    return ft.View(route="/dashboard", controls=[dashboard_content], appbar=appbar, padding=10)
