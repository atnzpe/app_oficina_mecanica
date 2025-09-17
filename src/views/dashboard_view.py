# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DA VIEW DO DASHBOARD (dashboard_view.py)
#
# ATUALIZAÇÃO:
#   - Adicionada a importação do módulo de estilos.
#   - As propriedades visuais (padding, espaçamento, etc.) agora usam as
#     constantes de `AppDimensions` e `AppFonts` para consistência.
# =================================================================================
import flet as ft
from src.viewmodels.dashboard_viewmodel import DashboardViewModel
# --- NOVO: Importa os estilos ---
from src.styles.style import AppDimensions, AppFonts

class DashboardView(ft.Column):
    """
    A View para a tela principal. Responsável apenas pela apresentação da UI.
    """
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = DashboardViewModel(page)
        self.view_model.vincular_view(self)

        # --- Definição dos Botões e Componentes ---
        self.botoes_dashboard = {
            "ordem_servico": ft.ElevatedButton("Nova Ordem de Serviço", on_click=self.view_model.abrir_form_os, icon=ft.Icons.RECEIPT_LONG),
            "gerir_clientes": self.view_model.editar_cliente_componente,
            "cadastrar_cliente": ft.ElevatedButton("Novo Cliente", on_click=self.view_model.abrir_cadastro_cliente, icon=ft.Icons.PERSON_ADD),
            "cadastrar_carro": ft.ElevatedButton("Novo Veículo", on_click=self.view_model.abrir_cadastro_carro, icon=ft.Icons.DIRECTIONS_CAR_ADD),
            "cadastrar_pecas": ft.ElevatedButton("Nova Peça", on_click=self.view_model.abrir_cadastro_peca, icon=ft.Icons.ADD_SHOPPING_CART),
            "saldo_estoque": ft.ElevatedButton("Verificar Estoque", on_click=self.view_model.abrir_saldo_estoque, icon=ft.Icons.INVENTORY_2),
            "relatorio": ft.ElevatedButton("Gerar Relatórios", on_click=self.view_model.abrir_relatorios, icon=ft.Icons.ASSESSMENT),
        }

        gerir_clientes_component = self.botoes_dashboard["gerir_clientes"]
        if hasattr(gerir_clientes_component, 'controls') and isinstance(gerir_clientes_component.controls[0], ft.ElevatedButton):
            gerir_clientes_component.controls[0].icon = ft.Icons.MANAGE_ACCOUNTS
            gerir_clientes_component.controls[0].text = "Gerir Clientes"

        # --- Estrutura da UI ---
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
                max_extent=350, # Dimensão ajustada
                child_aspect_ratio=1.2,
                spacing=15,
                run_spacing=15,
            )
        ]
        self.view_model.atualizar_estado_botoes_view()

    def _criar_cartao_de_acao(self, titulo: str, controles: list):
        """
        Função auxiliar para criar um `ft.Card` padronizado.
        """
        return ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Column(
                    controls=[
                        ft.Text(titulo, size=AppFonts.BODY_LARGE, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=10),
                        *controles,
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH # Alinhamento melhorado
                )
            ),
            elevation=4,
        )

    def atualizar_botoes(self, logado: bool):
        """
        Método público chamado pelo ViewModel para atualizar o estado visual.
        """
        for componente in self.botoes_dashboard.values():
            componente.disabled = not logado
        self.update()

def DashboardViewFactory(page: ft.Page) -> ft.View:
    """
    Cria a View completa do Dashboard para o roteador.
    """
    dashboard_content = DashboardView(page)
    appbar = ft.AppBar(
        title=ft.Text("Dashboard - Oficina Mecânica"),
        center_title=True,
        bgcolor=ft.Colors.BLUE,
        actions=[
            ft.IconButton(
                ft.Icons.LOGOUT, on_click=dashboard_content.view_model.logout, tooltip="Sair")
        ]
    )
    return ft.View(route="/dashboard", controls=[dashboard_content], appbar=appbar, padding=10)