# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DA VIEW DE CADASTRO DE CLIENTE (cadastro_cliente_view.py)
#
# OBJETIVO: Definir a interface visual (o modal) para o cadastro de novos
#           clientes. Esta View é um componente reutilizável.
# =================================================================================
import flet as ft
from src.viewmodels.cadastro_cliente_viewmodel import CadastroClienteViewModel
from src.styles.style import AppDimensions

class CadastroClienteView:
    """
    A View para o formulário de cadastro de clientes. Gerencia o AlertDialog.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        # A View cria sua própria instância do ViewModel.
        self.view_model = CadastroClienteViewModel(page)
        self.view_model.vincular_view(self)

        # --- Componentes Visuais do Formulário ---
        self._nome_field = ft.TextField(label="Nome", width=AppDimensions.FIELD_WIDTH)
        self._telefone_field = ft.TextField(label="Telefone", width=AppDimensions.FIELD_WIDTH)
        self._endereco_field = ft.TextField(label="Endereço", width=AppDimensions.FIELD_WIDTH)
        self._email_field = ft.TextField(label="Email", width=AppDimensions.FIELD_WIDTH)

        # --- O Modal (AlertDialog) ---
        self._dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Cadastrar Novo Cliente"),
            content=ft.Column(
                controls=[
                    self._nome_field,
                    self._telefone_field,
                    self._endereco_field,
                    self._email_field,
                ]
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.fechar_modal()),
                ft.ElevatedButton("Salvar", on_click=self.view_model.salvar_cliente),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def abrir_modal(self, e=None):
        """Abre o modal de cadastro na tela."""
        # Limpa os campos antes de abrir.
        self._nome_field.value = ""
        self._telefone_field.value = ""
        self._endereco_field.value = ""
        self._email_field.value = ""
        
        # Atribui e abre o diálogo.
        self.page.dialog = self._dlg
        self._dlg.open = True
        self.page.update()

    def fechar_modal(self):
        """Fecha o modal."""
        self._dlg.open = False
        self.page.update()

    def obter_dados_formulario(self) -> dict:
        """Envia os dados dos campos para o ViewModel."""
        return {
            "nome": self._nome_field.value,
            "telefone": self._telefone_field.value,
            "endereco": self._endereco_field.value,
            "email": self._email_field.value,
        }
    
    def mostrar_feedback(self, mensagem: str, sucesso: bool):
        """Exibe uma SnackBar para feedback ao usuário."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700
        )
        self.page.snack_bar.open = True
        self.page.update()