# =================================================================================
# MÓDULO DA VIEW DE GERENCIAMENTO DE CLIENTES (gerir_clientes_view.py)
#
# OBJETIVO: Criar a tela para listar e buscar clientes (funcionalidade READ).
# ATUALIZAÇÃO:
#   - Integrado o `style.py` para padronização da UI.
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

        # --- CORREÇÃO DO ERRO ---
        # O evento on_mount é atribuído aqui. Ele será chamado pelo Flet
        # assim que o controle for adicionado à página, garantindo que
        # `self.update()` possa ser chamado com segurança.
        self.on_mount = self.did_mount

        # --- Componentes Visuais ---
        self._campo_pesquisa = ft.TextField(
            label="Pesquisar por Nome, Telefone ou Placa",
            # A ação de submissão (Enter) aciona o método de pesquisa no ViewModel.
            on_submit=lambda e: self.view_model.pesquisar_cliente(
                self._campo_pesquisa.value),
            prefix_icon=ft.Icons.SEARCH,
            border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS)
        )

        # ListView para exibir os resultados da pesquisa de clientes.
        self._resultados_pesquisa_listview = ft.ListView(
            expand=True, spacing=10)

        # A lista de controles que compõem a view.
        self.controls = [
            self._campo_pesquisa,
            ft.Divider(),
            self._resultados_pesquisa_listview,
        ]

        # A chamada para carregar os dados foi REMOVIDA daqui para evitar o erro.
        # self.view_model.carregar_clientes_iniciais()

    def did_mount(self):
        """
        Este método é chamado pelo evento on_mount. É o local seguro para
        iniciar o carregamento de dados que atualizam a UI.
        """
        # Log para indicar que o método foi chamado.
        logging.info("GerirClientesView foi montada. Carregando clientes...")
        # Comanda o ViewModel a carregar a lista inicial de clientes.
        self.view_model.carregar_clientes_iniciais()

    def atualizar_lista_resultados(self, clientes: List[Cliente]):
        """Atualiza a ListView com os resultados da busca fornecidos pelo ViewModel."""
        # Limpa os resultados anteriores.
        self._resultados_pesquisa_listview.controls.clear()

        # Se a lista de clientes estiver vazia, exibe uma mensagem informativa.
        if not clientes:
            self._resultados_pesquisa_listview.controls.append(
                ft.Text("Nenhum cliente encontrado."))
        else:
            # Itera sobre a lista de clientes e cria um ListTile para cada um.
            for cliente in clientes:
                self._resultados_pesquisa_listview.controls.append(
                    ft.ListTile(
                        # Título do item da lista (nome do cliente).
                        title=ft.Text(cliente.nome, size=AppFonts.BODY_LARGE),
                        # Subtítulo com uma informação secundária (telefone).
                        subtitle=ft.Text(f"Telefone: {cliente.telefone}"),
                        # Ícone à direita para indicar que o item é clicável.
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                        # A ação de clique navega para a tela de edição do cliente.
                        on_click=lambda _, c=cliente: self.view_model.editar_cliente(
                            c.id),
                    )
                )
        # Este update agora é seguro, pois é chamado depois que a view foi montada.
        self.update()


def GerirClientesViewFactory(page: ft.Page) -> ft.View:
    """Cria a View completa para a rota /gerir_clientes."""
    view_content = GerirClientesView(page)

    return ft.View(
        route="/gerir_clientes",
        appbar=ft.AppBar(
            title=ft.Text("Gerenciar Clientes"),
            center_title=True,
            # Botão de voltar para o dashboard.
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS_NEW,
                on_click=lambda _: page.go("/dashboard"),
                tooltip="Voltar ao Dashboard"
            ),
            bgcolor=page.theme.color_scheme.surface,
        ),
        # --- NOVO FloatingActionButton ---
        # Adiciona um botão flutuante para criar um novo cliente, melhorando a UX.
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            tooltip="Cadastrar Novo Cliente",
            on_click=lambda _: page.go("/cadastro_cliente")
        ),
        floating_action_button2=ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            tooltip="Voltar ao Dashboard",
            on_click=lambda _: page.go("/dashboard")
        ),
        controls=[
            # Envolve o conteúdo com SafeArea e um Container para aplicar padding.
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
