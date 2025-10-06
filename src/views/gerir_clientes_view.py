# =================================================================================
# MÓDULO DA VIEW DE GERENCIAMENTO DE CLIENTES (gerir_clientes_view.py)
#
# OBJETIVO: Criar a tela para listar e buscar clientes (funcionalidade READ).
# CORREÇÃO (Dialog Fix):
#   - Refatorada a exibição do diálogo de confirmação para usar `page.overlay`,
#     garantindo que o modal sempre apareça de forma confiável sobre a view.
# =================================================================================
import flet as ft
from src.viewmodels.gerir_clientes_viewmodel import GerirClientesViewModel
from src.models.models import Cliente
from typing import List
# Importa as classes de estilo para fontes e dimensões.
from src.styles.style import AppDimensions, AppFonts
import logging


class GerirClientesView(ft.Column):
    """
    A View para a tela de gerenciamento de clientes, responsável por exibir
    a lista de clientes e permitir a busca.
    """

    def __init__(self, page: ft.Page):
        # Chama o construtor da classe pai (ft.Column).
        super().__init__()

        # Armazena a referência da página principal do Flet.
        self.page = page

        # Instancia e vincula o ViewModel correspondente.
        self.view_model = GerirClientesViewModel(page)
        self.view_model.vincular_view(self)

        # O evento on_mount é atribuído para carregar os dados de forma segura.
        self.on_mount = self.did_mount

        # --- Componentes Visuais ---
        self._campo_pesquisa = ft.TextField(
            label="Pesquisar por Nome, Telefone ou Placa do Carro",
            on_submit=lambda e: self.view_model.pesquisar_cliente(
                self._campo_pesquisa.value),
            prefix_icon=ft.Icons.SEARCH,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS)
        )

        # ListView para exibir os resultados da pesquisa de clientes.
        self._resultados_pesquisa_listview = ft.ListView(
            expand=True, spacing=10)

        # --- Diálogo de Confirmação (será gerenciado pela página) ---
        # O diálogo é criado uma vez e reutilizado.
        self._confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Ação"),
            content=ft.Text(),  # O conteúdo será preenchido dinamicamente
            actions=[
                ft.TextButton(
                    "Cancelar", on_click=self.fechar_dialogo), # Evento de clique para fechar
                ft.ElevatedButton(
                    "Sim, Desativar",
                    # O clique aqui chama diretamente o método do ViewModel.
                    on_click=lambda _: self.view_model.confirmar_desativacao(),
                    bgcolor=ft.Colors.RED_700
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # A lista de controles que compõem a view.
        self.controls = [
            self._campo_pesquisa,
            ft.Divider(),
            self._resultados_pesquisa_listview,
        ]

    def did_mount(self):
        """
        Este método é chamado pelo evento on_mount. É o local seguro para
        iniciar o carregamento de dados que atualizam a UI.
        """
        logging.info("GerirClientesView foi montada. Carregando clientes...")
        # Atualiza a cor do botão do diálogo com base no tema.
        if self._confirm_dialog.actions:
             self._confirm_dialog.actions[1].bgcolor = ft.Colors.RED_700 if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.RED_400
        # Comanda o ViewModel a carregar a lista inicial de clientes.
        self.view_model.carregar_clientes_iniciais()

    def atualizar_lista_resultados(self, clientes: List[Cliente]):
        """Atualiza a ListView com os resultados da busca fornecidos pelo ViewModel."""
        self._resultados_pesquisa_listview.controls.clear()

        if not clientes:
            self._resultados_pesquisa_listview.controls.append(
                ft.Text("Nenhum cliente encontrado."))
        else:
            for cliente in clientes:
                list_item = ft.Container(
                    on_click=lambda _, c=cliente: self.view_model.editar_cliente(c.id),
                    border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
                    ink=True,
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                expand=True,
                                spacing=2,
                                controls=[
                                    ft.Text(cliente.nome, size=AppFonts.BODY_LARGE),
                                    ft.Text(f"Telefone: {cliente.telefone}", size=AppFonts.BODY_SMALL, color=ft.Colors.ON_SURFACE_VARIANT),
                                ]
                            ),
                            ft.Row(
                                spacing=0,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.PERSON_OFF,
                                        tooltip="Desativar Cliente",
                                        # O evento de clique é capturado pelo 'e' (evento)
                                        # para evitar que o clique se propague para o Container pai.
                                        on_click=lambda e, c=cliente: self.view_model.solicitar_desativacao(c.id, c.nome),
                                        icon_color=ft.Colors.RED_400,
                                    ),
                                    ft.Icon(ft.Icons.CHEVRON_RIGHT),
                                ]
                            )
                        ]
                    )
                )
                self._resultados_pesquisa_listview.controls.append(list_item)
        self.update()

    # --- MÉTODOS DA VIEW (CORRIGIDOS) ---

    def mostrar_dialogo_confirmacao(self, nome_cliente: str):
        """
        Exibe o diálogo de confirmação adicionando-o à camada de sobreposição (overlay).
        """
        # Garante que o diálogo não seja adicionado múltiplas vezes à overlay.
        if self._confirm_dialog not in self.page.overlay:
            self.page.overlay.append(self._confirm_dialog)
        
        # Personaliza a mensagem do diálogo.
        self._confirm_dialog.content.value = f"Tem certeza de que deseja desativar o cliente '{nome_cliente}'?\nEsta ação o removerá das listas ativas."
        # Abre o diálogo.
        self._confirm_dialog.open = True
        # Atualiza a página para exibir o diálogo.
        self.page.update()

    def fechar_dialogo(self, e=None): # Adicionado 'e=None' para ser chamado por botões
        """Fecha o diálogo de confirmação."""
        if self._confirm_dialog in self.page.overlay:
            self._confirm_dialog.open = False
            self.page.update()

    def mostrar_feedback(self, mensagem: str, sucesso: bool):
        """Exibe uma SnackBar para feedback ao usuário."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=self.page.theme.color_scheme.primary if sucesso else self.page.theme.color_scheme.error
        )
        self.page.snack_bar.open = True
        self.page.update()


def GerirClientesViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa para a rota /gerir_clientes."""
    view_content = GerirClientesView(page)

    return ft.View(
        route="/gerir_clientes",
        appbar=ft.AppBar(
            title=ft.Text("Gerenciar Clientes"),
            center_title=True,
            leading=None,
            automatically_imply_leading=False,
            bgcolor=page.theme.color_scheme.surface,
        ),
        floating_action_button=ft.Row(
            [
                ft.FloatingActionButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Voltar ao Dashboard",
                    on_click=lambda _: page.go("/dashboard")
                ),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    tooltip="Cadastrar Novo Cliente",
                    on_click=lambda _: page.go("/cadastro_cliente")
                )
            ],
            alignment=ft.MainAxisAlignment.END,
        ),
        controls=[
            ft.SafeArea(
                content=ft.Container(
                    content=view_content,
                    padding=AppDimensions.PAGE_PADDING
                ),
                expand=True
            )
        ],
        padding=0
    )