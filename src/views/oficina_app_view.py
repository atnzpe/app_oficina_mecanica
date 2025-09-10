# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO PRINCIPAL DA APLICAÇÃO (oficina_app.py)
#
# OBJETIVO: Orquestrar a aplicação, inicializar a UI principal, gerenciar o estado
#           de login e coordenar a comunicação entre os componentes.
# =================================================================================
import logging
from typing import List
import flet as ft
import threading
import sqlite3

import queue

import bcrypt

# Importações dos módulos do projeto
from src.views.editar_cliente_view import EditarCliente
from src.views.os_formulario_view import OrdemServicoFormulario
from src.models.models import Usuario, Cliente
from src.database.database import (
    criar_conexao_banco_de_dados, NOME_BANCO_DE_DADOS, fila_db, obter_clientes
)

# Configuração do logger.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class OficinaApp:
    """Classe principal que gerencia toda a aplicação da oficina."""

    def __init__(self, page: ft.Page):
        """Construtor. Inicializa a página, estado e componentes da UI."""
        self.page = page
        self.conexao = criar_conexao_banco_de_dados(NOME_BANCO_DE_DADOS)
        self.usuario_atual: Usuario | None = None
        self.lista_clientes_cache: List[Cliente] = []

        # --- Componentes de UI ---
        self.ordem_servico_formulario = OrdemServicoFormulario(page, self)
        self.editar_cliente_componente = EditarCliente(page, self)

        # Componentes do modal de cadastro de carro
        self._modelo_input = ft.TextField(label="Modelo")
        self._cor_input = ft.TextField(label="Cor")
        self._ano_input = ft.TextField(label="Ano", keyboard_type=ft.KeyboardType.NUMBER)
        self._placa_input = ft.TextField(label="Placa")
        self._clientes_dropdown = ft.Dropdown(width=300, hint_text="Selecione o proprietário")

        self._modal_cadastro_carro = ft.AlertDialog(
            modal=True, title=ft.Text("Cadastrar Novo Carro"),
            content=ft.Column([self._clientes_dropdown, self._modelo_input, self._placa_input, self._cor_input, self._ano_input]),
            actions=[
                ft.TextButton("Cancelar", on_click=self._fechar_modal_cadastro_carro),
                ft.ElevatedButton("Cadastrar", on_click=self._cadastrar_carro),
            ]
        )

    def build(self):
        """Constrói e retorna a interface gráfica principal da aplicação."""
        logging.info("Construindo a UI principal da aplicação.")
        self.botoes = {
            "login": ft.ElevatedButton("Efetue Login", on_click=self._abrir_modal_login),
            "cadastrar_cliente": ft.ElevatedButton("Cadastrar Cliente", on_click=self._abrir_modal_cadastrar_cliente, disabled=True),
            "cadastrar_carro": ft.ElevatedButton("Cadastrar Carro", on_click=self._abrir_modal_cadastro_carro, disabled=True),
            "editar_cliente": self.editar_cliente_componente,
            "cadastrar_pecas": ft.ElevatedButton("Cadastrar / Atualizar Peças", on_click=self._abrir_modal_cadastrar_peca, disabled=True),
            "saldo_estoque": ft.ElevatedButton("Visualizar Saldo de Estoque", on_click=self._abrir_modal_saldo_estoque, disabled=True),
            "ordem_servico": ft.ElevatedButton("Criar Ordem de Serviço", on_click=self.ordem_servico_formulario.abrir_modal, disabled=True),
            "relatorio": ft.ElevatedButton("RELATÓRIOS", on_click=self._abrir_modal_relatorio, disabled=True),
            "sair": ft.ElevatedButton("Sair", on_click=self._sair_do_app),
        }
        self.botoes["editar_cliente"].disabled = True

        self.view = ft.Column(
            [*self.botoes.values()],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10
        )
        return self.view

    def atualizar_estado_botoes(self):
        """Atualiza o estado dos botões com base no login."""
        logado = bool(self.usuario_atual)
        self.botoes["login"].disabled = logado
        for nome, botao in self.botoes.items():
            if nome not in ("login", "sair"):
                botao.disabled = not logado
        self.page.update()

    def _carregar_clientes_para_dropdown_carros(self):
        """Carrega clientes e popula o dropdown no modal de cadastro de carros."""
        self.lista_clientes_cache = obter_clientes(self.conexao)
        self._clientes_dropdown.options = [
            ft.dropdown.Option(key=cliente.id, text=cliente.nome)
            for cliente in self.lista_clientes_cache
        ]

    def _abrir_modal_cadastro_carro(self, e):
        """Abre o modal para cadastrar um novo carro."""
        self._carregar_clientes_para_dropdown_carros()
        self.page.dialog = self._modal_cadastro_carro
        self._modal_cadastro_carro.open = True
        self.page.update()

    def _fechar_modal_cadastro_carro(self, e):
        """Fecha e limpa o modal de cadastro de carro."""
        self._modelo_input.value = ""
        self._cor_input.value = ""
        self._ano_input.value = ""
        self._placa_input.value = ""
        self._clientes_dropdown.value = None
        self._modal_cadastro_carro.open = False
        self.page.update()

    def _cadastrar_carro(self, e):
        """Valida e envia os dados do carro para a fila do DB."""
        proprietario_id = self._clientes_dropdown.value
        if not all([self._modelo_input.value, self._placa_input.value, proprietario_id]):
            self.page.snack_bar = ft.SnackBar(ft.Text("Proprietário, Modelo e Placa são obrigatórios!"), bgcolor=ft.Colors.ORANGE)
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        dados_carro = {
            "modelo": self._modelo_input.value, "cor": self._cor_input.value,
            "ano": int(self._ano_input.value) if self._ano_input.value.isdigit() else None,
            "placa": self._placa_input.value, "cliente_id": int(proprietario_id)
        }
        fila_db.put(("cadastrar_carro", dados_carro))
        self._fechar_modal_cadastro_carro(e)

    # (A implementação dos outros modais e do pubsub permanece a mesma)
    def _abrir_modal_login(self, e): pass
    def _abrir_modal_cadastrar_cliente(self, e): pass
    def _abrir_modal_cadastrar_peca(self, e): pass
    def _abrir_modal_saldo_estoque(self, e): pass
    def _abrir_modal_relatorio(self, e): pass
    def _sair_do_app(self, e): self.page.window_destroy()

