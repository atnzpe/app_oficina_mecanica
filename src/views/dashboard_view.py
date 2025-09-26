# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DA VIEW DO DASHBOARD (dashboard_view.py)
#
# CORREÇÃO (BUG FIX):
#   - O método `fechar_dialogos` foi corrigido para verificar se o atributo
#     `page.dialog` existe antes de tentar acessá-lo, evitando o `AttributeError`.
# =================================================================================
import flet as ft
from src.viewmodels.dashboard_viewmodel import DashboardViewModel
from src.styles.style import AppDimensions, AppFonts

class DashboardView(ft.Column):
    def __init__(self, page: ft.Page):
        """
        Construtor da View do Dashboard.
        """
        super().__init__()
        self.page = page
        self.view_model = DashboardViewModel(page)
        self._dialogo_primeiro_cliente = ft.AlertDialog(
            modal=True,
            title=ft.Text("Bem-vindo ao Sistema de Oficina!"),
            content=ft.Text("Percebemos que você ainda não tem clientes cadastrados. Deseja cadastrar o seu primeiro cliente agora?"),
            actions=[
                ft.ElevatedButton("Sim, vamos lá!", on_click=self.view_model.abrir_cadastro_cliente),
                ft.TextButton("Não, obrigado", on_click=self.fechar_dialogos),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.view_model.vincular_view(self)

        

        is_logged_in = self.view_model.usuario_atual is not None

        # ... (código dos botões e GridView permanece o mesmo) ...
        self.botoes_dashboard = {
            "ordem_servico": ft.ElevatedButton("Nova Ordem de Serviço", on_click=self.view_model.abrir_form_os, icon=ft.Icons.RECEIPT_LONG, disabled=not is_logged_in),
            "gerir_clientes": self.view_model.editar_cliente_componente,
            "cadastrar_cliente": ft.ElevatedButton("Novo Cliente", on_click=self.view_model.abrir_cadastro_cliente, icon=ft.Icons.PERSON_ADD, disabled=not is_logged_in),
            "cadastrar_carro": ft.ElevatedButton("Novo Veículo", on_click=self.view_model.abrir_cadastro_carro, icon=ft.Icons.DIRECTIONS_CAR, disabled=not is_logged_in),
            "cadastrar_pecas": ft.ElevatedButton("Nova Peça", on_click=self.view_model.abrir_cadastro_peca, icon=ft.Icons.ADD_SHOPPING_CART, disabled=not is_logged_in),
            "saldo_estoque": ft.ElevatedButton("Verificar Estoque", on_click=self.view_model.abrir_saldo_estoque, icon=ft.Icons.INVENTORY_2, disabled=not is_logged_in),
            "relatorio": ft.ElevatedButton("Gerar Relatórios", on_click=self.view_model.abrir_relatorios, icon=ft.Icons.ASSESSMENT, disabled=not is_logged_in),
        }
        self.botoes_dashboard["gerir_clientes"].disabled = not is_logged_in
        gerir_clientes_component = self.botoes_dashboard["gerir_clientes"]
        if hasattr(gerir_clientes_component, 'controls') and isinstance(gerir_clientes_component.controls[0], ft.ElevatedButton):
            gerir_clientes_component.controls[0].icon = ft.Icons.MANAGE_ACCOUNTS
            gerir_clientes_component.controls[0].text = "Gerir Clientes"
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
                expand=True, runs_count=5, max_extent=350,
                child_aspect_ratio=1.2, spacing=15, run_spacing=15,
            )
        ]

    def mostrar_dialogo_primeiro_cliente(self):
        """Exibe o diálogo de boas-vindas na tela."""
        self.page.dialog = self._dialogo_primeiro_cliente
        self._dialogo_primeiro_cliente.open = True
        self.page.update()

    # --- MÉTODO CORRIGIDO ---
    def fechar_dialogos(self, e=None):
        """Fecha de forma segura qualquer diálogo que a página possa ter aberto."""
        # Verifica se o atributo 'dialog' existe na página E se ele não é None.
        if hasattr(self.page, "dialog") and self.page.dialog is not None:
            self.page.dialog.open = False
            self.page.update()
        
    def mostrar_feedback(self, mensagem: str, sucesso: bool):
        """Exibe uma SnackBar para feedback ao usuário."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _criar_cartao_de_acao(self, titulo: str, controles: list):
        """Função auxiliar para criar um `ft.Card` padronizado."""
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
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH
                )
            ),
            elevation=4,
        )

    def atualizar_botoes(self, logado: bool):
        """Método público chamado pelo ViewModel para ATUALIZAÇÕES futuras."""
        for componente in self.botoes_dashboard.values():
            componente.disabled = not logado
        self.update()

def DashboardViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa do Dashboard para o roteador."""
    dashboard_content = DashboardView(page)
    appbar = ft.AppBar(
        title=ft.Text("Dashboard - Oficina Mecânica"),
        center_title=True,
        bgcolor=ft.Colors.SURFACE,
        actions=[
            ft.IconButton(
                ft.Icons.LOGOUT, on_click=dashboard_content.view_model.logout, tooltip="Sair")
        ]
    )
    return ft.View(route="/dashboard", controls=[dashboard_content], appbar=appbar, padding=10)