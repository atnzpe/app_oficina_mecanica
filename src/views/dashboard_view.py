# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DA VIEW DO DASHBOARD (dashboard_view.py)
#
# CORREÇÃO (BUG FIX):
#   - Removida a chamada `self.view_model.atualizar_estado_botoes_view()` do
#     final do construtor para evitar o `AssertionError`.
#   - O estado inicial dos botões (`disabled`) agora é definido diretamente
#     durante a criação, com base no estado `usuario_atual` do ViewModel,
#     que já foi inicializado corretamente.
# =================================================================================
import flet as ft
from src.viewmodels.dashboard_viewmodel import DashboardViewModel
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
        
        # --- NOVO: Diálogo de Boas-Vindas ---
        # Define a aparência e o comportamento do pop-up.
        self._dialogo_primeiro_cliente = ft.AlertDialog(
            modal=True,
            title=ft.Text("Bem-vindo ao Sistema de Oficina!"),
            content=ft.Text("Percebemos que você ainda não tem clientes cadastrados. Deseja cadastrar o seu primeiro cliente agora?"),
            actions=[
                # O botão "Sim" delega a ação de volta para o ViewModel.
                ft.ElevatedButton("Sim, vamos lá!", on_click=self.view_model.abrir_cadastro_cliente),
                # O botão "Não" simplesmente fecha o diálogo.
                ft.TextButton("Não, obrigado", on_click=self._fechar_dialogo),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        

        # --- LÓGICA ATUALIZADA ---
        # Determina o estado de login a partir do ViewModel, que já leu a sessão.
        is_logged_in = self.view_model.usuario_atual is not None

        # --- Definição dos Botões e Componentes ---
        # O estado 'disabled' é definido na criação, com base em 'is_logged_in'.
        self.botoes_dashboard = {
            "ordem_servico": ft.ElevatedButton("Nova Ordem de Serviço", on_click=self.view_model.abrir_form_os, icon=ft.Icons.RECEIPT_LONG, disabled=not is_logged_in),
            "gerir_clientes": self.view_model.editar_cliente_componente,
            "cadastrar_cliente": ft.ElevatedButton("Novo Cliente", on_click=self.view_model.abrir_cadastro_cliente, icon=ft.Icons.PERSON_ADD, disabled=not is_logged_in),
            "cadastrar_carro": ft.ElevatedButton("Novo Veículo", on_click=self.view_model.abrir_cadastro_carro, icon=ft.Icons.DIRECTIONS_CAR, disabled=not is_logged_in),
            "cadastrar_pecas": ft.ElevatedButton("Nova Peça", on_click=self.view_model.abrir_cadastro_peca, icon=ft.Icons.ADD_SHOPPING_CART, disabled=not is_logged_in),
            "saldo_estoque": ft.ElevatedButton("Verificar Estoque", on_click=self.view_model.abrir_saldo_estoque, icon=ft.Icons.INVENTORY_2, disabled=not is_logged_in),
            "relatorio": ft.ElevatedButton("Gerar Relatórios", on_click=self.view_model.abrir_relatorios, icon=ft.Icons.ASSESSMENT, disabled=not is_logged_in),
        }

        # A lógica para o componente de gerir clientes também usa a flag.
        self.botoes_dashboard["gerir_clientes"].disabled = not is_logged_in
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
                expand=True, runs_count=5, max_extent=350,
                child_aspect_ratio=1.2, spacing=15, run_spacing=15,
            )
        ]

    # --- NOVOS MÉTODOS DA VIEW ---
    def mostrar_dialogo_primeiro_cliente(self):
        """Exibe o diálogo de boas-vindas na tela."""
        # Atribui o diálogo à página.
        self.page.dialog = self._dialogo_primeiro_cliente
        # Abre o diálogo.
        self._dialogo_primeiro_cliente.open = True
        # Atualiza a página para mostrar o diálogo.
        self.page.update()

    def fechar_dialogo(self, e):
        """Fecha o diálogo de boas-vindas."""
        self._dialogo_primeiro_cliente.open = False
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
                        ft.Text(titulo, size=AppFonts.BODY_LARGE,
                                weight=ft.FontWeight.BOLD),
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
