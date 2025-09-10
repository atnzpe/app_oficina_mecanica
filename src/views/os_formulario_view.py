# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DO FORMULÁRIO DE ORDEM DE SERVIÇO (os_formulario.py)
#
# OBJETIVO: Encapsular a UI e a lógica para a criação de uma nova Ordem de Serviço.
# =================================================================================
import flet as ft
import logging
from src.models.models import Cliente, Carro, Peca
from src.database.database import (
    criar_conexao_banco_de_dados, NOME_BANCO_DE_DADOS, obter_clientes,
    obter_carros_por_cliente, obter_pecas, fila_db
)

# Configuração do logger.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class OrdemServicoFormulario(ft.UserControl):
    """UserControl que representa o formulário completo para criar uma Ordem de Serviço."""

    def __init__(self, page: ft.Page, oficina_app):
        """Construtor da classe. Inicializa a UI e os dados necessários."""
        super().__init__()
        self.page = page
        self.oficina_app = oficina_app
        self.conexao = criar_conexao_banco_de_dados(NOME_BANCO_DE_DADOS)

        # --- Estado do Componente ---
        self.pecas_selecionadas = []
        self.lista_clientes: list[Cliente] = []
        self.lista_pecas: list[Peca] = []

        # --- Componentes de UI ---
        self._cliente_dropdown = ft.Dropdown(hint_text="Selecione um cliente", on_change=self._on_cliente_selecionado, expand=True)
        self._carro_dropdown = ft.Dropdown(hint_text="Selecione um carro", expand=True)
        self._peca_dropdown = ft.Dropdown(hint_text="Selecione uma peça", expand=True)
        self._quantidade_field = ft.TextField(label="Qtd.", width=80, value="1")
        self._mao_de_obra_field = ft.TextField(label="Mão de Obra (R$)", width=150, value="0.0", on_change=self._atualizar_valor_total)
        self._adicionar_peca_button = ft.ElevatedButton("Adicionar Peça", icon=ft.Icons.ADD, on_click=self._adicionar_peca_a_lista)
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
                ft.TextButton("Cancelar", on_click=self._fechar_modal),
                ft.ElevatedButton("Criar OS", on_click=self._processar_criacao_os),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self._carregar_dados_iniciais()

    def build(self):
        """Renderiza um container vazio, pois o controle é um modal."""
        return ft.Container()

    def _carregar_dados_iniciais(self):
        """Carrega clientes e peças do banco e popula os dropdowns."""
        self.lista_clientes = obter_clientes(self.conexao)
        self.lista_pecas = obter_pecas(self.conexao)
        self._cliente_dropdown.options = [ft.dropdown.Option(key=cliente.id, text=cliente.nome) for cliente in self.lista_clientes]
        self._peca_dropdown.options = [ft.dropdown.Option(key=peca.id, text=f"{peca.nome} (Ref: {peca.referencia})") for peca in self.lista_pecas]

    def _on_cliente_selecionado(self, e):
        """Callback acionado quando um cliente é selecionado."""
        cliente_id = self._cliente_dropdown.value
        self._carro_dropdown.options.clear()
        self._carro_dropdown.value = None
        if cliente_id:
            carros_do_cliente = obter_carros_por_cliente(self.conexao, int(cliente_id))
            self._carro_dropdown.options = [ft.dropdown.Option(key=carro.id, text=f"{carro.modelo} - Placa: {carro.placa}") for carro in carros_do_cliente]
        self.page.update()

    def _adicionar_peca_a_lista(self, e):
        """Adiciona a peça selecionada à lista de itens da OS."""
        peca_id = self._peca_dropdown.value
        try:
            quantidade = int(self._quantidade_field.value)
            if not peca_id or quantidade <= 0: raise ValueError("Seleção ou quantidade inválida.")
        except (ValueError, TypeError):
            self._mostrar_feedback("Selecione uma peça e uma quantidade válida.", False); return

        peca_obj = next((p for p in self.lista_pecas if p.id == int(peca_id)), None)
        if peca_obj:
            self.pecas_selecionadas.append({"peca_obj": peca_obj, "quantidade": quantidade, "valor_unitario": peca_obj.preco_venda, "valor_total": peca_obj.preco_venda * quantidade})
            self._atualizar_visualizacao_pecas()
            self._atualizar_valor_total()

    def _atualizar_visualizacao_pecas(self):
        """Recria a lista visual de peças adicionadas."""
        self._pecas_list_view.controls.clear()
        for index, item in enumerate(self.pecas_selecionadas):
            peca = item["peca_obj"]
            self._pecas_list_view.controls.append(
                ft.Row(controls=[
                    ft.Text(f"{item['quantidade']}x {peca.nome} (R$ {item['valor_unitario']:.2f})", expand=True),
                    ft.Text(f"Total: R$ {item['valor_total']:.2f}"),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, tooltip="Remover Peça", on_click=lambda _, idx=index: self._remover_peca_da_lista(idx))
                ])
            )
        if self.page.dialog and self.page.dialog.open: self.page.update()

    def _remover_peca_da_lista(self, index: int):
        """Remove um item da lista de peças da OS."""
        if 0 <= index < len(self.pecas_selecionadas):
            self.pecas_selecionadas.pop(index)
            self._atualizar_visualizacao_pecas()
            self._atualizar_valor_total()

    def _atualizar_valor_total(self, e=None):
        """Calcula e exibe o valor total da OS."""
        total_pecas = sum(item['valor_total'] for item in self.pecas_selecionadas)
        try: mao_de_obra = float(self._mao_de_obra_field.value or 0)
        except (ValueError, TypeError): mao_de_obra = 0.0
        self._valor_total_text.value = f"Valor Total: R$ {total_pecas + mao_de_obra:.2f}"
        if self.page.dialog and self.page.dialog.open: self.page.update()

    def abrir_modal(self, e):
        """Abre o diálogo principal para criar uma OS."""
        self._limpar_formulario()
        self.page.dialog = self._dlg
        self._dlg.open = True
        self.page.update()

    def _fechar_modal(self, e):
        """Fecha o diálogo principal."""
        self._dlg.open = False
        self.page.update()

    def _processar_criacao_os(self, e):
        """Valida e envia os dados da OS para a fila do banco."""
        cliente_id = self._cliente_dropdown.value
        carro_id = self._carro_dropdown.value
        if not all([cliente_id, carro_id, self.pecas_selecionadas]):
            self._mostrar_feedback("Cliente, Carro e ao menos uma Peça são obrigatórios.", False); return

        total_pecas = sum(item['valor_total'] for item in self.pecas_selecionadas)
        mao_de_obra = float(self._mao_de_obra_field.value or 0)
        
        fila_db.put(("criar_ordem_servico", {
            "cliente_id": int(cliente_id), "carro_id": int(carro_id),
            "pecas_quantidades": {item['peca_obj'].id: item['quantidade'] for item in self.pecas_selecionadas},
            "valor_total": total_pecas + mao_de_obra, "mao_de_obra": mao_de_obra,
        }))
        self._fechar_modal(e)
        self._mostrar_feedback("Ordem de Serviço enviada para criação!", True)

    def _limpar_formulario(self):
        """Reseta todos os campos e o estado do formulário."""
        self._cliente_dropdown.value = None
        self._carro_dropdown.options.clear(); self._carro_dropdown.value = None
        self._peca_dropdown.value = None
        self._quantidade_field.value = "1"
        self._mao_de_obra_field.value = "0.0"
        self.pecas_selecionadas.clear()
        self._pecas_list_view.controls.clear()
        self._valor_total_text.value = "Valor Total: R$ 0.00"

    def _mostrar_feedback(self, mensagem: str, sucesso: bool):
        """Exibe uma SnackBar para feedback ao usuário."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700
        )
        self.page.snack_bar.open = True
        self.page.update()