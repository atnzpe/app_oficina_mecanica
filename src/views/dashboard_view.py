# Compartilhe aqui o CÓDIGO COMPLETO da View.
# O código deve estar comentado.

# -*- coding: utf-8 -*-
# =================================================================================
# MÓDULO DA VIEW DO DASHBOARD (dashboard_view.py)
#
# REATORAÇÃO:
#   - A UI foi completamente redesenhada para uma estrutura de Cards organizados.
#   - Os botões agora são `ListTile` para um visual mais limpo e profissional.
#   - A navegação é 100% baseada em rotas.
#   - Adicionado `SafeArea` e botão de troca de tema na Factory.
#   - Integrado o `style.py` para padronização da UI.
# =================================================================================
import flet as ft
from src.viewmodels.dashboard_viewmodel import DashboardViewModel
# Importa as classes de estilo para fontes e dimensões.
from src.styles.style import AppFonts, AppDimensions


class DashboardView(ft.Column):
    """
    A nova View do Dashboard, organizada em Cards de funcionalidades.
    """

    def __init__(self, page: ft.Page):
        # Chama o construtor da classe pai (ft.Column).
        super().__init__()

        # Armazena a referência da página e instancia o ViewModel.
        self.page = page
        self.view_model = DashboardViewModel(page)
        self.view_model.vincular_view(self)

        # Atributo para armazenar a referência da AppBar e poder atualizá-la.
        self.appbar: ft.AppBar | None = None

        # --- Configurações da coluna principal ---
        self.spacing = 20  # Espaçamento vertical entre os cards.
        # Garante que a coluna ocupe todo o espaço vertical disponível.
        self.expand = True
        # Habilita a rolagem automática em telas menores.
        self.scroll = ft.ScrollMode.ADAPTIVE

        # --- Estrutura da View ---
        # A lista de controles (os cards) que compõem o dashboard.
        self.controls = [
            # Card de Cadastros
            self._criar_card_principal(
                titulo="Cadastros",
                cor=ft.Colors.BLUE_GREY_800,
                conteudo=[
                    self._criar_sub_item(
                        "Clientes", ft.Icons.PEOPLE_OUTLINED, "/gerir_clientes"),
                    self._criar_sub_item(
                        "Veículos", ft.Icons.DIRECTIONS_CAR_OUTLINED, "/gerir_veiculos"),
                    self._criar_sub_item(
                        "Peças", ft.Icons.SETTINGS_INPUT_COMPONENT_OUTLINED, "/gerir_pecas"),
                    self._criar_sub_item(
                        "Serviços", ft.Icons.MISCELLANEOUS_SERVICES_OUTLINED, "/gerir_servicos"),
                    self._criar_sub_item(
                        "Mecânicos", ft.Icons.ENGINEERING_OUTLINED, "/gerir_mecanicos"),
                ]
            ),
            # Card de Serviços
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
            # Card de Consultas e Relatórios
            self._criar_card_principal(
                titulo="Consultas e Relatórios",
                cor=ft.Colors.INDIGO_800,
                conteudo=[
                    self._criar_sub_item(
                        "Entrada de Peças", ft.Icons.INPUT_OUTLINED, "/entrada_pecas"),
                    self._criar_sub_item(
                        "Verificar Estoque", ft.Icons.INVENTORY_2_OUTLINED, "/estoque"),
                    self._criar_sub_item(
                        "Relatórios", ft.Icons.ASSESSMENT_OUTLINED, "/relatorios"),
                ]
            ),
            # Card Administrativo
            self._criar_card_principal(
                titulo="Administrativo",
                cor=ft.Colors.GREY_800,
                conteudo=[
                    self._criar_sub_item(
                        "Minha Conta", ft.Icons.ACCOUNT_CIRCLE_OUTLINED, "/minha_conta"),
                    self._criar_sub_item(
                        "Usuários", ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED, "/usuarios"),
                    self._criar_sub_item(
                        "Dados da Oficina", ft.Icons.STORE_OUTLINED, "/dados_oficina"),
                ]
            ),
        ]

    def _criar_card_principal(self, titulo: str, cor: str, conteudo: list) -> ft.Card:
        """Função auxiliar para criar um Card principal padronizado."""
        return ft.Card(
            # Usa a elevação padrão para consistência.
            elevation=AppDimensions.CARD_ELEVATION,
            content=ft.Container(
                bgcolor=cor,
                # Usa o raio de borda padrão.
                border_radius=ft.border_radius.all(
                    AppDimensions.BORDER_RADIUS),
                padding=AppDimensions.PAGE_PADDING,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        # Título do card, usando a fonte padrão para títulos médios.
                        ft.Text(titulo, size=AppFonts.TITLE_MEDIUM,
                                weight=ft.FontWeight.BOLD),
                        ft.Divider(height=5, color=ft.Colors.WHITE24),
                        # Desempacota a lista de sub-itens (ListTiles) dentro da coluna.
                        *conteudo
                    ]
                )
            )
        )

    def _criar_sub_item(self, texto: str, icone: str, rota: str) -> ft.Container:
        """
        Função auxiliar para criar um item de navegação (botão) dentro de um Card.
        Retorna um Container para suportar border_radius e efeitos de hover.
        """
        return ft.Container(
            # O Container agora é o elemento clicável, delegando a navegação ao ViewModel.
            on_click=lambda _: self.view_model.navigate(rota),
            # Propriedades visuais aplicadas ao Container.
            border_radius=ft.border_radius.all(
                AppDimensions.BORDER_RADIUS - 2),  # Um pouco menor que o card
            ink=True,  # Efeito de ondulação ao clicar.
            padding=ft.padding.symmetric(vertical=8, horizontal=12),

            # O ListTile agora vive DENTRO do Container.
            content=ft.ListTile(
                # Fonte padrão para corpo de texto.
                title=ft.Text(texto, size=AppFonts.BODY_MEDIUM),
                leading=ft.Icon(icone),
                trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                # O on_click foi removido daqui e passado para o Container.
            )
        )

    def atualizar_icone_tema(self, theme_mode: ft.ThemeMode):
        """Atualiza o ícone do botão de tema na AppBar, comandado pelo ViewModel."""
        if self.appbar:
            if theme_mode == ft.ThemeMode.DARK:
                self.appbar.actions[0].icon = ft.Icons.LIGHT_MODE_OUTLINED
                self.appbar.actions[0].tooltip = "Mudar para Tema Claro"
            else:
                self.appbar.actions[0].icon = ft.Icons.DARK_MODE_OUTLINED
                self.appbar.actions[0].tooltip = "Mudar para Tema Escuro"
            # Atualiza apenas a AppBar, o que é mais eficiente do que atualizar a página inteira.
            self.appbar.update()


def DashboardViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa do Dashboard para o roteador."""
    dashboard_content = DashboardView(page)

    # Define o ícone inicial do botão de tema com base no tema atual da página.
    initial_icon = ft.Icons.LIGHT_MODE_OUTLINED if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE_OUTLINED
    initial_tooltip = "Mudar para Tema Claro" if page.theme_mode == ft.ThemeMode.DARK else "Mudar para Tema Escuro"

    # Cria a AppBar da página do Dashboard.
    appbar = ft.AppBar(
        title=ft.Text("Dashboard - Oficina Mecânica"),
        center_title=True,
        bgcolor=page.theme.color_scheme.surface,
        actions=[
            # Botão de Troca de Tema
            ft.IconButton(
                icon=initial_icon,
                tooltip=initial_tooltip,
                on_click=dashboard_content.view_model.change_theme
            ),
            # Botão de Logout
            ft.IconButton(
                ft.Icons.LOGOUT,
                on_click=dashboard_content.view_model.logout,
                tooltip="Sair"
            )
        ]
    )

    # Associa a appbar criada à instância da view para que ela possa ser atualizada.
    dashboard_content.appbar = appbar

    return ft.View(
        route="/dashboard",
        appbar=appbar,
        controls=[
            # Envolve o conteúdo principal com o SafeArea.
            ft.SafeArea(
                content=dashboard_content,
                expand=True
            )
        ],
        # O padding agora será controlado pelo SafeArea e pelos containers internos.
        padding=0
    )
