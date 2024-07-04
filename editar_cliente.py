from typing import Any
import flet as ft
from flet import (
    Column,
    Container,
    ElevatedButton,
    Page,
    Row,
    Text,
    TextField,
    UserControl,
    colors,
    ListView,
    Dropdown,
    dropdown,
    AlertDialog,
    ListTile,
    MainAxisAlignment,
    ScrollMode,
    Ref,
)
import sqlite3
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import threading

from models import Oficina, Peca, Carro, Cliente, Usuario
from database import (
    criar_conexao_banco_de_dados,
    criar_usuario_admin,
    obter_carros_por_cliente,
    obter_clientes,
    obter_pecas,
    inserir_ordem_servico,
    atualizar_estoque_peca,
    quantidade_em_estoque_suficiente,
    inserir_movimentacao_peca,
    nome_banco_de_dados,
    fila_db,
    atualizar_carro,
)


class EditarCliente(UserControl):
    """
    Classe para editar clientes.
    """

    def __init__(self, page, oficina_app):
        super().__init__()
        self.page = page
        self.oficina_app = oficina_app
        self.conexao = criar_conexao_banco_de_dados(nome_banco_de_dados)

        # Inicializa o Dropdown de clientes (vazio inicialmente)
        self.clientes_dropdown = ft.Dropdown(width=150)

        # Carrega os clientes no Dropdown
        self.carregar_clientes_no_dropdown()

        # Inicializa os campos do formulário de edição
        self.campo_nome = ft.TextField(label="Nome")
        self.campo_telefone = ft.TextField(label="Telefone")
        self.campo_endereco = ft.TextField(label="Endereço")
        self.campo_email = ft.TextField(label="Email")
        self.carros_dropdown = ft.Dropdown(width=200, hint_text="Carros do Cliente")

    def build(self):
        # ... outros controles ...
        botao_pesquisar = ft.ElevatedButton(
            "Pesquisar Cliente", on_click=self.abrir_modal_pesquisar_cliente
        )

        return botao_pesquisar  # Retorna o botão ou um container com os controles

    def carregar_clientes_no_dropdown(self):
        """Carrega os clientes no Dropdown."""
        
        try:
            with self.conexao:
                cursor = self.conexao.cursor()
                cursor.execute("SELECT id, nome FROM clientes")
                clientes = cursor.fetchall()

                self.clientes_dropdown.options = [
                    ft.dropdown.Option(f"{cliente[1]} (ID: {cliente[0]})")
                    for cliente in clientes
                ]
                self.page.update()

        except Exception as e:
            print(f"Erro ao carregar clientes no dropdown: {e}")

    def abrir_modal_pesquisar_cliente(self, e):
        """Abre o modal de pesquisa de clientes."""
        self.dlg_pesquisa = ft.AlertDialog(
            modal=True,
            title=ft.Text("Pesquisar Cliente para Edição"),
            content=ft.Column(
                [
                    ft.TextField(
                        label="Termo de Pesquisa",
                        on_submit=self.realizar_pesquisa_cliente,
                    ),
                    ft.Column(scroll=ft.ScrollMode.AUTO, ref=Ref[Column]()),
                ]
            ),
            actions=[
                ft.TextButton("Fechar", on_click=self.fechar_modal),
            ],
            actions_alignment=MainAxisAlignment.END,
        )
        self.page.dialog = self.dlg_pesquisa
        self.dlg_pesquisa.open = True
        self.page.update()

    def realizar_pesquisa_cliente(self, e):
        """Realiza a pesquisa de clientes no banco de dados."""
        termo_pesquisa = e.control.value  # Corrigido: obtém o valor do TextField
        clientes_encontrados = self.obter_clientes_por_termo(termo_pesquisa)

        resultados_view = self.dlg_pesquisa.content.controls[
            1
        ]  # Corrigido: acessa o controle correto
        resultados_view.controls.clear()

        if clientes_encontrados:
            for cliente in clientes_encontrados:
                resultados_view.controls.append(
                    ft.ListTile(
                        title=ft.Text(cliente.nome),
                        subtitle=ft.Text(
                            f"Telefone: {cliente.telefone}, Email: {cliente.email}"
                        ),
                        on_click=lambda e, c=cliente: self.abrir_modal_editar_cliente(
                            e, c
                        ),  # Passa o cliente como argumento
                    )
                )
        else:
            resultados_view.controls.append(ft.Text("Nenhum cliente encontrado."))

        self.page.update()

    def obter_clientes_por_termo(self, termo):
        """Busca clientes no banco de dados por nome, telefone ou placa."""
        with self.conexao:
            cursor = self.conexao.cursor()
            cursor.execute(
                """
                SELECT DISTINCT c.id, c.nome, c.telefone, c.endereco, c.email
                FROM clientes c
                LEFT JOIN carros car ON c.id = car.cliente_id
                WHERE
                    c.nome LIKE ?
                    OR c.telefone LIKE ?
                    OR car.placa LIKE ?
                """,
                (f"%{termo}%", f"%{termo}%", f"%{termo}%"),
            )
            resultados = cursor.fetchall()

        return [Cliente(*resultado) for resultado in resultados]

    def fechar_modal(self, e):
        """Fecha o modal atual."""
        print("Iniciando fechamento do modal...")  # Print antes
        if self.page.dialog:
            self.page.dialog.open = False
        print("Modal definido como None.")  # Print durante
        self.page.update()
        print("Página atualizada.")  # Print depois

    def mostrar_alerta(self, mensagem):
        """Exibe um alerta em um modal."""
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("ATENÇÃO"),
            content=ft.Text(mensagem),
            actions=[
                ft.TextButton("OK", on_click=self.fechar_modal),  # Fecha o alerta ao clicar em OK
            ],
            actions_alignment=MainAxisAlignment.END,
            on_dismiss=self.fechar_modal # Fecha o modal de edição ao fechar o alerta
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def abrir_modal_editar_cliente(self, e, cliente):
        """Abre o modal para editar os dados do cliente e seus carros."""

        # Atualiza os campos do formulário com os dados do cliente
        self.campo_nome.value = cliente.nome
        self.campo_telefone.value = cliente.telefone
        self.campo_endereco.value = cliente.endereco
        self.campo_email.value = cliente.email

        # Carrega os carros do cliente no Dropdown
        self.carregar_carros_cliente(cliente.id)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Cliente"),
            content=ft.Column(
                [
                    self.campo_nome,
                    self.campo_telefone,
                    self.campo_endereco,
                    self.campo_email,
                    self.carros_dropdown,
                    self.clientes_dropdown,  # Adiciona o Dropdown de clientes ao modal
                ]
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_modal),
                ft.ElevatedButton(
                    "Salvar", on_click=lambda e: self.salvar_edicao_cliente(e, cliente)
                ),  # Passa 'cliente' para salvar_edicao_cliente
            ],
            actions_alignment=MainAxisAlignment.END,
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def carregar_carros_cliente(self, cliente_id):
        """Carrega os carros associados a um cliente no Dropdown."""
        carros = self.obter_carros_por_cliente_id(cliente_id)
        self.carros_dropdown.options = (
            [
                ft.dropdown.Option(f"Placa: {carro.placa}, Modelo: {carro.modelo}")
                for carro in carros
            ]
            if carros
            else [ft.dropdown.Option("Nenhum carro encontrado")]
        )
        self.page.update()

    def obter_carros_por_cliente_id(self, cliente_id):
        """Busca os carros de um cliente pelo ID."""
        with self.conexao:
            cursor = self.conexao.cursor()
            cursor.execute(
                """
                SELECT id, modelo, ano, cor, placa 
                FROM carros
                WHERE cliente_id = ?
                """,
                (cliente_id,),
            )
            return [Carro(*resultado) for resultado in cursor.fetchall()]

    def salvar_edicao_cliente(self, e, cliente):  # Adiciona 'cliente' como argumento
        """Salva as edições do cliente no banco de dados."""
        
        try:
            # Obtém os valores dos campos de texto
            nome = self.campo_nome.value
            telefone = self.campo_telefone.value
            endereco = self.campo_endereco.value
            email = self.campo_email.value
            print("Iniciando salvamento...")
            # Atualiza o cliente no banco de dados
            if self.oficina_app.oficina.atualizar_cliente(
                cliente.id, nome, telefone, email
            ):
                print("Edição salva com sucesso!")
                print("Salvando edição do cliente...")
                self.mostrar_alerta("Cliente atualizado com sucesso!")  # Exibe o alerta de sucesso
            else:
                self.mostrar_alerta("Erro ao atualizar os dados do cliente!")
            

        except Exception as e:
            print(f"Erro ao salvar edição do cliente: {e}")
            self.mostrar_alerta(f"Erro ao salvar edição do cliente: {e}")
            
        #self.page.update()
