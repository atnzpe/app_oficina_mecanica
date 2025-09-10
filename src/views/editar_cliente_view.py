# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DO COMPONENTE DE EDIÇÃO DE CLIENTE (editar_cliente.py)
#
# OBJETIVO: Encapsular a UI e a lógica para pesquisar e atualizar clientes.
# =================================================================================
import flet as ft
import logging
from models.models import Cliente, Carro
from src.database.database import criar_conexao_banco_de_dados, NOME_BANCO_DE_DADOS

# Configuração do logger.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EditarCliente(ft.UserControl):
    """UserControl que encapsula a funcionalidade de pesquisa e edição de clientes."""

    def __init__(self, page: ft.Page, oficina_app):
        """Construtor. Inicializa a UI e o estado do componente."""
        super().__init__()
        self.page = page
        self.oficina_app = oficina_app
        self.conexao = criar_conexao_banco_de_dados(NOME_BANCO_DE_DADOS)
        self.cliente_em_edicao: Cliente | None = None

        # --- Componentes Visuais ---
        self._campo_nome = ft.TextField(label="Nome")
        self._campo_telefone = ft.TextField(label="Telefone")
        self._campo_endereco = ft.TextField(label="Endereço")
        self._campo_email = ft.TextField(label="Email")
        self._carros_dropdown = ft.Dropdown(width=350, hint_text="Carros do Cliente")
        self._campo_pesquisa = ft.TextField(label="Pesquisar por Nome, Telefone ou Placa", on_submit=self._on_pesquisa_submit, autofocus=True)
        self._resultados_pesquisa_col = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, height=300)

        # --- Diálogos (Modais) ---
        self._dlg_pesquisa = ft.AlertDialog(
            modal=True, title=ft.Text("Pesquisar Cliente"),
            content=ft.Column([self._campo_pesquisa, self._resultados_pesquisa_col]),
            actions=[ft.TextButton("Fechar", on_click=self._fechar_dialogo_atual)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._dlg_edicao = ft.AlertDialog(
            modal=True, title=ft.Text("Editar Cliente"),
            content=ft.Column([self._campo_nome, self._campo_telefone, self._campo_endereco, self._campo_email, self._carros_dropdown]),
            actions=[
                ft.TextButton("Cancelar", on_click=self._fechar_dialogo_atual),
                ft.ElevatedButton("Salvar", on_click=self._on_salvar_click),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def build(self):
        """Renderiza o controle inicial (botão)."""
        return ft.ElevatedButton("Pesquisar / Editar Cliente", on_click=self._abrir_modal_pesquisa)

    def _fechar_dialogo_atual(self, e):
        """Fecha o diálogo aberto na página."""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def _abrir_modal_pesquisa(self, e):
        """Prepara e exibe o modal de pesquisa."""
        self._campo_pesquisa.value = ""
        self._resultados_pesquisa_col.controls.clear()
        self.page.dialog = self._dlg_pesquisa
        self._dlg_pesquisa.open = True
        self.page.update()

    def _on_pesquisa_submit(self, e):
        """Executa a busca e atualiza a lista de resultados."""
        termo = self._campo_pesquisa.value
        self._resultados_pesquisa_col.controls.clear()
        clientes_encontrados = self._obter_clientes_por_termo(termo)
        if not clientes_encontrados:
            self._resultados_pesquisa_col.controls.append(ft.Text("Nenhum cliente encontrado."))
        else:
            for cliente in clientes_encontrados:
                self._resultados_pesquisa_col.controls.append(
                    ft.ListTile(
                        title=ft.Text(cliente.nome),
                        subtitle=ft.Text(f"Telefone: {cliente.telefone}"),
                        on_click=lambda _, c=cliente: self._abrir_modal_edicao(c),
                    )
                )
        self.page.update()

    def _obter_clientes_por_termo(self, termo: str) -> list[Cliente]:
        """Busca clientes no banco. Retorna uma lista de objetos `Cliente`."""
        with self.conexao:
            cursor = self.conexao.cursor()
            cursor.execute(
                "SELECT DISTINCT c.id, c.nome, c.telefone, c.endereco, c.email FROM clientes c LEFT JOIN carros car ON c.id = car.cliente_id WHERE c.nome LIKE ? OR c.telefone LIKE ? OR car.placa LIKE ?",
                (f"%{termo}%", f"%{termo}%", f"%{termo}%")
            )
            return [Cliente(**row) for row in cursor.fetchall()]

    def _abrir_modal_edicao(self, cliente: Cliente):
        """Prepara e exibe o modal de edição com os dados de um cliente."""
        self._fechar_dialogo_atual(None)
        self.cliente_em_edicao = cliente
        self._campo_nome.value = cliente.nome
        self._campo_telefone.value = cliente.telefone
        self._campo_endereco.value = cliente.endereco
        self._campo_email.value = cliente.email
        self._carregar_carros_cliente(cliente.id)
        self.page.dialog = self._dlg_edicao
        self._dlg_edicao.open = True
        self.page.update()

    def _carregar_carros_cliente(self, cliente_id: int):
        """Busca os carros de um cliente e popula o dropdown."""
        carros = self._obter_carros_por_cliente_id(cliente_id)
        self._carros_dropdown.options.clear()
        if carros:
            self._carros_dropdown.options = [ft.dropdown.Option(key=str(carro.id), text=f"{carro.modelo} - Placa: {carro.placa}") for carro in carros]
        else:
            self._carros_dropdown.options.append(ft.dropdown.Option(key="0", text="Nenhum carro cadastrado"))

    def _obter_carros_por_cliente_id(self, cliente_id: int) -> list[Carro]:
        """Busca os carros de um cliente pelo ID. Retorna uma lista de objetos `Carro`."""
        with self.conexao:
            cursor = self.conexao.cursor()
            cursor.execute("SELECT id, modelo, ano, cor, placa, cliente_id FROM carros WHERE cliente_id = ?", (cliente_id,))
            return [Carro(**row) for row in cursor.fetchall()]

    def _on_salvar_click(self, e):
        """Salva as alterações do cliente no banco de dados."""
        if not self.cliente_em_edicao: return
        try:
            with self.conexao:
                cursor = self.conexao.cursor()
                cursor.execute("UPDATE clientes SET nome = ?, telefone = ?, endereco = ?, email = ? WHERE id = ?",
                               (self._campo_nome.value, self._campo_telefone.value, self._campo_endereco.value,
                                self._campo_email.value, self.cliente_em_edicao.id))
            self._fechar_dialogo_atual(None)
            self._mostrar_feedback("Cliente atualizado com sucesso!", success=True)
        except Exception as ex:
            logging.error(f"Erro ao salvar edição do cliente ID {self.cliente_em_edicao.id}: {ex}")
            self._mostrar_feedback(f"Erro ao salvar: {ex}", success=False)
        finally:
            self.cliente_em_edicao = None

    def _mostrar_feedback(self, mensagem: str, success: bool):
        """Exibe uma SnackBar para feedback ao usuário."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=ft.Colors.GREEN_700 if success else ft.Colors.RED_700
        )
        self.page.snack_bar.open = True
        self.page.update()