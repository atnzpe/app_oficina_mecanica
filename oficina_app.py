from typing import Any, Tuple, List
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
)
import threading
import sqlite3
import bcrypt
import queue
from datetime import datetime
import os

# Importações para relatórios
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Importações de outros módulos
from editar_cliente import EditarCliente
from report import gerar_relatorio_os, gerar_relatorio_estoque, abrir_modal_os_por_cliente
from os_formulario import OrdemServicoFormulario
from models import Oficina, Peca, Carro, Cliente, Usuario

# Importações do banco de dados
from database import (
    criar_conexao_banco_de_dados,
    criar_usuario_admin,
    obter_carros_por_cliente,
    obter_clientes,
    obter_pecas,
    inserir_ordem_servico,
    atualizar_estoque_peca,
    quantidade_em_estoque_suficiente,
    nome_banco_de_dados,
    banco_de_dados,
    fila_db,
)
class OficinaApp:

    def __init__(self, page: ft.Page):
        super().__init__()
        
        self.page = page
        self.os = OrdemServicoFormulario
        
        # Conexão única com o banco de dados
        self.conexao = self.criar_conexao_segura()
        if not self.conexao:
            print("Erro ao conectar ao banco de dados. Encerrando a aplicação.")
            self.page.window_destroy()
            return
        
        
        # Inicializa o banco de dados se ele não existir
        self.inicializar_banco_de_dados()

        
        
        self.carro_dropdown_os = ft.Dropdown(width=300)
        self.cliente_selecionado = None
        self.carro_selecionado = None
        
        self.conexao = criar_conexao_banco_de_dados(nome_banco_de_dados)
        #self.conexao = conexao
        self.conexao_db = criar_conexao_banco_de_dados(nome_banco_de_dados)
        conexao_db = criar_conexao_banco_de_dados(nome_banco_de_dados)
        #conexao = criar_conexao_banco_de_dados(nome_banco_de_dados)
        self.carregar_dados()
        self.peca_dropdown = []
        self.peca_dropdown = ft.Dropdown(width=200)

        self.oficina = Oficina()
        self.usuario_atual = None
        self.clientes_dropdown = ft.Dropdown(width=300)
        

        self.evento_clientes_carregados = threading.Event()
        page.pubsub.subscribe(self._on_message)
        self.pecas: List[Any] = []  # Inicialize com lista vazia
        self.clientes: List[Any] = []  # Inicialize com lista vazia
        # Carregue os dados primeiro
        
        
        # Inicializa o formulario_os com os argumentos necessários
        #self.ordem_servico_formulario = OrdemServicoFormulario(
        #    page, self, self.pecas, self.clientes
        #)
        #self.ordem_servico_formulario = OrdemServicoFormulario(page, self, pecas, clientes)
        # Carrega o Dropdown ao Iniciar
        self.carregar_clientes_no_dropdown()
        self.ordem_servico_formulario = OrdemServicoFormulario(page, self, [], [])
        # Chama a Função de criar usuario Admin
        criar_usuario_admin(nome_banco_de_dados)
        
        
        self.carregar_dados()
        self.carregar_clientes_no_dropdown()
        #self.build_ui()
        

        # Modal de cadastro de carro
        self.modal_cadastro_carro = ft.AlertDialog(
            modal=True,
            title=ft.Text("Cadastrar Novo Carro"),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Cadastrar", on_click=self.cadastrar_carro
                            ),
                            ft.OutlinedButton(
                                "Cancelar", on_click=self.fechar_modal_cadastro_carro
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ]
            ),
        )

        # Inputs do formulário
        self.modelo_input = ft.TextField(label="Modelo")
        self.cor_input = ft.TextField(label="Cor")
        self.ano_input = ft.TextField(label="Ano")
        self.placa_input = ft.TextField(label="Placa")
        self.clientes_dropdown = ft.Dropdown(
            width=300,
            options=[],
        )

        # Adicione os inputs ao conteúdo do modal
        self.modal_cadastro_carro.content.controls.insert(0, self.placa_input)
        self.modal_cadastro_carro.content.controls.insert(0, self.ano_input)
        self.modal_cadastro_carro.content.controls.insert(0, self.cor_input)
        self.modal_cadastro_carro.content.controls.insert(0, self.modelo_input)
        self.modal_cadastro_carro.content.controls.insert(0, self.clientes_dropdown)

        self.editarcliente = EditarCliente(page, self)
        
    # Botões da Tela Inici
    # 
    # al
    
    def build(self):
        self.botoes = {
            # Botão de Login
            "login": ft.ElevatedButton("Efetue Login", on_click=self.abrir_modal_login),
            # Botão Cadastrar Cliente
            "cadastrar_cliente": ft.ElevatedButton(
                "Cadastrar Cliente",
                on_click=self.abrir_modal_cadastrar_cliente,
                disabled=True,
            ),  # Botão Cadastrar Carro
            "cadastrar_carro": ft.ElevatedButton(
                "Cadastrar Carro",
                on_click=self.abrir_modal_cadastro_carro,
                disabled=True,
            ),# Botão Editar Cliente
            "editar_cliente": ft.ElevatedButton(
                "Pesquisar / Editar Cliente",
                on_click=self.editarcliente.abrir_modal_pesquisar_cliente,  # Lambda salva o dia!
                disabled=True,
            ),
            # Botão Cadastrar Peças
            "cadastrar_pecas": ft.ElevatedButton(
                "Cadastrar / Atualizar Peças",
                on_click=self.abrir_modal_cadastrar_peca,
                disabled=True,
            ),
            # Visualiza o Saldo de Estoque
            "saldo_estoque": ft.ElevatedButton(
                "Visualiza o Saldo de Estoque",
                on_click=self.abrir_modal_saldo_estoque,
                disabled=True,
            ),
            # Gera uma Ordem de Serviço
            "ordem_servico": ft.ElevatedButton(
            "Criar Ordem de Serviço",
            on_click=self.ordem_servico_formulario.abrir_modal_ordem_servico,  # Chama a função para abrir o modal
            disabled=True,
            ),
            # Relatórios
            "relatorio": ft.ElevatedButton(
                "RELATÓRIOS",
                on_click=self.abrir_modal_relatorio,
                disabled=True,
            ),
            # Sair do App
            "sair": ft.ElevatedButton("Sair", on_click=self.sair_do_app),
        }

        self.view = ft.Column(
            [
                ft.Text("Bem-vindo à oficina Guarulhos!", size=30),  # Titulo
                *self.botoes.values(),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.page.add(self.view)

        return self.view

    #     ==================================
    #     FUNÇÕES GERAIS
    #     ==================================

    # Recebe mensagens da thread do banco de dados através do pubsub.
    # As mensagens devem ser dicionários com a chave 'topic' para indicar o tipo de mensagem.
    def _on_message(self, e):
        """
        Recebe mensagens da thread do banco de dados através do pubsub.
        As mensagens devem ser dicionários com a chave 'topic' para indicar o tipo de mensagem.
        """
        if e["topic"] == "login_bem_sucedido":
            usuario = e["usuario"]
            self.usuario_atual = usuario
            self.fechar_modal(None)
            self.atualizar_estado_botoes()
            self.page.snack_bar = ft.SnackBar(ft.Text("Login realizado com sucesso!"))
            self.page.snack_bar.open = True

        elif e["topic"] == "login_falhou":
            mensagem_erro = e["mensagem_erro"]
            self.mostrar_alerta(mensagem_erro)

        elif e["topic"] == "usuario_cadastrado":
            self.mostrar_alerta(e["mensagem_erro"])

        elif e["topic"] == "erro_cadastro_usuario":
            self.mostrar_alerta(e["mensagem_erro"])

        elif e["topic"] == "cliente_cadastrado":
            self.mostrar_alerta(e["mensagem_erro"])

        elif e["topic"] == "erro_cadastro_cliente":
            self.mostrar_alerta(e["mensagem_erro"])

        elif e["topic"] == "carro_cadastrado":
            self.mostrar_alerta(e["mensagem_erro"])

        elif e["topic"] == "erro_cadastro_carro":
            self.mostrar_alerta(e["mensagem_erro"])

        # Manipula as mensagens recebidas do pubsub."""
        elif e["topic"] == "clientes_dropdown":
            # Atualizar o Dropdown do modal de cadastro de carro
            self.clientes_dropdown = e["clientes"]
            self.evento_clientes_carregados.set()

        elif e["topic"] == "peca_cadastrada":
            self.mostrar_alerta(e["mensagem_erro"])

        elif e["topic"] == "peca_atualizada":
            self.mostrar_alerta(e["mensagem_erro"])

        elif e["topic"] == "erro_ao_salvar_peca":
            self.mostrar_alerta(e["mensagem_erro"])

        elif e["topic"] == "erro_db":
            self.mostrar_alerta(e["mensagem_erro"])

        self.page.update()

    def criar_conexao_segura(self):
        """
        Cria uma conexão com o banco de dados e retorna a conexão.
        Retorna None em caso de erro.
        """
        try:
            conexao = sqlite3.connect(nome_banco_de_dados)
            return conexao
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None

    def inicializar_banco_de_dados(self):
        """Inicializa as tabelas e dados básicos no banco de dados."""
        try:
            criar_usuario_admin(self.conexao)
            # ... outras inicializações, se necessário ...
        except Exception as e:
            print(f"Erro ao inicializar o banco de dados: {e}")
            
    

    # Atualiza o Estado Dos Botoes
    def atualizar_estado_botoes(self):
        """Atualiza o estado dos botões com base no login."""
        logado = bool(self.usuario_atual)  # True se usuario_atual não for None

        # Habilita/desabilita botões (exceto "login" e "sair")
        for nome_botao, botao in self.botoes.items():
            if nome_botao not in ("login", "sair"):
                botao.disabled = not logado

        # Controle do botão de login
        self.botoes["login"].disabled = logado

        # Atualiza a view para refletir as mudanças
        self.view.update()

    # ==================================
    # MOSTRA ALERTAS / FECHAR MODAL
    # ==================================
    def carregar_dados(self) -> Tuple[List[Any], List[Any]]:
        """
        Carrega peças e clientes do banco de dados.

        Returns:
            Tuple[List[Any], List[Any]]: Tupla contendo a lista de peças e a lista de clientes.
            Levanta uma exceção caso ocorra algum erro durante o processo.
        """
       
        try:
            with criar_conexao_banco_de_dados(nome_banco_de_dados) as conexao:
                self.clientes = obter_clientes(conexao)
                self.pecas = obter_pecas(conexao)
                
                # Carregar outros dados (exemplo):
                self.carros = self.carregar_carros(conexao)  #  <-- Nova função para carregar carros
                self.servicos = self.carregar_servicos(conexao) # <-- Nova função para carregar serviços

                if not self.clientes:
                    raise ValueError("A lista de clientes está vazia!")
                if not self.pecas:
                    raise ValueError("A lista de peças está vazia!")
                
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Erro ao carregar dados do banco de dados: {e}")

        except ValueError as e: 
            print(f"Erro ao carregar dados: {e}")
        
        
    def carregar_carros(self, conexao):
        """
        Carrega os dados dos carros do banco de dados.
        """
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM carros")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao carregar carros: {e}")
            return []  # Retorna uma lista vazia em caso de erro

    def carregar_servicos(self, conexao):
        """
        Carrega os dados dos serviços do banco de dados.
        """
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM servicos") 
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao carregar serviços: {e}")
            return [] # Retorna uma lista vazia em caso de erro
        
    def mostrar_alerta(self, mensagem):
        # O código acima está criando e exibindo uma caixa de diálogo de alerta (AlertDialog) com o título "ATENÇÃO"
        # e uma mensagem especificada pela variável "mensagem". A caixa de diálogo contém um único botão rotulado
        # "OK" que, ao ser clicado, chamará o método "fechar_modal" para fechar a caixa de diálogo. O diálogo é
        # definido como modal, o que significa que bloqueará a interação com o resto da página até que ela seja fechada.
        # A caixa de diálogo é então exibida na página e a página é atualizada para refletir as alterações.
        """Exibe um alerta em um Modal (AlertDialog)."""
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("ATENÇÃO"),
            content=ft.Text(mensagem),
            actions=[
                # usa a mesma função fechar_modal
                ft.TextButton("OK", on_click=self.fechar_modal)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dlg  # Atribui o diálogo diretamente
        dlg.open = True
        self.page.update()

    # """Fecha qualquer modal aberto."""
    def fechar_modal(self, e):
        """Fecha qualquer modal aberto."""
        self.page.dialog.open = False
        self.page.update()

    # ==================================
    # LOGIN / CADASTRO USUÁRIO
    # ==================================

    # Abre o Modal de Login
    def abrir_modal_login(self, e):
        self.dlg_login = ft.AlertDialog(
            modal=True,
            title=ft.Text("Login do Usuario"),
            content=ft.Column(
                [
                    ft.TextField(label="Digite seu Nome", ref=ft.Ref[str]()),
                    ft.TextField(label="Digite sua Senha", ref=ft.Ref[str]()),
                    ft.Row(
                        [
                            ft.ElevatedButton("Entrar", on_click=self.fazer_login),
                            ft.TextButton("Cadastrar", on_click=self.abrir_cadastro),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                ]
            ),
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = self.dlg_login
        self.dlg_login.open = True
        self.page.update()

    # Funçõa para fazer no login
    def fazer_login(self, e):
        dlg = self.page.dialog
        nome = dlg.content.controls[0].value
        senha = dlg.content.controls[1].value

        try:
            fila_db.put(("fazer_login", (nome, senha)))
            self.mostrar_alerta("Processando...")
        except Exception as e:
            self.mostrar_alerta(f"Erro ao processar : {e}")

    # Abre o modal para cadastro de novo usuário.
    def abrir_cadastro(self, e):
        """Abre o modal para cadastro de novo usuário."""
        self.dlg_cadastro = ft.AlertDialog(
            modal=True,
            title=ft.Text("Cadastro de Usuário"),
            content=ft.Column(
                [
                    ft.TextField(label="Nome de Usuário", ref=ft.Ref[str]()),
                    ft.TextField(label="Senha", password=True, ref=ft.Ref[str]()),
                    ft.TextField(
                        label="Confirmar Senha", password=True, ref=ft.Ref[str]()
                    ),
                ]
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_modal),
                ft.ElevatedButton("Cadastrar", on_click=self.cadastrar_usuario),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = self.dlg_cadastro
        self.dlg_cadastro.open = True
        self.page.update()

    # Cadastra Usuario do Sistema
    def cadastrar_usuario(self, e):
        dlg = self.page.dialog
        nome = dlg.content.controls[0].value
        senha = dlg.content.controls[1].value
        confirmar_senha = dlg.content.controls[2].value

        if senha != confirmar_senha:
            self.mostrar_alerta("As senhas não coincidem!")
            return

        try:
            fila_db.put(
                (
                    "cadastrar_usuario",
                    (nome, bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()),
                )
            )
            self.mostrar_alerta("Solicitação de cadastro enviada. Aguarde...")
            self.fechar_modal(e)
        except Exception as e:
            self.mostrar_alerta(f"Erro ao enviar solicitação de cadastro: {e}")

    # ==================================
    # CADASTRO DE CLIENTES
    # ==================================

    # ABRE O MODAL PARA CADASTRO DE CLIENTES
    def abrir_modal_cadastrar_cliente(self, e):
        self.cadastrar_cliente(e)

    # Coleta dados do cliente e tenta cadastrá-lo.
    def cadastrar_cliente(self, e):
        """Coleta dados do cliente e tenta cadastrá-lo."""

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Cadastrar Cliente"),
            content=ft.Column(
                [
                    ft.TextField(label="Nome", ref=ft.Ref[str]()),
                    ft.TextField(label="Telefone (Ex: 55 + ddd + numero cliente)", ref=ft.Ref[str]()),
                    ft.TextField(label="Endereço", ref=ft.Ref[str]()),
                    ft.TextField(label="Email", ref=ft.Ref[str]()),
                ]
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_modal),
                ft.ElevatedButton("Salvar", on_click=self.salvar_cliente),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    # Função para Salvar o Cadastro do Cliente
    def salvar_cliente(self, e):
        """Envia a solicitação de cadastro de cliente para a thread do banco de dados."""
        dlg = self.page.dialog
        nome = dlg.content.controls[0].value
        telefone = dlg.content.controls[1].value
        endereco = dlg.content.controls[2].value
        email = dlg.content.controls[3].value

        try:
            fila_db.put(("cadastrar_cliente", (nome, telefone, endereco, email)))
            self.mostrar_alerta("Processando cadastro de cliente. Aguarde...")
            self.fechar_modal(e)
        except Exception as e:
            self.mostrar_alerta(f"Erro ao processar cadastro de cliente: {e}")

        self.page.update()

    # ==================================
    # CADASTRO DE CARROS
    # ==================================

    # aBRE O mODAL PARA REALIZAR O CADASTRO DE CARROS
    def abrir_modal_cadastro_carro(self, e):
        self.carregar_clientes_no_dropdown()
        self.page.dialog = self.modal_cadastro_carro
        self.modal_cadastro_carro.open = True
        self.page.update()

    def fechar_modal_cadastro_carro(self, e):
        self.modelo_input.value = ""
        self.cor_input.value = ""
        self.ano_input.value = ""
        self.placa_input.value = ""
        self.clientes_dropdown.value = None
        self.modal_cadastro_carro.open = False
        self.page.update()

    def cadastrar_carro(self, e):
        # Obter valores dos campos de entrada
        modelo = self.modelo_input.value
        cor = self.cor_input.value
        ano = self.ano_input.value
        placa = self.placa_input.value
        proprietario_id = (
            int(self.clientes_dropdown.value.split(" (ID: ")[1][:-1])
            if self.clientes_dropdown.value
            else None
        )

        # Validações
        if not all([modelo, cor, ano, placa, proprietario_id]):
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Por favor, preencha todos os campos!"),
                bgcolor="red",
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        try:
            ano = int(ano)
            if ano <= 1900 or ano > 2100:  # Validação simples do ano
                raise ValueError("Ano inválido")
        except ValueError:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Ano inválido. Digite um ano entre 1900 e 2100."),
                bgcolor="red",
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Envia os dados para a fila do banco de dados
        fila_db.put(
            (
                "cadastrar_carro",
                (modelo, cor, ano, placa, proprietario_id),
            )
        )

        self.fechar_modal_cadastro_carro(e)  # Fecha o modal após enviar dados

    def carregar_clientes_no_dropdown(self):
        try:
            with criar_conexao_banco_de_dados(nome_banco_de_dados) as conexao:
                cursor = conexao.cursor()
                cursor.execute("SELECT id, nome FROM clientes")
                clientes = cursor.fetchall()

                self.clientes_dropdown.options = [
                    ft.dropdown.Option(f"{cliente[1]} (ID: {cliente[0]})")
                    for cliente in clientes
                ]

                self.evento_clientes_carregados.set()
                self.page.update()
        except Exception as e:
            print(f"Erro ao carregar clientes no dropdown: {e}")

    # -----------------------------------
    # INICIO FUNÇÕES CADASTRAR PEÇAS
    # ------------------------------------

    # FUNÇÃO ABRIR MODAL CADASTRAR PEÇAS
    def abrir_modal_cadastrar_peca(self, e):
        """Abre o modal para cadastrar uma nova peça."""

        # Define se é uma nova peça (padrão: True)
        self.nova_peca = True

        self.dlg_cadastrar_peca = ft.AlertDialog(
            modal=True,
            title=ft.Text("Cadastrar/Atualizar Peça"),
            content=ft.Column(
                [
                    ft.TextField(label="Nome", ref=ft.Ref[str]()),
                    ft.TextField(label="Referência", ref=ft.Ref[str]()),
                    ft.TextField(label="Fabricante", ref=ft.Ref[str]()),
                    ft.TextField(label="Descrição", ref=ft.Ref[str]()),
                    ft.TextField(label="Preço de Compra", ref=ft.Ref[str]()),
                    ft.TextField(label="Preço de Venda", ref=ft.Ref[str]()),
                    ft.TextField(label="Quantidade em Estoque", ref=ft.Ref[str]()),
                ]
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_modal),
                ft.ElevatedButton("Salvar", on_click=self.salvar_peca),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = self.dlg_cadastrar_peca
        self.dlg_cadastrar_peca.open = True

        # Adiciona evento on_change para os campos de nome e referência
        self.dlg_cadastrar_peca.content.controls[0].on_change = (
            self.verificar_peca_existente
        )
        self.dlg_cadastrar_peca.content.controls[1].on_change = (
            self.verificar_peca_existente
        )

        self.page.update()

    def obter_peca_por_nome_e_referencia(self, nome, referencia):
        """
        Busca uma peça pelo nome e referência.

        Args:
            nome (str): O nome da peça.
            referencia (str): A referência da peça.

        Returns:
            Peca: O objeto Peca se encontrado, None caso contrário.
        """
        with sqlite3.connect(nome_banco_de_dados) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT * FROM pecas WHERE nome=? AND referencia=?", (nome, referencia)
            )
            peca_data = cursor.fetchone()
            if peca_data:
                return Peca(*peca_data[1:])
        return None

    def verificar_peca_existente(self, e):
        """Verifica se a peça já existe no banco de dados."""
        dlg = self.dlg_cadastrar_peca  # Referência ao modal
        nome = dlg.content.controls[0].value
        referencia = dlg.content.controls[1].value

        with sqlite3.connect(nome_banco_de_dados) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT * FROM pecas WHERE nome=? AND referencia=?", (nome, referencia)
            )
            peca_existente = cursor.fetchone()

        # Habilita/desabilita campos com base na existência da peça
        if self.nova_peca:  # Só verifica se for uma nova peça
            peca_existente = self.obter_peca_por_nome_e_referencia(nome, referencia)
            if peca_existente:
                # Desabilita campos (exceto quantidade)
                for i in range(2, 4):  # Índices dos campos a desabilitar
                    dlg.content.controls[i].disabled = True
                self.nova_peca = False  # Indica que não é mais uma nova peça
            else:
                # Habilita os campos se a peça não for encontrada
                for i in range(2, 4):
                    dlg.content.controls[i].disabled = False

        self.page.update()

    # FUNÇÃO DO SALVAR PEÇA

    def salvar_peca(self, e):
        """Salva uma nova peça ou atualiza a quantidade de uma existente."""
        dlg = self.page.dialog
        nome = dlg.content.controls[0].value
        referencia = dlg.content.controls[1].value
        fabricante = dlg.content.controls[2].value
        descricao = dlg.content.controls[3].value
        preco_compra = dlg.content.controls[4].value
        preco_venda = dlg.content.controls[5].value
        quantidade = dlg.content.controls[6].value

        try:
            preco_compra = float(preco_compra)
            preco_venda = float(preco_venda)
            quantidade = int(quantidade)
        except ValueError:
            self.mostrar_alerta("Os campos de preço e quantidade devem ser numéricos.")
            return

        try:
            fila_db.put(
                (
                    "salvar_peca",
                    (
                        nome,
                        referencia,
                        fabricante,
                        descricao,
                        preco_compra,
                        preco_venda,
                        quantidade,
                    ),
                )
            )

            self.mostrar_alerta("Processando informações da peça. Aguarde...")
            self.fechar_modal(e)
        except Exception as e:
            self.mostrar_alerta(f"Erro ao processar informações da peça: {e}")

        self.page.update()

    # -----------------------------------
    # FINAL FUNÇÕES CADASTRAR PEÇAS
    # ------------------------------------

    # =====================================
    # FUNÇÃO ABRIR MODOAL SALDO DE ESTOQUE
    # =====================================

    # Abre o modal para exibir o saldo de estoque.
    def abrir_modal_saldo_estoque(self, e):
        """Abre o modal para exibir o saldo de estoque."""

        movimentacoes = self.carregar_dados_saldo_estoque()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Saldo de Estoque"),
            content=ft.Column(
                [
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Nome")),
                            ft.DataColumn(ft.Text("Referência")),
                            ft.DataColumn(ft.Text("Total de Entradas")),
                            ft.DataColumn(ft.Text("Total de Saídas")),
                            ft.DataColumn(ft.Text("Estoque Final")),
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text(m[1])),  # Nome da peça
                                    ft.DataCell(ft.Text(m[2])),  # Referência da peça
                                    ft.DataCell(ft.Text(m[3])),  # Total de Entradas
                                    ft.DataCell(ft.Text(m[4])),  # Total de Saídas
                                    ft.DataCell(ft.Text(m[3] - m[4])),  # Estoque Final
                                ]
                            )
                            for m in movimentacoes
                        ],
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Fechar", on_click=self.fechar_modal),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def obter_ids_os_por_peca(self, peca_id):
        """Retorna uma lista de IDs de OSs onde a peça foi utilizada."""
        with sqlite3.connect(nome_banco_de_dados) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                """
                SELECT DISTINCT ordem_servico_id 
                FROM movimentacao_pecas 
                WHERE peca_id = ? AND tipo_movimentacao = 'saida'
                """,
                (peca_id,),
            )
            return [row[0] for row in cursor.fetchall() if row[0] is not None]

    # Carrega os dados de movimentação de peças do banco de dados,
    # calculando o saldo final para cada peça
    def carregar_dados_saldo_estoque(self):
        """Carrega os dados de movimentação de peças do banco de dados,
        calculando o saldo final para cada peça.
        """
        with sqlite3.connect(nome_banco_de_dados) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                """
                SELECT 
                    p.id,
                    p.nome, 
                    p.referencia,
                    COALESCE(SUM(CASE WHEN mp.tipo_movimentacao = 'entrada' THEN mp.quantidade ELSE 0 END), 0) AS total_entradas,
                    COALESCE(SUM(CASE WHEN mp.tipo_movimentacao = 'saida' THEN mp.quantidade ELSE 0 END), 0) AS total_saidas
                FROM 
                    pecas p
                LEFT JOIN 
                    movimentacao_pecas mp ON p.id = mp.peca_id
                GROUP BY
                    p.id, p.nome, p.referencia; 
                """
            )
            movimentacoes = cursor.fetchall()

        return movimentacoes

    # ======================================
    # ORDEM DE SERVIÇO
    # ======================================
    
    
        #ft.TextButton("Cancelar", on_click=lambda e: self.ordem_servico_formulario.fechar_modal_os(e, self.modal_ordem_servico)),


    # ================================
    
    # RELATORIOS
    # ================================

    def abrir_modal_relatorio(self, e):
        """Abre o modal para selecionar o tipo de relatório."""

        self.modal_relatorio = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Gerar Relatório"),
                    content=ft.Column(
                        [
                            ft.ElevatedButton(
                                "Relatório OS",
                                on_click=gerar_relatorio_os(self.conexao, self.page), 
                            ),
                            ft.ElevatedButton(
                                "Saldo de Estoque",
                                on_click=gerar_relatorio_estoque(self.conexao, self.page),  # Implementar lógica depois
                            ),
                            ft.ElevatedButton(
                                "OS por Cliente",
                                on_click=abrir_modal_os_por_cliente,  # Implementar lógica depois
                            ),
                        ]
                    ),
                    actions=[
                        ft.TextButton("Fechar", on_click=self.fechar_modal),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
        self.page.dialog = self.modal_relatorio
        self.modal_relatorio.open = True
        self.page.update()

    

        
    
    
    # =============================
    # SAIR DO APLICATIVO
    # ============================

    # Função para Encerrar o Aplicativo usado no VBotão SAIR
    def sair_do_app(self, e):
        self.page.window_destroy()


# Processa as operações do banco de dados em uma thread separada.
# Envia mensagens para a thread principal usando pubsub com informações sobre o resultado das operações.
def processar_fila_db(page):
    """
    Processa as operações do banco de dados em uma thread separada.
    Envia mensagens para a thread principal usando pubsub com informações sobre o resultado das operações.
    """

    conexao_db = criar_conexao_banco_de_dados(nome_banco_de_dados)
    try:
        while True:

            try:

                operacao, dados = fila_db.get(block=True, timeout=1)
                if operacao == "cadastrar_usuario":
                    nome, senha_hash = dados
                    cursor = conexao_db.cursor()
                    try:

                        cursor.execute(
                            "INSERT INTO usuarios (nome, senha) VALUES (?, ?)",
                            (nome, senha_hash),
                        )
                        conexao_db.commit()
                        page.pubsub.send_all(
                            {
                                "topic": "usuario_cadastrado",
                                "usuario": None,
                                "mensagem_erro": "Usuário cadastrado com sucesso!",
                            }
                        )
                    except sqlite3.IntegrityError:
                        page.pubsub.send_all(
                            {
                                "topic": "erro_cadastro_usuario",
                                "mensagem_erro": "Nome de usuário já existe!",
                            }
                        )
                    except Exception as e:
                        page.pubsub.send_all(
                            {"topic": "erro_cadastro_usuario", "mensagem_erro": str(e)}
                        )

                elif operacao == "fazer_login":
                    nome, senha = dados
                    cursor = conexao_db.cursor()
                    cursor.execute("SELECT * FROM usuarios WHERE nome=?", (nome,))
                    usuario_data = cursor.fetchone()

                    if usuario_data:
                        senha_armazenada = usuario_data[2]
                        if bcrypt.checkpw(senha.encode(), senha_armazenada.encode()):
                            usuario = Usuario(usuario_data[1], usuario_data[2])
                            page.pubsub.send_all(
                                {"topic": "login_bem_sucedido", "usuario": usuario}
                            )
                        else:
                            page.pubsub.send_all(
                                {
                                    "topic": "login_falhou",
                                    "mensagem_erro": "Credenciais inválidas!",
                                }
                            )

                    else:
                        # Tentar cadastrar o usuário se não existir
                        try:
                            senha_hash = bcrypt.hashpw(
                                senha.encode(), bcrypt.gensalt()
                            ).decode()
                            cursor.execute(
                                "INSERT INTO usuarios (nome, senha) VALUES (?, ?)",
                                (nome, senha_hash),
                            )
                            conexao_db.commit()
                            page.pubsub.send_all(
                                {
                                    "topic": "usuario_cadastrado",
                                    "mensagem_erro": f"Usuário '{nome}' cadastrado com sucesso! Faça o login.",
                                }
                            )
                        except Exception as e:
                            page.pubsub.send_all(
                                {
                                    "topic": "login_falhou",
                                    "mensagem_erro": f"Erro ao cadastrar usuário: {e}",
                                }
                            )

                elif operacao == "cadastrar_cliente":
                    # Nova operação
                    nome, telefone, endereco, email = dados
                    cursor = conexao_db.cursor()

                    try:
                        cursor.execute(
                            "INSERT INTO clientes (nome, telefone, endereco, email) VALUES (?, ?, ?, ?)",
                            (nome, telefone, endereco, email),
                        )
                        conexao_db.commit()
                        page.pubsub.send_all(
                            {
                                "topic": "cliente_cadastrado",
                                "mensagem_erro": "Cliente cadastrado com sucesso!",
                            }
                        )
                    except sqlite3.IntegrityError:
                        page.pubsub.send_all(
                            {
                                "topic": "erro_cadastro_cliente",
                                "mensagem_erro": "Já existe um cliente com este nome.",
                            }
                        )
                    except Exception as e:
                        page.pubsub.send_all(
                            {
                                "topic": "erro_cadastro_cliente",
                                "mensagem_erro": f"Erro ao cadastrar cliente: {str(e)}",
                            }
                        )

                elif operacao == "cadastrar_carro":
                    modelo, ano, cor, placa, cliente_id = dados
                    cursor = conexao_db.cursor()

                    try:
                        cursor.execute(
                            "INSERT INTO carros (modelo, ano, cor, placa, cliente_id) VALUES (?, ?, ?, ?, ?)",
                            (modelo, ano, cor, placa, cliente_id),
                        )
                        conexao_db.commit()
                        page.pubsub.send_all(
                            {
                                "topic": "carro_cadastrado",
                                "mensagem_erro": "Carro cadastrado com sucesso!",
                            }
                        )
                    except sqlite3.IntegrityError:
                        page.pubsub.send_all(
                            {
                                "topic": "erro_cadastro_carro",
                                "mensagem_erro": "Já existe um carro com essa placa.",
                            }
                        )
                    except Exception as e:
                        page.pubsub.send_all(
                            {
                                "topic": "erro_cadastro_carro",
                                "mensagem_erro": f"Erro ao cadastrar carro: {str(e)}",
                            }
                        )

                elif operacao == "obter_clientes_dropdown":  #  nova operação
                    cursor = conexao_db.cursor()
                    cursor.execute("SELECT id, nome FROM clientes")
                    clientes = cursor.fetchall()
                    opcoes_dropdown = [
                        ft.dropdown.Option(f"{cliente[1]} (ID: {cliente[0]})")
                        for cliente in clientes
                    ]
                    page.pubsub.send_all(
                        {"topic": "clientes_dropdown", "clientes": opcoes_dropdown}
                    )

                elif operacao == "salvar_peca":
                    (
                        nome,
                        referencia,
                        fabricante,
                        descricao,
                        preco_compra,
                        preco_venda,
                        quantidade,
                    ) = dados
                    cursor = conexao_db.cursor()
                    try:
                        cursor.execute(
                            "SELECT id, quantidade_em_estoque FROM pecas WHERE nome = ? AND referencia = ?",
                            (nome, referencia),
                        )
                        peca_existente = cursor.fetchone()

                        if peca_existente:
                            # Peça existente - atualizar quantidade
                            peca_id, quantidade_atual = peca_existente
                            nova_quantidade = quantidade_atual + quantidade
                            cursor.execute(
                                "UPDATE pecas SET quantidade_em_estoque = ? WHERE id = ?",
                                (nova_quantidade, peca_id),
                            )
                            conexao_db.commit()

                            # Registrar a movimentação de atualização da peça
                            cursor.execute(
                                """
                                INSERT INTO movimentacao_pecas (peca_id, tipo_movimentacao, quantidade)
                                VALUES (?, 'entrada', ?)
                                """,
                                (peca_id, quantidade),
                            )
                            conexao_db.commit()

                            page.pubsub.send_all(
                                {
                                    "topic": "peca_atualizada",
                                    "mensagem_erro": f"Quantidade da peça '{nome}' atualizada com sucesso!",
                                }
                            )
                        else:
                            # Nova peça - inserir na tabela
                            cursor.execute(
                                """
                                INSERT INTO pecas (nome, referencia, fabricante, descricao, preco_compra, preco_venda, quantidade_em_estoque) 
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    nome,
                                    referencia,
                                    fabricante,
                                    descricao,
                                    preco_compra,
                                    preco_venda,
                                    quantidade,
                                ),
                            )
                            peca_id = (
                                cursor.lastrowid
                            )  # Obter o ID da peça recém-inserida
                            conexao_db.commit()

                            # Registrar a entrada da peça na tabela de movimentação
                            cursor.execute(
                                """
                                INSERT INTO movimentacao_pecas (peca_id, tipo_movimentacao, quantidade)
                                VALUES (?, 'entrada', ?)
                                """,
                                (peca_id, quantidade),
                            )
                            conexao_db.commit()

                            page.pubsub.send_all(
                                {
                                    "topic": "peca_cadastrada",
                                    "mensagem_erro": f"Peça '{nome}' cadastrada com sucesso!",
                                }
                            )
                    except Exception as e:
                        page.pubsub.send_all(
                            {
                                "topic": "erro_ao_salvar_peca",
                                "mensagem_erro": f"Erro ao salvar peça: {str(e)}",
                            }
                        )

            except queue.Empty:
                pass

            except sqlite3.IntegrityError as e:
                page.pubsub.send_all(
                    {
                        "topic": "erro_db",
                        "mensagem_erro": f"Erro de integridade no banco de dados: {e}",
                        "dados": dados,
                        "operacao": operacao,
                    }
                )

            except sqlite3.Error as e:
                page.pubsub.send_all(
                    {
                        "topic": "erro_db",
                        "mensagem_erro": f"Erro no banco de dados: {e}",
                        "dados": dados,
                        "operacao": operacao,
                    }
                )

            except Exception as e:
                page.pubsub.send_all(
                    {
                        "topic": "erro_db",
                        "mensagem_erro": f"Erro inesperado: {e}",
                        "dados": dados,
                        "operacao": operacao,
                    }
                )

    except Exception as e:
        print(f"Erro ao processar operação da fila: {e}")

    finally:
        if conexao_db:
            conexao_db.close()
