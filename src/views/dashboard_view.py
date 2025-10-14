# =================================================================================
# MÓDULO DA VIEW DO DASHBOARD (dashboard_view.py)
#
# ATUALIZAÇÃO (UX/Organização):
#   - Reorganizados os itens de navegação para agrupar todos os cadastros
#     (Peças, Mecânicos, Serviços) sob o card "Administrativo".
# =================================================================================
import flet as ft
from src.viewmodels.dashboard_viewmodel import DashboardViewModel
from src.styles.style import AppFonts, AppDimensions


class DashboardView(ft.Column):
    """
    A nova View do Dashboard, organizada em Cards de funcionalidades.
    """

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.view_model = DashboardViewModel(page)
        self.view_model.vincular_view(self)
        self.appbar: ft.AppBar | None = None
        self.spacing = 20
        self.expand = True
        self.scroll = ft.ScrollMode.ADAPTIVE

        # --- Estrutura da View ---
        self.controls = [
            # Card de Cadastros (Agora focado em Clientes e Veículos)
            self._criar_card_principal(
                titulo="Cadastros",
                cor=ft.Colors.BLUE_GREY_800,
                conteudo=[
                    self._criar_sub_item(
                        "Clientes", ft.Icons.PEOPLE_OUTLINED, "/gerir_clientes"),
                    self._criar_sub_item(
                        "Veículos", ft.Icons.DIRECTIONS_CAR_OUTLINED, "/gerir_carros"),
                ]
            ),
            # Card de Serviços (Operacional)
            self._criar_card_principal(
                titulo="Serviços",
                cor=ft.Colors.TEAL_800,
                conteudo=[
                    self._criar_sub_item(
                        "Nova Ordem de Serviço", ft.Icons.RECEIPT_LONG_OUTLINED, "/nova_os"),
                    self._criar_sub_item(
                        "Gerar Orçamento", ft.Icons.CALCULATE_OUTLINED, "/novo_orcamento"),
                    self._criar_sub_item(
                        "Vender Peças", ft.Icons.POINT_OF_SALE_OUTLINED, "/venda_pecas"),
                ]
            ),
            # Card Administrativo (Agora centraliza todos os outros cadastros)
            self._criar_card_principal(
                titulo="Administrativo",
                cor=ft.Colors.INDIGO_800,
                conteudo=[
                    self._criar_sub_item(
                        "Peças e Estoque", ft.Icons.INVENTORY_2_OUTLINED, "/gerir_pecas"),
                    self._criar_sub_item(
                        "Mecânicos", ft.Icons.ENGINEERING_OUTLINED, "/gerir_mecanicos"),
                    self._criar_sub_item(
                        "Serviços", ft.Icons.MISCELLANEOUS_SERVICES_OUTLINED, "/gerir_servicos"),
                    self._criar_sub_item(
                        "Usuários", ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED, "/usuarios"),
                    self._criar_sub_item(
                        "Dados da Oficina", ft.Icons.STORE_OUTLINED, "/dados_oficina"),
                    self._criar_sub_item(
                        "Relatórios", ft.Icons.ASSESSMENT_OUTLINED, "/relatorios"),
                ]
            ),
        ]

    def _criar_card_principal(self, titulo: str, cor: str, conteudo: list) -> ft.Card:
        """Função auxiliar para criar um Card principal padronizado."""
        return ft.Card(
            elevation=AppDimensions.CARD_ELEVATION,
            content=ft.Container(
                bgcolor=cor,
                border_radius=ft.border_radius.all(
                    AppDimensions.BORDER_RADIUS),
                padding=AppDimensions.PAGE_PADDING,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text(titulo, size=AppFonts.TITLE_MEDIUM,
                                weight=ft.FontWeight.BOLD),
                        ft.Divider(height=5, color=ft.Colors.WHITE24),
                        *conteudo
                    ]
                )
            )
        )

    def _criar_sub_item(self, texto: str, icone: str, rota: str) -> ft.Container:
        """Função auxiliar para criar um item de navegação (botão) dentro de um Card."""
        return ft.Container(
            on_click=lambda _: self.view_model.navigate(rota),
            border_radius=ft.border_radius.all(
                AppDimensions.BORDER_RADIUS - 2),
            ink=True,
            padding=ft.padding.symmetric(vertical=8, horizontal=12),
            content=ft.ListTile(
                title=ft.Text(texto, size=AppFonts.BODY_MEDIUM),
                leading=ft.Icon(icone),
                trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
            )
        )

    def atualizar_icone_tema(self, theme_mode: ft.ThemeMode):
        """Atualiza o ícone do botão de tema na AppBar."""
        if self.appbar:
            if theme_mode == ft.ThemeMode.DARK:
                self.appbar.actions[0].icon = ft.Icons.LIGHT_MODE_OUTLINED
                self.appbar.actions[0].tooltip = "Mudar para Tema Claro"
            else:
                self.appbar.actions[0].icon = ft.Icons.DARK_MODE_OUTLINED
                self.appbar.actions[0].tooltip = "Mudar para Tema Escuro"
            self.appbar.update()


def DashboardViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa do Dashboard para o roteador."""
    dashboard_content = DashboardView(page)
    initial_icon = ft.Icons.LIGHT_MODE_OUTLINED if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE_OUTLINED
    initial_tooltip = "Mudar para Tema Claro" if page.theme_mode == ft.ThemeMode.DARK else "Mudar para Tema Escuro"
    appbar = ft.AppBar(
        title=ft.Text("Dashboard - Oficina Mecânica"),
        center_title=True,
        bgcolor=page.theme.color_scheme.surface,
        actions=[
            ft.IconButton(
                icon=initial_icon,
                tooltip=initial_tooltip,
                on_click=dashboard_content.view_model.change_theme
            ),
            ft.IconButton(
                ft.Icons.LOGOUT,
                on_click=dashboard_content.view_model.logout,
                tooltip="Sair"
            )
        ]
    )
    dashboard_content.appbar = appbar
    return ft.View(
        route="/dashboard",
        appbar=appbar,
        controls=[ft.SafeArea(content=dashboard_content, expand=True)],
        padding=0
    )