# =================================================================================
# MÓDULO DA VIEW DO FORMULÁRIO DE OS (os_formulario_view.py)
#
# ATUALIZAÇÃO:
#   - Adicionada a importação do módulo de estilos.
#   - Todos os componentes visuais foram padronizados com as constantes de
#     `AppDimensions` e `AppFonts`.
# =================================================================================
import flet as ft
import logging
from typing import List
from src.models.models import Cliente, Carro, Peca
from src.viewmodels.os_formulario_viewmodel import OrdemServicoFormularioViewModel
# --- Importa os estilos ---
from src.styles.style import AppFonts, AppDimensions


class OrdemServicoFormularioView:
    """
    A View para o formulário de OS. Gera o modal e delega ações ao ViewModel.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.view_model = OrdemServicoFormularioViewModel(page)
        self.view_model.vincular_view(self)

        # --- Componentes de UI Padronizados ---
        self._cliente_dropdown = ft.Dropdown(
            hint_text="Selecione um cliente", on_change=self._on_cliente_selecionado, expand=True, border_radius=AppDimensions.BORDER_RADIUS)
        self._carro_dropdown = ft.Dropdown(
            hint_text="Selecione um carro", expand=True, border_radius=AppDimensions.BORDER_RADIUS)
        self._peca_dropdown = ft.Dropdown(
            hint_text="Selecione uma peça", expand=True, border_radius=AppDimensions.BORDER_RADIUS)
        self._quantidade_field = ft.TextField(
            label="Qtd.", width=80, value="1", border_radius=AppDimensions.BORDER_RADIUS)
        self._mao_de_obra_field = ft.TextField(label="Mão de Obra (R$)", width=150, value="0.0",
                                               on_change=self._on_valor_alterado, border_radius=AppDimensions.BORDER_RADIUS)
        self._adicionar_peca_button = ft.ElevatedButton(
            "Adicionar Peça", icon=ft.Icons.ADD, on_click=self._on_adicionar_peca)
        self._pecas_list_view = ft.ListView(expand=True, spacing=10)
        self._valor_total_text = ft.Text(
            "Valor Total: R$ 0.00", size=AppFonts.BODY_LARGE, weight=ft.FontWeight.BOLD)

        # --- Diálogo Principal (Modal) ---
        self._dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Criar Nova Ordem de Serviço",
                          size=AppFonts.TITLE_MEDIUM),
            content=ft.Column(
                controls=[
                    ft.Row([self._cliente_dropdown, self._carro_dropdown]),
                    ft.Divider(),
                    ft.Row([self._peca_dropdown, self._quantidade_field],
                           alignment=ft.MainAxisAlignment.START),
                    self._adicionar_peca_button,
                    ft.Divider(),
                    ft.Text("Peças Adicionadas:", weight=ft.FontWeight.BOLD),
                    self._pecas_list_view,
                    ft.Divider(),
                    ft.Row([self._mao_de_obra_field, self._valor_total_text],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ],
                # Define um tamanho fixo para o conteúdo do modal.
                width=800,
                height=500,
                # Habilita a rolagem se o conteúdo exceder a altura.
                scroll=ft.ScrollMode.ADAPTIVE,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_modal),
                ft.ElevatedButton("Criar OS", icon=ft.Icons.SAVE_OUTLINED,
                                  on_click=self._on_processar_criacao_os),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def abrir_modal(self, e):
        """Abre o modal da OS, limpa o formulário e carrega dados iniciais."""
        self._limpar_formulario()
        self.view_model.carregar_dados_iniciais()
        self.page.dialog = self._dlg
        self._dlg.open = True
        self.page.update()

    def fechar_modal(self, e=None):
        """Fecha o modal da OS."""
        self._dlg.open = False
        self.page.update()

    def popular_dropdowns_iniciais(self, clientes: List[Cliente], pecas: List[Peca]):
        """Preenche os dropdowns de clientes e peças com dados do ViewModel."""
        self._cliente_dropdown.options = [ft.dropdown.Option(
            key=cliente.id, text=cliente.nome) for cliente in clientes]
        self._peca_dropdown.options = [ft.dropdown.Option(
            key=peca.id, text=f"{peca.nome} (Ref: {peca.referencia})") for peca in pecas]
        self.page.update()

    def popular_dropdown_carros(self, carros: List[Carro]):
        """Preenche o dropdown de carros com base no cliente selecionado."""
        self._carro_dropdown.options.clear()
        if carros:
            self._carro_dropdown.options = [ft.dropdown.Option(
                key=carro.id, text=f"{carro.modelo} - Placa: {carro.placa}") for carro in carros]
        self.page.update()

    def atualizar_visualizacao_pecas(self, pecas_selecionadas: List[dict]):
        """Atualiza a lista de peças adicionadas à OS."""
        self._pecas_list_view.controls.clear()
        for index, item in enumerate(pecas_selecionadas):
            peca = item["peca_obj"]
            self._pecas_list_view.controls.append(
                ft.Row(controls=[
                    ft.Text(
                        f"{item['quantidade']}x {peca.nome} (R$ {item['valor_unitario']:.2f})", expand=True),
                    ft.Text(f"Total: R$ {item['valor_total']:.2f}"),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip="Remover Peça",
                        on_click=lambda _, idx=index: self.view_model.remover_peca_da_lista(
                            idx)
                    )
                ])
            )
        self.page.update()

    def atualizar_valor_total(self, pecas_selecionadas: List[dict]):
        """Calcula e exibe o valor total da OS."""
        total_pecas = sum(item['valor_total'] for item in pecas_selecionadas)
        try:
            mao_de_obra = float(self._mao_de_obra_field.value or 0)
        except (ValueError, TypeError):
            mao_de_obra = 0.0
        self._valor_total_text.value = f"Valor Total: R$ {total_pecas + mao_de_obra:.2f}"
        self.page.update()

    def mostrar_feedback(self, mensagem: str, sucesso: bool):
        """Exibe uma SnackBar para feedback ao usuário."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=self.page.theme.color_scheme.primary if sucesso else self.page.theme.color_scheme.error
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _on_cliente_selecionado(self, e):
        """Callback para quando um cliente é selecionado."""
        self.view_model.cliente_selecionado(self._cliente_dropdown.value)

    def _on_adicionar_peca(self, e):
        """Callback para o botão de adicionar peça."""
        try:
            peca_id = int(self._peca_dropdown.value)
            quantidade = int(self._quantidade_field.value)
            self.view_model.adicionar_peca_a_lista(peca_id, quantidade)
        except (ValueError, TypeError):
            self.mostrar_feedback(
                "Selecione uma peça e uma quantidade válida.", False)

    def _on_valor_alterado(self, e):
        """Callback para quando o valor da mão de obra é alterado."""
        self.view_model._atualizar_view()

    def _on_processar_criacao_os(self, e):
        """Callback para o botão de criar a OS."""
        cliente_id = self._cliente_dropdown.value
        carro_id = self._carro_dropdown.value
        mao_de_obra = self._mao_de_obra_field.value
        self.view_model.processar_criacao_os(cliente_id, carro_id, mao_de_obra)

    def _limpar_formulario(self):
        """Limpa todos os campos do formulário para um novo preenchimento."""
        self._cliente_dropdown.value = None
        self._carro_dropdown.options.clear()
        self._carro_dropdown.value = None
        self._peca_dropdown.value = None
        self._quantidade_field.value = "1"
        self._mao_de_obra_field.value = "0.0"
        self._pecas_list_view.controls.clear()
        self._valor_total_text.value = "Valor Total: R$ 0.00"