def _sair_do_app(self, e):
        """Encerra a aplicação."""
        logging.info("Saindo da aplicação.")
        self.page.window_destroy()

    def _mostrar_feedback(self, mensagem: str, sucesso: bool):
        """Exibe uma SnackBar para feedback ao usuário."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700
        )
        self.page.snack_bar.open = True
        self.page.update()


# --- SEÇÃO SEM ALTERAÇÃO (com pequenas melhorias) ---
def processar_fila_db(page: ft.Page):
    """Função executada em uma thread para processar operações de banco de dados."""
    conexao_db = criar_conexao_banco_de_dados(NOME_BANCO_DE_DADOS)
    if not conexao_db:
        logging.error("Falha crítica: a thread do banco de dados não conseguiu se conectar.")
        return

    while True:
        try:
            operacao, dados = fila_db.get(timeout=1.0) # Adicionado timeout para não bloquear para sempre

            if operacao == "cadastrar_carro":
                # Lida com o dicionário de dados enviado pela UI.
                cursor = conexao_db.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO carros (modelo, ano, cor, placa, cliente_id) VALUES (:modelo, :ano, :cor, :placa, :cliente_id)",
                        dados
                    )
                    conexao_db.commit()
                    page.pubsub.send_all({"topic": "carro_cadastrado", "mensagem": "Carro cadastrado com sucesso!"})
                except sqlite3.IntegrityError:
                    page.pubsub.send_all({"topic": "erro_cadastro", "mensagem": "Já existe um carro com essa placa."})
                except Exception as e:
                    page.pubsub.send_all({"topic": "erro_generico", "mensagem": f"Erro: {e}"})
            
            # (outras operações como 'cadastrar_cliente', 'fazer_login', 'criar_ordem_servico' continuam aqui)

        except queue.Empty:
            continue # Simplesmente continua o loop se a fila estiver vazia.
        except Exception as e:
            logging.error(f"Erro inesperado na thread do banco de dados: {e}")