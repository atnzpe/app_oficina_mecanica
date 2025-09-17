# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DA VIEW DE EDIÇÃO DE CLIENTE (editar_cliente_view.py)
#
# OBJETIVO: Definir a aparência e os componentes visuais para a funcionalidade
#           de pesquisa e edição de clientes. Esta é a camada de "View" e não
#           contém lógica de negócio.
#
# SEÇÕES ALTERADAS NESTA REATORAÇÃO (ISSUE #1):
#   - Este ficheiro foi refatorado a partir do antigo `editar_cliente.py`.
#   - Toda a lógica de negócio foi movida para `editar_cliente_viewmodel.py`.
#   - A classe agora instancia o seu próprio ViewModel e delega-lhe todas as ações.
#   - Herda de `ft.Column` para ser um componente Flet válido, seguindo as
#     melhores práticas atuais da biblioteca.
# =================================================================================
import flet as ft
import logging
from typing import List
from src.models.models import Cliente, Carro
# Importa a "forma" do seu ViewModel para saber quais métodos chamar.
from src.viewmodels.editar_cliente_viewmodel import EditarClienteViewModel

class EditarClienteView(ft.Column):
    """
    A View para a funcionalidade de edição de clientes. Herda de `ft.Column`.
    """
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        # Cria a sua própria instância do ViewModel para gerir a sua lógica.
        self.view_model = EditarClienteViewModel(page)
        self.view_model.vincular_view(self)

        # --- Componentes Visuais ---
        self._campo_nome = ft.TextField(label="Nome")
        self._campo_telefone = ft.TextField(label="Telefone")
        self._campo_endereco = ft.TextField(label="Endereço")
        self._campo_email = ft.TextField(label="Email")
        self._carros_dropdown = ft.Dropdown(width=350, hint_text="Carros do Cliente")
        self._campo_pesquisa = ft.TextField(
            label="Pesquisar por Nome, Telefone ou Placa",
            on_submit=self._on_pesquisa_submit,
            autofocus=True
        )
        self._resultados_pesquisa_col = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, height=300)

        # --- Diálogos (Modais) ---
        self._dlg_pesquisa = ft.AlertDialog(
            modal=True, title=ft.Text("Pesquisar Cliente"),
            content=ft.Column([self._campo_pesquisa, self._resultados_pesquisa_col]),
            actions=[ft.TextButton("Fechar", on_click=self.fechar_todos_os_modais)],
        )
        self._dlg_edicao = ft.AlertDialog(
            modal=True, title=ft.Text("Editar Cliente"),
            content=ft.Column([
                self._campo_nome, self._campo_telefone, self._campo_endereco,
                self._campo_email, self._carros_dropdown
            ]),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_todos_os_modais),
                ft.ElevatedButton("Salvar", on_click=self._on_salvar_click),
            ],
        )

        # --- Estrutura do Componente ---
        # Define o que este componente `Column` irá renderizar.
        self.controls = [
            ft.ElevatedButton(
                "Pesquisar / Editar Cliente",
                on_click=self.abrir_modal_pesquisa,
                icon=ft.Icons.MANAGE_ACCOUNTS
            )
        ]

    # --- MÉTODOS PÚBLICOS (API da View) ---

    def abrir_modal_pesquisa(self, e):
        """Prepara e exibe o modal de pesquisa."""
        self._campo_pesquisa.value = ""
        self._resultados_pesquisa_col.controls.clear()
        self.page.dialog = self._dlg_pesquisa
        self._dlg_pesquisa.open = True
        self.page.update()

    def atualizar_lista_resultados(self, clientes: List[Cliente]):
        """Comandado pelo ViewModel para atualizar a lista de resultados da pesquisa."""
        self._resultados_pesquisa_col.controls.clear()
        if not clientes:
            self._resultados_pesquisa_col.controls.append(ft.Text("Nenhum cliente encontrado."))
        else:
            for cliente in clientes:
                self._resultados_pesquisa_col.controls.append(
                    ft.ListTile(
                        title=ft.Text(cliente.nome),
                        subtitle=ft.Text(f"Telefone: {cliente.telefone}"),
                        # Delega a ação para o ViewModel.
                        on_click=lambda _, c=cliente: self.view_model.selecionar_cliente_para_edicao(c),
                    )
                )
        self.page.update()

    def abrir_modal_edicao(self, cliente: Cliente, carros: List[Carro]):
        """Comandado pelo ViewModel para abrir e popular o modal de edição."""
        self.fechar_todos_os_modais(None)
        
        # Preenche os campos com os dados recebidos do ViewModel.
        self._campo_nome.value = cliente.nome
        self._campo_telefone.value = cliente.telefone
        self._campo_endereco.value = cliente.endereco
        self._campo_email.value = cliente.email

        self._carros_dropdown.options.clear()
        if carros:
            self._carros_dropdown.options = [ft.dropdown.Option(key=str(carro.id), text=f"{carro.modelo} - Placa: {carro.placa}") for carro in carros]
        else:
            self._carros_dropdown.options.append(ft.dropdown.Option(key="0", text="Nenhum carro cadastrado"))

        self.page.dialog = self._dlg_edicao
        self._dlg_edicao.open = True
        self.page.update()

    def fechar_todos_os_modais(self, e=None):
        """Fecha qualquer diálogo que esta View possa ter aberto."""
        if self.page.dialog in [self._dlg_pesquisa, self._dlg_edicao]:
            self.page.dialog.open = False
            self.page.update()

    def mostrar_feedback(self, mensagem: str, success: bool):
        """Exibe uma SnackBar para feedback ao utilizador."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=ft.Colors.GREEN_700 if success else ft.Colors.RED_700
        )
        self.page.snack_bar.open = True
        self.page.update()

    # --- HANDLERS DE EVENTOS PRIVADOS (Callbacks da UI) ---

    def _on_pesquisa_submit(self, e):
        """Delega a ação de pesquisa para o ViewModel."""
        self.view_model.pesquisar_cliente(self._campo_pesquisa.value)

    def _on_salvar_click(self, e):
        """Coleta os dados do formulário e os envia para o ViewModel salvar."""
        novos_dados = {
            "nome": self._campo_nome.value,
            "telefone": self._campo_telefone.value,
            "endereco": self._campo_endereco.value,
            "email": self._campo_email.value,
        }
        self.view_model.salvar_alteracoes(novos_dados)
