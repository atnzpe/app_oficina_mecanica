from src.styles.style import AppDimensions, AppFonts
from src.models.models import Cliente
from src.viewmodels.editar_cliente_viewmodel import EditarClienteViewModel
import flet as ft
Com certeza! Continuamos o processo de refatoração, garantindo uma interface coesa e de fácil manutenção.

Os próximos dois arquivos que vamos padronizar são a tela de edição de cliente, que é a continuação natural do CRUD de clientes, e a tela de Ordem de Serviço, que é uma das mais complexas e importantes.

PROPOSTA DE ATUALIZAÇÃO(1/2)
1. MENSAGEM DE COMMIT
feat(ui): Aplica style.py à EditarClienteView para consistência no CRUD

Refatora a `editar_cliente_view.py` para utilizar as constantes de design globais(`AppFonts`, `AppDimensions`) de `src/styles/style.py`. Esta alteração garante que o formulário de edição de cliente seja visualmente consistente com as telas de listagem e cadastro.

- Padroniza os campos de texto e botões com as dimensões e raios de borda do design system.
- Aplica a escala de fontes padronizada para o título da página e outros elementos textuais.
- Melhora a legibilidade e a manutenibilidade do código da view.
2. ANÁLISE DA SOLICITAÇÃO
A tarefa é aplicar nosso design system centralizado em style.py à tela de edição de clientes(src/views/editar_cliente_view.py). O objetivo é substituir os valores estáticos por constantes, garantindo que a experiência do usuário ao editar um cliente seja coesa com o resto da aplicação.

As modificações serão focadas exclusivamente na camada View:

View(src/views/editar_cliente_view.py): O arquivo será alterado para importar AppFonts e AppDimensions. As propriedades dos componentes visuais(TextField, ElevatedButton, Text) serão atualizadas para usar as constantes do style.py. Adicionarei comentários detalhados a cada linha.

3. ARQUIVOS MODIFICADOS/CRIADOS
(View: src/views/editar_cliente_view.py)

Python

# =================================================================================
# MÓDULO DA VIEW DE EDIÇÃO DE CLIENTE (editar_cliente_view.py)
#
# REATORAÇÃO (CRUD):
#   - A View foi transformada em uma tela completa, controlada pela rota
#     /editar_cliente/:id, substituindo o antigo sistema de modais.
#   - Integrado o `style.py` para padronização da UI.
# =================================================================================
# Importa as classes de estilo para fontes e dimensões.


class EditarClienteView(ft.Column):
    """
    A View para o formulário de edição de clientes como uma página completa.
    """

    def __init__(self, page: ft.Page, cliente_id: int):
        # Chama o construtor da classe pai (ft.Column).
        super().__init__()

        # Armazena referências da página e instancia o ViewModel.
        self.page = page
        self.view_model = EditarClienteViewModel(page, cliente_id)
        self.view_model.vincular_view(self)

        # --- Componentes Visuais ---
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.CENTER
        self.spacing = 15

        # Campos de texto padronizados com as dimensões e raios de borda do style.py.
        self._campo_nome = ft.TextField(label="Nome", width=AppDimensions.FIELD_WIDTH,
                                        border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._campo_telefone = ft.TextField(
            label="Telefone", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._campo_endereco = ft.TextField(
            label="Endereço", width=AppDimensions.FIELD_WIDTH, border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))
        self._campo_email = ft.TextField(label="Email", width=AppDimensions.FIELD_WIDTH,
                                         border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS))

        # Botão para desativar o cliente.
        self._desativar_btn = ft.ElevatedButton(
            "Desativar Cliente",
            icon=ft.Icons.DELETE_FOREVER,
            # Cores devem ser obtidas do tema para garantir contraste.
            color=self.page.theme.color_scheme.on_error,
            bgcolor=self.page.theme.color_scheme.error,
            on_click=lambda _: self.view_model.solicitar_desativacao_cliente()
        )

        # Botão para salvar as alterações.
        self._salvar_btn = ft.ElevatedButton(
            "Salvar Alterações", icon=ft.Icons.SAVE, on_click=self._on_salvar_click)

        # Diálogo de confirmação para a ação de desativar.
        self._dlg_confirmar_desativacao = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Ação"),
            content=ft.Text(
                "Tem certeza de que deseja desativar este cliente? Esta ação o removerá das listas ativas."),
            actions=[
                ft.TextButton(
                    "Cancelar", on_click=self.fechar_todos_os_modais),
                ft.ElevatedButton(
                    "Sim, Desativar",
                    on_click=self.view_model.confirmar_desativacao_cliente,
                    bgcolor=self.page.theme.color_scheme.error
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        # --- Estrutura da View ---
        self.controls = [
            ft.Text("Editando Cliente", size=AppFonts.TITLE_MEDIUM,
                    weight=ft.FontWeight.BOLD),
            self._campo_nome,
            self._campo_telefone,
            self._campo_endereco,
            self._campo_email,
            # Linha para organizar os botões de ação.
            ft.Row(
                [self._desativar_btn, self._salvar_btn],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                width=AppDimensions.FIELD_WIDTH
            )
        ]

        # Comanda o ViewModel para carregar os dados do cliente assim que a view for criada.
        self.view_model.carregar_dados_cliente()

    def preencher_formulario(self, cliente: Cliente):
        """Preenche os campos do formulário com os dados do cliente."""
        self._campo_nome.value = cliente.nome
        self._campo_telefone.value = cliente.telefone
        self._campo_endereco.value = cliente.endereco
        self._campo_email.value = cliente.email
        self.update()

    def _on_salvar_click(self, e):
        """Coleta os dados do formulário e os envia ao ViewModel para salvar."""
        novos_dados = {
            "nome": self._campo_nome.value,
            "telefone": self._campo_telefone.value,
            "endereco": self._campo_endereco.value,
            "email": self._campo_email.value,
        }
        self.view_model.salvar_alteracoes(novos_dados)

    def abrir_modal_confirmacao_desativar(self):
        """Abre o diálogo de confirmação para desativar o cliente."""
        self.page.dialog = self._dlg_confirmar_desativacao
        self._dlg_confirmar_desativacao.open = True
        self.page.update()

    def fechar_todos_os_modais(self, e=None):
        """Fecha qualquer modal aberto por esta view."""
        if self.page.dialog == self._dlg_confirmar_desativacao:
            self.page.dialog.open = False
            self.page.update()

    def mostrar_feedback(self, mensagem: str, success: bool):
        """Exibe uma SnackBar para feedback ao usuário."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=self.page.theme.color_scheme.primary if success else self.page.theme.color_scheme.error
        )
        self.page.snack_bar.open = True
        self.page.update()


def EditarClienteViewFactory(page: ft.Page, cliente_id: int) -> ft.View:
    """Cria a View completa para a rota /editar_cliente/:id."""
    return ft.View(
        route=f"/editar_cliente/{cliente_id}",
        appbar=ft.AppBar(
            title=ft.Text("Editar Cliente"),
            center_title=True,
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS_NEW,
                on_click=lambda _: page.go("/gerir_clientes"),
                tooltip="Voltar para a Lista"
            ),
            bgcolor=page.theme.color_scheme.surface,
        ),
        controls=[
            ft.Container(
                content=EditarClienteView(page, cliente_id),
                alignment=ft.alignment.center,
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=AppDimensions.PAGE_PADDING
    )
