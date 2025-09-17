# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DA VIEW DO FORMULÁRIO DE OS (os_formulario_view.py)
#
# OBJETIVO: Definir a aparência e os componentes visuais para a criação de uma
#           Ordem de Serviço. Não contém lógica de negócio.
#
# SEÇÕES ALTERADAS NESTA REATORAÇÃO (ISSUE #1):
#   - Este ficheiro foi refatorado a partir do antigo `os_formulario.py`.
#   - Toda a lógica de negócio foi movida para `os_formulario_viewmodel.py`.
#   - A classe já não herda de `ft.UserControl`, mas sim gere um `ft.AlertDialog`,
#     seguindo as melhores práticas atuais do Flet.
# =================================================================================
import flet as ft
import logging
from typing import List
from src.models.models import Cliente, Carro, Peca
from src.viewmodels.os_formulario_viewmodel import OrdemServicoFormularioViewModel

class OrdemServicoFormularioView:
    """
    A View para o formulário de OS. Gere o modal e delega ações ao ViewModel.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        self.view_model = OrdemServicoFormularioViewModel(page)
        self.view_model.vincular_view(self)

        # --- Componentes de UI ---
        self._cliente_dropdown = ft.Dropdown(hint_text="Selecione um cliente", on_change=self._on_cliente_selecionado, expand=True)
        self._carro_dropdown = ft.Dropdown(hint_text="Selecione um carro", expand=True)
        self._peca_dropdown = ft.Dropdown(hint_text="Selecione uma peça", expand=True)
        self._quantidade_field = ft.TextField(label="Qtd.", width=80, value="1")
        self._mao_de_obra_field = ft.TextField(label="Mão de Obra (R$)", width=150, value="0.0", on_change=self._on_valor_alterado)
        self._adicionar_peca_button = ft.ElevatedButton("Adicionar Peça", icon=ft.icons.ADD, on_click=self._on_adicionar_peca)
        self._pecas_list_view = ft.ListView(expand=True, spacing=10)
        self._valor_total_text = ft.Text("Valor Total: R$ 0.00", size=16, weight=ft.FontWeight.BOLD)

        # --- Diálogo Principal ---
        self._dlg = ft.AlertDialog(
            modal=True, title=ft.Text("Criar Nova Ordem de Serviço"),
            content=ft.Column(
                controls=[
                    ft.Row([self._cliente_dropdown, self._carro_dropdown]),
                    ft.Divider(),
                    ft.Row([self._peca_dropdown, self._quantidade_field], alignment=ft.MainAxisAlignment.START),
                    self._adicionar_peca_button,
                    ft.Divider(),
                    ft.Text("Peças Adicionadas:"),
                    self._pecas_list_view,
                    ft.Divider(),
                    ft.Row([self._mao_de_obra_field, self._valor_total_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], width=800, height=500,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_modal),
                ft.ElevatedButton("Criar OS", on_click=self._on_processar_criacao_os),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    # --- MÉTODOS PÚBLICOS (API da View) ---

    def abrir_modal(self, e):
        """Prepara e exibe o modal do formulário."""
        self._limpar_formulario()
        self.view_model.carregar_dados_iniciais()
        self.page.dialog = self._dlg
        self._dlg.open = True
        self.page.update()

    def fechar_modal(self, e=None):
        """Fecha o modal principal."""
        self._dlg.open = False
        self.page.update()

    def popular_dropdowns_iniciais(self, clientes: List[Cliente], pecas: List[Peca]):
        """Comandado pelo ViewModel para preencher os dropdowns iniciais."""
        self._cliente_dropdown.options = [ft.dropdown.Option(key=cliente.id, text=cliente.nome) for cliente in clientes]
        self._peca_dropdown.options = [ft.dropdown.Option(key=peca.id, text=f"{peca.nome} (Ref: {peca.referencia})") for peca in pecas]
        self.page.update()

    def popular_dropdown_carros(self, carros: List[Carro]):
        """Comandado pelo ViewModel para preencher o dropdown de carros."""
        self._carro_dropdown.options.clear()
        if carros:
            self._carro_dropdown.options = [ft.dropdown.Option(key=carro.id, text=f"{carro.modelo} - Placa: {carro.placa}") for carro in carros]
        self.page.update()

    def atualizar_visualizacao_pecas(self, pecas_selecionadas: List[dict]):
        """Comandado pelo ViewModel para redesenhar a lista de peças."""
        self._pecas_list_view.controls.clear()
        for index, item in enumerate(pecas_selecionadas):
            peca = item["peca_obj"]
            self._pecas_list_view.controls.append(
                ft.Row(controls=[
                    ft.Text(f"{item['quantidade']}x {peca.nome} (R$ {item['valor_unitario']:.2f})", expand=True),
                    ft.Text(f"Total: R$ {item['valor_total']:.2f}"),
                    ft.IconButton(icon=ft.icons.DELETE_OUTLINE, on_click=lambda _, idx=index: self.view_model.remover_peca_da_lista(idx))
                ])
            )
        self.page.update()

    def atualizar_valor_total(self, pecas_selecionadas: List[dict]):
        """Comandado pelo ViewModel para recalcular e exibir o valor total."""
        total_pecas = sum(item['valor_total'] for item in pecas_selecionadas)
        try: mao_de_obra = float(self._mao_de_obra_field.value or 0)
        except (ValueError, TypeError): mao_de_obra = 0.0
        self._valor_total_text.value = f"Valor Total: R$ {total_pecas + mao_de_obra:.2f}"
        self.page.update()

    def mostrar_feedback(self, mensagem: str, sucesso: bool):
        """Exibe uma SnackBar para feedback ao utilizador."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=ft.colors.GREEN_700 if sucesso else ft.colors.RED_700
        )
        self.page.snack_bar.open = True
        self.page.update()

    # --- HANDLERS DE EVENTOS PRIVADOS (Callbacks da UI) ---

    def _on_cliente_selecionado(self, e):
        """Delega a ação para o ViewModel."""
        self.view_model.cliente_selecionado(self._cliente_dropdown.value)

    def _on_adicionar_peca(self, e):
        """Coleta dados da UI e delega a ação para o ViewModel."""
        try:
            peca_id = int(self._peca_dropdown.value)
            quantidade = int(self._quantidade_field.value)
            self.view_model.adicionar_peca_a_lista(peca_id, quantidade)
        except (ValueError, TypeError):
            self.mostrar_feedback("Selecione uma peça e uma quantidade válida.", False)

    def _on_valor_alterado(self, e):
        """Quando a mão de obra muda, pede ao ViewModel para recalcular."""
        self.view_model._atualizar_view()

    def _on_processar_criacao_os(self, e):
        """Coleta os IDs finais e delega a criação para o ViewModel."""
        cliente_id = self._cliente_dropdown.value
        carro_id = self._carro_dropdown.value
        mao_de_obra = self._mao_de_obra_field.value
        self.view_model.processar_criacao_os(cliente_id, carro_id, mao_de_obra)

    def _limpar_formulario(self):
        """Reseta os campos do formulário para o estado inicial."""
        self._cliente_dropdown.value = None
        self._carro_dropdown.options.clear(); self._carro_dropdown.value = None
        self._peca_dropdown.value = None
        self._quantidade_field.value = "1"
        self._mao_de_obra_field.value = "0.0"
        self._pecas_list_view.controls.clear()
        self._valor_total_text.value = "Valor Total: R$ 0.00"