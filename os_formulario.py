from typing import Any
import flet as ft
import sqlite3
from flet import (
    Column,
    Container,
    ElevatedButton,
    Page,
    Row,
    Text,
    TextField,
    UserControl,
    ListView,
    Dropdown,
    dropdown,
)
import urllib.parse
import os
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import TableStyle
from reportlab.platypus import Table
from reportlab.lib import colors

from models import Oficina, Peca, Carro, Cliente, Usuario
from database import (
    criar_conexao_banco_de_dados,
    obter_carros_por_cliente,
    obter_clientes,
    obter_pecas,
    inserir_ordem_servico,
    atualizar_estoque_peca,
    quantidade_em_estoque_suficiente,
    inserir_movimentacao_peca,
    nome_banco_de_dados,
)



class BotaoAdicionarPeca(ft.UserControl):
    """
    UserControl para o botão "Adicionar Peça".
    Controla dinamicamente seu estado (habilitado/desabilitado).

    # Comentário para QA:
    # - Verificar se o botão é habilitado somente quando todos os campos
    #   ("Peça", "Preço Unitário" e "Quantidade") estiverem preenchidos.
    # - Verificar se o botão é desabilitado quando qualquer um dos campos
    #   for limpo ou ficar vazio.
    """

    def __init__(self, ordem_servico_formulario):
        super().__init__()
        self.ordem_servico_formulario = ordem_servico_formulario

    


class OrdemServicoFormulario(ft.UserControl):
    """Formulário para criar uma nova ordem de serviço."""

    def __init__(self, page, oficina_app, pecas, clientes):  #
        super().__init__()
        self.page = page
        # Inicializa dados da ordem de serviço
        self.pecas_selecionadas = []
        self.link_whatsapp = None

        
        self.oficina_app = oficina_app
        self.pecas = pecas
        self.clientes = clientes
        self.adicionar_peca_button = BotaoAdicionarPeca(self)
        self.botao_add = ft.TextButton("ADCIONE A PEÇA", on_click=self.adicionar_peca)
        #self.orcamento_formulario = OrcamentoFormulario(self.page, self, self.pecas, self.clientes)
        self.botao_enviar_orcamento = ft.ElevatedButton(
            "Enviar Orçamento", on_click=self.enviar_orcamento
        )
        
        self.cliente_dropdown = ft.Dropdown(width=200)
        self.carro_dropdown = ft.Dropdown(width=200)
        self.peca_dropdown = ft.Dropdown(  # Inicializar o dropdown primeiro
            width=200,
            options=[ft.dropdown.Option(f"{peca[1]}") for peca in self.pecas],
            on_change=self.atualizar_botao_adicionar_peca,
        )
        self.preco_unitario_field = []
        self.preco_unitario_field = ft.TextField(
            label="Preço Unitário",
            width=200,
            value="0.00",
            on_change=self.atualizar_botao_adicionar_peca,
        )

        self.quantidade_field = ft.TextField(
            label="Quantidade",
            width=100,
            value="1",  # Define como string inicialmente
            # Conecta on_change ao atualizar_botao_adicionar_peca
            on_change=self.atualizar_botao_adicionar_peca,  # Conecta ao evento
        )
        self.botao_add
        self.pecas_list_view = ft.ListView(expand=True, height=200)
        self.valor_total_text = ft.Text("Valor Total: R$ 0.00", visible=True)
        self.total_pecas_text = ft.Text("Total de Peças: R$ 0.00")
        self.mao_de_obra_text = ft.Text("Mão de Obra: R$ 0.00")
        self.maodeobra = 0.0
        self.total_com_mao_de_obra_text = ft.Text("Total com mão de obra: R$ 0.00")
        self.pagamento_avista_text = ft.Text("Pagamento à Vista: R$ 0.00")
        self.pagamento_cartao_text = ft.Text(
            "Pagamento No Cartão: Consultar Valores"
        )  # Implementar Hiperlink WhatsApp para que seja solcitado orcamento atraves do WhatsApp
        self.preco_mao_de_obra_field = ft.TextField(
            label="Mão de Obra (R$)", width=100, value="0.00"
        )

        # Inicializa dados da ordem de serviço
        self.pecas_selecionadas = []
        self.link_whatsapp = None

        # Carrega dados iniciais do formulário
        self.carregar_dados()
        self.carregar_clientes_no_dropdown()

        # Cria o AlertDialog aqui no construtor
        # self.dlg_ordem_servico = self.criar_modal_ordem_servico()

    def abrir_modal_ordem_servico(self, e):
        """Abre o modal da ordem de serviço."""
        
        
        print("Abrindo modal...")
        
        self.criar_modal_ordem_servico()

    def atualizar_botao_adicionar_peca(self, e):
        """
        Atualiza o estado do botão "Adicionar Peça".
        Este método é chamado sempre que um dos campos
        relevantes do formulário é alterado.
        """
        # self.adicionar_peca_button.atualizar_estado()
        self.calcular_valor_total()  # Recalcula totais quando algo muda
        self.page.update()

    def criar_modal_ordem_servico(self):
        """Cria o modal (janela pop-up) para a ordem de serviço."""
        print("Criando o modal...")
        try:
            self.carregar_dados()
            self.carregar_clientes_no_dropdown()
            #self.pecas, self.clientes = self.carregar_dados()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            
        
        self.dlg_os = ft.AlertDialog(
            modal=True,
            title=ft.Text("Criar Ordem de Serviço"),
            content=ft.Container(
                content=ft.Row(  # Linha principal para conter as duas colunas
                    [
                        ft.Column(  # Primeira Coluna
                            [
                                ft.Container(
                                    content=ft.Text("Cliente:"),
                                    width=100,
                                ),
                                self.cliente_dropdown,
                                ft.Container(content=ft.Text("Carro:"), width=100),
                                self.carro_dropdown,
                                ft.Container(content=ft.Text("Peça:"), width=100),
                                self.peca_dropdown,
                                ft.Text("Preço Unitário:", width=100),
                                self.preco_unitario_field,
                                ft.Text("Quantidade:", width=100),
                                self.quantidade_field,
                                self.botao_add,
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        ft.VerticalDivider(
                            width=2,
                            color=ft.colors.GREY_400,
                        ),
                        ft.Column(  # Segunda Coluna
                            [
                                self.pecas_list_view,
                                ft.Divider(),
                                self.total_pecas_text,
                                self.mao_de_obra_text,
                                self.total_com_mao_de_obra_text,
                                ft.Divider(),
                                self.botao_add,
                                ft.Row(
                                    [
                                        ft.Text("Mão de Obra (R$):", width=120),
                                        self.preco_mao_de_obra_field,
                                        ft.ElevatedButton(
                                            "Inserir Mão de Obra",
                                            on_click=self.atualizar_mao_de_obra,
                                        ),
                                        ft.TextButton(
                                            "Visualizar OS", on_click=self.visualizar_os
                                        ),
                                        ft.TextButton(
                                            "Criar OS",
                                            on_click=self.criar_ordem_servico,
                                        ),
                                    ],
                                    spacing=20,
                                    alignment=ft.MainAxisAlignment.START,
                                ),
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                    ],
                    spacing=50,
                    alignment=ft.MainAxisAlignment.START,
                ),
                width=1115,
                expand=1,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_modal_os),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = self.dlg_os
        self.dlg_os.open = True
        

        self.page.update()
        #return dlg

    def atualizar_mao_de_obra(self, e):
        """Atualiza o valor da mão de obra e recalcula o total da OS."""
        try:
            mao_de_obra = float(self.preco_mao_de_obra_field.value)
            self.maodeobra = mao_de_obra
            print(f"Este e a mao_de_obra: {mao_de_obra}")
            print(self.maodeobra)
            self.calcular_valor_total()  # Recalcula o valor total da OS
            print(f"Mão de obra atualizada para: R$ {mao_de_obra:.2f}")
            ft.snack_bar = ft.SnackBar(ft.Text("Mão de obra atualizada com sucesso!"))
            self.page.show_snack_bar(ft.snack_bar)
            self.preco_mao_de_obra_field.value = "0.00"

            self.page.update()
        except ValueError:
            print("Erro: Valor inválido para a mão de obra.")
            ft.snack_bar = ft.SnackBar(ft.Text("Valor inválido para a mão de obra."))
            self.page.show_snack_bar(ft.snack_bar)

    def atualizar_lista_pecas(self):
        """Atualiza a lista de peças no modal."""
        self.pecas_list_view.controls = []
        for i, peca in enumerate(self.pecas_selecionadas):
            self.pecas_list_view.controls.append(
                ft.Row(
                    [
                        ft.Text(
                            f"{peca['nome']} - Preço Unitário: R$ {peca['preco_unitario']:.2f} - Quantidade: {peca['quantidade']} - Total: R$ {peca['valor_total']:.2f}"
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            on_click=lambda e, index=i: self.remover_peca(index),
                        ),
                    ]
                )
            )
        self.page.update()

    def formatar_valor(self, valor, largura=20, alinhamento="<"):
        """Formata um valor com alinhamento e largura,
        lidando com valores None.
        """
        if valor is not None:
            return f"{valor:{alinhamento}{largura}}"
        else:
            return ""

    def visualizar_os(self, e):
        """Exibe uma prévia da OS em um novo modal."""
        print("Pré-Visualizar OS!")
        if not all([self.cliente_dropdown.value, self.carro_dropdown.value]):
            ft.snack_bar = ft.SnackBar(ft.Text("Preencha os campos Cliente e Carro!"))
            self.page.show_snack_bar(ft.snack_bar)
            return

        cliente_nome = self.cliente_dropdown.value.split(" (ID: ")[0]
        carro_descricao = self.carro_dropdown.value

        # Ler o valor da mão de obra AQUI
        mao_de_obra = self.maodeobra
        print(f"Linha 221 {mao_de_obra}")
        print(self.maodeobra)
        # Calcula o valor total das peças
        valor_total_pecas = sum(peca["valor_total"] for peca in self.pecas_selecionadas)

        conteudo_preview = ft.Column(
            [
                ft.Markdown(f"## Ordem de Serviço"),
                ft.Markdown(f"**Cliente:** {cliente_nome}"),
                ft.Markdown(f"**Carro:** {carro_descricao}"),
                ft.Markdown(
                    f"**Data de Criação:** {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}"
                ),
                ft.Divider(),
                ft.Markdown(f"**Itens:**"),
                ft.Markdown(
                    f"{'Material':<20} {'Valor Unitário':<15} {'Quantidade':<10} {'Valor Total':>10}"
                ),
                ft.Divider(),
                *[
                    ft.Row(
                        [
                            ft.Text(self.formatar_valor(peca["nome"])),
                            ft.Text(
                                self.formatar_valor(
                                    f"R$ {peca['preco_unitario']:.2f}", largura=15
                                )
                            ),
                            ft.Text(
                                self.formatar_valor(peca["quantidade"], largura=10)
                            ),
                            ft.Text(
                                self.formatar_valor(
                                    f"R$ {peca['valor_total']:.2f}",
                                    largura=10,
                                    alinhamento=">",
                                )
                            ),
                        ]
                    )
                    for peca in self.pecas_selecionadas
                ],
                ft.Divider(),
                ft.Markdown(f"**Valor das Peças: R$ {valor_total_pecas:.2f}**"),
                ft.Markdown(f"**Mão de Obra: R$ {mao_de_obra:.2f}**"),
                ft.Markdown(
                    f"**Valor Total da OS: R$ {valor_total_pecas + mao_de_obra:.2f}**"
                ),
            ],
            alignment=ft.MainAxisAlignment.START,  # Alinha o conteúdo à esquerda
        )

        modal_preview = ft.AlertDialog(
            modal=False,
            title=ft.Text("Pré-visualização da OS"),
            content=conteudo_preview,
            actions=[
                ft.Text("Enviar Orçamento para o Whatsapp:"),
                self.botao_enviar_orcamento,
                ft.ElevatedButton("Fechar", on_click=self.fechar_modal_preview),
                ft.ElevatedButton("Enviar OS", on_click=self.criar_ordem_servico),
            ],
        )
        print(f"Linha 267 {mao_de_obra}")
        print(self.maodeobra)
        self.page.dialog = modal_preview
        modal_preview.open = True
        self.page.update()

    def formatar_os(self, ordem_servico_id):
        """Formata os dados da OS no formato desejado."""
        cliente_nome = self.cliente_dropdown.value.split(" (ID: ")[0]
        placa_carro = self.carro_dropdown.value.split("Placa: ")[1][:-1]
        data_hora_criacao = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        mao_de_obra = self.maodeobra

        # Cabeçalho
        os_formatada = f"**Ordem de Serviço - Nº {ordem_servico_id}**\n\n"
        os_formatada += f"**Cliente:** {cliente_nome}\n"
        os_formatada += f"**Placa do Carro:** {placa_carro}\n"
        os_formatada += f"**Data de Criação:** {data_hora_criacao}\n\n"

        # Itens em tabela
        os_formatada += "**Itens:**\n"
        os_formatada += "| Material | Valor Unitário | Quantidade | Valor Total |\n"
        os_formatada += "|---|---|---|---| \n"

        for peca in self.pecas_selecionadas:
            os_formatada += (
                f"| {peca['nome']} "
                f"| R$ {peca['preco_unitario']:.2f} "
                f"| {peca['quantidade']} "
                f"| R$ {peca['valor_total']:.2f} |\n"
            )

            # Valores totais
        valor_total_pecas = sum(peca["valor_total"] for peca in self.pecas_selecionadas)
        mao_de_obra = self.maodeobra
        valor_total_os = valor_total_pecas + mao_de_obra

        os_formatada += f"\nValor das Peças: R$ {valor_total_pecas:.2f}\n"
        os_formatada += f"Valor da Mão de Obra: R$ {mao_de_obra:.2f}\n"
        os_formatada += f"**Valor Total da OS: R$ {valor_total_os:.2f}**"

        return os_formatada

    def fechar_modal_preview(self, e):
        """Fecha o modal de pré-visualização."""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
            
            

    def remover_peca(self, index):
        """Remove uma peça da lista de peças selecionadas."""
        del self.pecas_selecionadas[index]
        self.atualizar_lista_pecas()
        self.calcular_valor_total()
        # ---->  Atualiza o componente 'BotaoAdicionarPeca'
        #        após remover uma peça.

        self.page.update()

    def carregar_clientes_no_dropdown(self):
        """Carrega a lista de clientes no dropdown."""
        print(f"Tipo de self.pecas: {type(self.pecas)}")
        try:
            with criar_conexao_banco_de_dados(nome_banco_de_dados) as conexao:
                clientes = obter_clientes(conexao)
                self.cliente_dropdown.options = [
                    ft.dropdown.Option(f"{cliente[1]} (ID: {cliente[0]})")
                    for cliente in clientes
                ]
                self.cliente_dropdown.on_change = self.cliente_alterado
                self.page.update()
        except Exception as e:
            print(f"Erro ao carregar clientes no dropdown: {e}")
            # TODO: Exibir mensagem de erro para o usuário

    def carregar_carros_no_dropdown(self, cliente_id):
        """Carrega a lista de carros no dropdown,
        baseado no cliente selecionado.
        """
        try:
            with criar_conexao_banco_de_dados(nome_banco_de_dados) as conexao:
                if cliente_id:
                    carros = obter_carros_por_cliente(conexao, cliente_id)
                    self.carro_dropdown.options = [
                        ft.dropdown.Option(
                            f"{carro[1]} (ID: {carro[0]}, Placa: {carro[4]})"
                        )
                        for carro in carros
                    ]
                else:
                    self.carro_dropdown.options = []
                self.page.update()
        except Exception as e:
            print(f"Erro ao carregar carros no dropdown: {e}")
            # Exibir mensagem de erro para o usuário

    def carregar_dados(self):
        """Carrega os dados iniciais do formulário."""
        with criar_conexao_banco_de_dados(nome_banco_de_dados) as conexao:
            self.clientes = obter_clientes(conexao)
            self.pecas = obter_pecas(conexao)
        self.peca_dropdown.options = [
            ft.dropdown.Option(f"{peca[1]}") for peca in self.pecas
        ]
        self.page.update()

    def cliente_alterado(self, e):
        """Atualiza o dropdown de carros quando o cliente é alterado."""
        self.cliente_selecionado = self.cliente_dropdown.value
        if self.cliente_selecionado:
            cliente_id = int(self.cliente_selecionado.split(" (ID: ")[1][:-1])
            self.carregar_carros_no_dropdown(cliente_id)
        else:
            self.carregar_carros_no_dropdown(None)

    def adicionar_peca(self, e):
        """Adiciona uma peça à lista de peças da OS."""
        peca_nome = self.peca_dropdown.value

        try:
            preco_unitario = float(self.preco_unitario_field.value)
            if preco_unitario <= 0:
                raise ValueError("Preço unitário deve ser maior que zero.")
        except ValueError:
            ft.snack_bar = ft.SnackBar(ft.Text("Preço unitário inválido."))
            self.page.show_snack_bar(ft.snack_bar)
            return

        try:
            quantidade = int(self.quantidade_field.value)  # Quantidade como inteiro
            if quantidade <= 0:
                raise ValueError("Quantidade deve ser maior que zero.")
        except ValueError:
            ft.snack_bar = ft.SnackBar(ft.Text("Quantidade inválida."))
            self.page.show_snack_bar(ft.snack_bar)
            return

        valor_total = preco_unitario * quantidade

        try:
            self.pecas_selecionadas.append(
                {
                    "nome": peca_nome,
                    "preco_unitario": preco_unitario,
                    "quantidade": quantidade,
                    "valor_total": valor_total,
                }
            )
            self.atualizar_lista_pecas()
            self.calcular_valor_total()

            self.peca_dropdown.value = None
            self.preco_unitario_field.value = "0.00"  # Reset para string
            self.quantidade_field.value = "1"  # Reset para string

            self.page.update()
        except Exception as e:
            print(f"Erro ao adicionar peça: {e}")
            ft.snack_bar = ft.SnackBar(ft.Text("Erro ao adicionar peça."))
            self.page.show_snack_bar(ft.snack_bar)

    def formatar_moeda(self, valor):
        """Formata um valor como moeda brasileira (R$)."""
        return f"R$ {valor:.2f}"

    def calcular_valor_total(self):
        """Calcula e atualiza os valores totais da OS, incluindo a mão de obra."""
        valor_total_pecas = sum(peca["valor_total"] for peca in self.pecas_selecionadas)
        mao_de_obra = float(self.preco_mao_de_obra_field.value)
        valor_total_os = valor_total_pecas + mao_de_obra

        self.valor_total_text.value = self.formatar_moeda(valor_total_os)
        self.total_pecas_text.value = f"Total de Peças: R$ {valor_total_pecas:.2f}"
        self.mao_de_obra_text.value = f"Mão de Obra: R$ {mao_de_obra:.2f}"
        self.total_com_mao_de_obra_text.value = (
            f"Total com mão de obra: R$ {self.formatar_moeda(valor_total_os)}"
        )
        self.pagamento_avista_text.value = f"Pagamento à Vista: R$ {valor_total_os:.2f}"
        self.page.update()

    def fechar_modal_os(self, e):
        """Fecha o modal de ordem de serviço."""
        print("Fechar modal!")
        if self.page.dialog:
            
            self.page.dialog.open = False
            self.page.update()
            
            

    def criar_ordem_servico(self, e):
        """Cria a ordem de serviço no banco de dados."""
        if not all(
            [
                self.cliente_dropdown.value,
                self.carro_dropdown.value,
                self.pecas_selecionadas,
            ]
        ):
            ft.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos!"))
            self.page.show_snack_bar(ft.snack_bar)
            return

        pecas_quantidades = {}

        try:
            # Validação do campo mão de obra
            mao_de_obra_str = self.preco_mao_de_obra_field.value
            if not mao_de_obra_str or not mao_de_obra_str.strip():
                ft.snack_bar = ft.SnackBar(ft.Text("Informe o valor da mão de obra!"))
                self.page.show_snack_bar(ft.snack_bar)
                return

            mao_de_obra = float(mao_de_obra_str)

            cliente_id = int(self.cliente_dropdown.value.split(" (ID: ")[1][:-1])
            carro_id = int(self.carro_dropdown.value.split(" (ID: ")[1].split(",")[0])

            # Ponto de atenção: Validação da lista self.pecas_selecionadas
            for peca_selecionada in self.pecas_selecionadas:
                # Certifique-se de que 'nome', 'preco_unitario'
                # e 'quantidade' estão presentes e são válidos
                # ... (implemente a validação aqui) ...
                for peca in self.pecas:
                    if peca[1] == peca_selecionada["nome"]:
                        peca_id = peca[0]
                        pecas_quantidades[peca_id] = peca_selecionada["quantidade"]
                        break

            valor_total_os = (
                sum(peca["valor_total"] for peca in self.pecas_selecionadas)
                + mao_de_obra
            )

            with criar_conexao_banco_de_dados(nome_banco_de_dados) as conexao:
                for peca_id, quantidade in pecas_quantidades.items():
                    if not quantidade_em_estoque_suficiente(
                        conexao, peca_id, quantidade
                    ):
                        raise ValueError(
                            f"Quantidade insuficiente em estoque para a peça {peca_id}"
                        )

                # ----> Captura o ID da OS criada <----
                ordem_servico_id = inserir_ordem_servico(
                    conexao,
                    cliente_id,
                    carro_id,
                    pecas_quantidades,
                    valor_total_os,
                    mao_de_obra,
                )

                if ordem_servico_id is not None:
                    for peca_id, quantidade in pecas_quantidades.items():
                        atualizar_estoque_peca(conexao, peca_id, -quantidade)
                        inserir_movimentacao_peca(
                            conexao,
                            peca_id,
                            "saida",
                            quantidade,
                            ordem_servico_id,
                        )

                # Ordem correta das chamadas:
                self.gerar_pdf_os(ordem_servico_id)  # ----> Passa o ID da OS <----
                self.gerar_link_whatsapp(
                    ordem_servico_id
                )  # ----> Passa o ID da OS <----
                self.abrir_link_whatsapp()  # Abre o link se existir
                self.limpar_campos_os()  # Limpa os campos após usar
                self.fechar_modal_os(e)  # Fecha o modal principal
                ft.snack_bar = ft.SnackBar(
                    ft.Text("Ordem de Serviço criada com sucesso!")
                )
                self.page.show_snack_bar(ft.snack_bar)
                self.page.update()

        except ValueError as e:
            print(f"Erro de validação: {e}")
            ft.snack_bar = ft.SnackBar(ft.Text(str(e)))
            self.page.show_snack_bar(ft.snack_bar)
        except Exception as e:
            print(f"Erro ao criar ordem de serviço: {e}")
            ft.snack_bar = ft.SnackBar(ft.Text("Erro ao criar ordem de serviço!"))
            self.page.show_snack_bar(ft.snack_bar)

    def gerar_texto_os(self, ordem_servico_id):
        return self.formatar_os(ordem_servico_id)

    def gerar_link_whatsapp(self, ordem_servico_id):
        """Gera o link do WhatsApp com a mensagem da OS."""
        try:
            if self.cliente_dropdown.value:
                cliente_nome = self.cliente_dropdown.value.split(" (ID: ")[0]
                numero_telefone = self.buscar_numero_cliente(cliente_nome)

                if numero_telefone:
                    mensagem = self.gerar_texto_os(ordem_servico_id)
                    texto_codificado = urllib.parse.quote(mensagem)
                    self.link_whatsapp = f"https://web.whatsapp.com/send?phone={numero_telefone}&text={texto_codificado}"
                    print(f"Link do WhatsApp: {self.link_whatsapp}")
                    return self.link_whatsapp
                else:
                    print(
                        f"Número de telefone não encontrado para o cliente: {cliente_nome}"
                    )
                    return None
            else:
                print("Erro: Nenhum cliente selecionado no dropdown.")
                return None
        except Exception as e:
            print(f"Erro ao gerar link do WhatsApp: {e}")
            return None

    def buscar_numero_cliente(self, cliente_nome):
        """
        Busca o número de telefone de um cliente pelo nome.

        Args:
            cliente_nome (str): O nome do cliente.

        Returns:
            str: O número de telefone do cliente ou None se não encontrado.
        """
        print(f"Nome do cliente sendo buscado: '{cliente_nome}'")
        try:
            with criar_conexao_banco_de_dados(nome_banco_de_dados) as conexao:
                cursor = conexao.cursor()

                consulta_sql = "SELECT telefone FROM clientes WHERE nome = ?"
                print(f"Consulta SQL: {consulta_sql}, Parâmetros: {cliente_nome}")
                cursor.execute(
                    "SELECT telefone FROM clientes WHERE nome = ?",
                    (cliente_nome,),
                )
                resultado = cursor.fetchone()
                print(f"Resultado da consulta: {resultado}")
                if resultado:
                    print(f"Número de telefone encontrado: {resultado[0]}")
                    return resultado[0]
                else:
                    print(f"Nenhum número de telefone encontrado para {cliente_nome}")
                    ft.snack_bar = ft.SnackBar(
                        ft.Text(
                            f"Cliente {cliente_nome} não possui número de telefone cadastrado."
                        )
                    )
                    self.page.show_snack_bar(ft.snack_bar)
                    return None

        except sqlite3.Error as e:
            print(f"Erro ao buscar número do cliente: {e}")
            return None

    def gerar_pdf_os(self, ordem_servico_id):

        try:
            cliente_nome = self.cliente_dropdown.value.split(" (ID: ")[0]
            placa_carro = self.carro_dropdown.value.split("Placa: ")[1][:-1]
            data_hora_criacao = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

            # Formatar os itens da OS para a tabela
            dados_tabela = [
                ["Material", "Valor Unitário", "Quantidade", "Valor Total"]
            ]  # Cabeçalho
            for peca in self.pecas_selecionadas:
                dados_tabela.append(
                    [
                        peca["nome"],
                        f"R$ {peca['preco_unitario']:.2f}",
                        peca["quantidade"],
                        f"R$ {peca['valor_total']:.2f}",
                    ]
                )

            # Criar a tabela com ReportLab
            tabela = Table(dados_tabela)
            estilo_tabela = TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),  # Alinhamento à esquerda
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # Alinhamento vertical
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),  # Linhas da tabela
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),  # Cabeçalho
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),  # Negrito no cabeçalho
                ]
            )
            tabela.setStyle(estilo_tabela)

            valor_total_pecas = sum(
                peca["valor_total"] for peca in self.pecas_selecionadas
            )
            mao_de_obra = self.maodeobra
            dados_tabela.append(["Mão de Obra", "", "", f"R$ {mao_de_obra:.2f}"])
            valor_total_os = valor_total_pecas + mao_de_obra

            nome_arquivo = f"OS{ordem_servico_id}_{cliente_nome}_{placa_carro}_{data_hora_criacao}.pdf"
            caminho_pasta = "./historico"
            os.makedirs(caminho_pasta, exist_ok=True)
            caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)

            doc = SimpleDocTemplate(
                caminho_arquivo,
                pagesize=letter,
                title=f"Ordem de Serviço - Nº {ordem_servico_id}",
            )
            conteudo = [
                Paragraph(
                    f"**Ordem de Serviço - Nº {ordem_servico_id}**",
                    getSampleStyleSheet()["Heading1"],
                ),
                Spacer(1, 12),
                Paragraph(
                    f"**Cliente:** {cliente_nome}", getSampleStyleSheet()["Normal"]
                ),
                Paragraph(
                    f"**Placa do Carro:** {placa_carro}",
                    getSampleStyleSheet()["Normal"],
                ),
                Paragraph(
                    f"**Data de Criação:** {data_hora_criacao}",
                    getSampleStyleSheet()["Normal"],
                ),
                Spacer(1, 12),
                tabela,
                Spacer(1, 12),
                Paragraph(
                    f"Valor das Peças: R$ {valor_total_pecas:.2f}",
                    getSampleStyleSheet()["Normal"],
                ),
                Paragraph(
                    f"Valor da Mão de Obra: R$ {mao_de_obra:.2f}",
                    getSampleStyleSheet()["Normal"],
                ),
                Paragraph(
                    f"**Valor Total da OS: R$ {valor_total_os:.2f}**",
                    getSampleStyleSheet()["Heading3"],
                ),
            ]
            doc.build(conteudo)
            print(f"PDF da OS gerado com sucesso em: {caminho_arquivo}")

        except Exception as e:
            print(f"Erro ao gerar PDF da OS: {e}")

    def abrir_link_whatsapp(self, e=None):
        """Abre o link do WhatsApp se ele tiver sido gerado."""
        if self.link_whatsapp:
            try:
                print("Abrir link!")
                self.page.launch_url(self.link_whatsapp)
            except Exception as e:
                print(f"Erro ao abrir o self.link_whatsapp: {e}")

    def limpar_campos_os(self):
        """Limpa os campos após a criação da ordem de serviço."""
        self.cliente_dropdown.value = None
        self.carro_dropdown.value = None
        self.peca_dropdown.value = None
        self.preco_unitario_field.value = 0.0
        self.quantidade_field.value = 0.0
        self.preco_mao_de_obra_field.value = "0"
        self.pecas_selecionadas = []
        self.atualizar_lista_pecas()
        self.calcular_valor_total()
        self.link_whatsapp = None  # Limpa o link após o envio

        self.page.update()

    def atualizar_interface(self, e):
        """
        Atualiza a interface do usuário após mudanças no formulário.

        Args:
            e: O evento que acionou a atualização.
        """
        self.calcular_valor_total()  # Recalcula totais quando algo muda
        self.page.update()
        
        
        
   #============================
   # Orçamento
   #============================     

    def enviar_orcamento(self, e):
        """Gera o orçamento e envia por WhatsApp."""
        if not all([self.cliente_dropdown.value, self.carro_dropdown.value]):
            ft.snack_bar = ft.SnackBar(ft.Text("Preencha os campos Cliente e Carro!"))
            self.page.show_snack_bar(ft.snack_bar)
            return

        try:
            # 1. Gerar PDF do Orçamento
            self.gerar_pdf_orcamento()

            # 2. Gerar Link do WhatsApp com o PDF
            link_whatsapp = self.gerar_link_whatsapp_orcamento()
            if link_whatsapp:
                self.page.launch_url(link_whatsapp)
                self.mostrar_sucesso("Orçamento enviado com sucesso!")
                self.limpar_campos_os()  # Limpa os campos após usar
                self.fechar_modal_os(e)  # Fecha o modal principal
                ft.snack_bar = ft.SnackBar(
                    ft.Text("Orçamento enviado com sucesso!")
                )
                self.page.show_snack_bar(ft.snack_bar)
                self.page.update()
            else:
                self.mostrar_erro("Erro ao gerar link do WhatsApp.")

        except Exception as e:
            print(f"Erro ao enviar orçamento: {e}")
            self.mostrar_erro("Erro ao enviar orçamento.")

    def gerar_pdf_orcamento(self):
        """Gera um PDF do orçamento."""
        # Utilize a lógica da função gerar_pdf_os, adaptando para o orçamento
        try:
            ordem_servico_id = "Orcamento De"  # Ou qualquer outro identificador para orçamento
            cliente_nome = self.cliente_dropdown.value.split(" (ID: ")[0]
            placa_carro = self.carro_dropdown.value.split("Placa: ")[1][:-1]
            data_hora_criacao = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

            # Formatar os itens da OS para a tabela
            dados_tabela = [
                ["Material", "Valor Unitário", "Quantidade", "Valor Total"]
            ]  # Cabeçalho
            for peca in self.pecas_selecionadas:
                dados_tabela.append(
                    [
                        peca["nome"],
                        f"R$ {peca['preco_unitario']:.2f}",
                        peca["quantidade"],
                        f"R$ {peca['valor_total']:.2f}",
                    ]
                )

            # Criar a tabela com ReportLab
            tabela = Table(dados_tabela)
            estilo_tabela = TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),  # Alinhamento à esquerda
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # Alinhamento vertical
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),  # Linhas da tabela
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),  # Cabeçalho
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),  # Negrito no cabeçalho
                ]
            )
            tabela.setStyle(estilo_tabela)

            valor_total_pecas = sum(
                peca["valor_total"] for peca in self.pecas_selecionadas
            )
            mao_de_obra = self.maodeobra
            dados_tabela.append(["Mão de Obra", "", "", f"R$ {mao_de_obra:.2f}"])
            valor_total_os = valor_total_pecas + mao_de_obra

            nome_arquivo = (
                f"ORC{cliente_nome}_{placa_carro}_{data_hora_criacao}.pdf"
            )
            caminho_pasta = "./orcamento"
            os.makedirs(caminho_pasta, exist_ok=True)
            caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)

            doc = SimpleDocTemplate(
                caminho_arquivo,
                pagesize=letter,
                title=f"Orçamento - Nº {ordem_servico_id}",
            )
            conteudo = [
                Paragraph(
                    f"**Orçamento - Nº {ordem_servico_id}**",
                    getSampleStyleSheet()["Heading1"],
                ),
                Spacer(1, 12),
                Paragraph(
                    f"**Cliente:** {cliente_nome}", getSampleStyleSheet()["Normal"]
                ),
                Paragraph(
                    f"**Placa do Carro:** {placa_carro}",
                    getSampleStyleSheet()["Normal"],
                ),
                Paragraph(
                    f"**Data de Criação:** {data_hora_criacao}",
                    getSampleStyleSheet()["Normal"],
                ),
                Spacer(1, 12),
                tabela,
                Spacer(1, 12),
                Paragraph(
                    f"Valor das Peças: R$ {valor_total_pecas:.2f}",
                    getSampleStyleSheet()["Normal"],
                ),
                Paragraph(
                    f"Valor da Mão de Obra: R$ {mao_de_obra:.2f}",
                    getSampleStyleSheet()["Normal"],
                ),
                Paragraph(
                    f"**Valor Total da OS: R$ {valor_total_os:.2f}**",
                    getSampleStyleSheet()["Heading3"],
                ),
            ]
            doc.build(conteudo)
            print(f"PDF da OS gerado com sucesso em: {caminho_arquivo}")

        except Exception as e:
            print(f"Erro ao gerar PDF da OS: {e}")
        pass  # Implemente a lógica para gerar o PDF do orçamento
    
    def gerar_texto_orcamento(self):
        return self.formatar_orcamento()    

    def formatar_orcamento(self):
        """Formata os dados da OS no formato desejado."""
        cliente_nome = self.cliente_dropdown.value.split(" (ID: ")[0]
        placa_carro = self.carro_dropdown.value.split("Placa: ")[1][:-1]
        data_hora_criacao = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        mao_de_obra = self.maodeobra

        # Cabeçalho
        os_formatada = f"**ORÇAMENTO**\n\n"
        os_formatada += f"**Cliente:** {cliente_nome}\n"
        os_formatada += f"**Placa do Carro:** {placa_carro}\n"
        os_formatada += f"**Data do Orçamento:** {data_hora_criacao}\n\n"

        # Itens em tabela
        os_formatada += "**Itens ORÇAMENTO:**\n"
        os_formatada += "| Material | Valor Unitário | Quantidade | Valor Total |\n"
        os_formatada += "|---|---|---|---| \n"

        for peca in self.pecas_selecionadas:
            os_formatada += (
                f"| {peca['nome']} "
                f"| R$ {peca['preco_unitario']:.2f} "
                f"| {peca['quantidade']} "
                f"| R$ {peca['valor_total']:.2f} |\n"
            )

            # Valores totais
        valor_total_pecas = sum(peca["valor_total"] for peca in self.pecas_selecionadas)
        mao_de_obra = self.maodeobra
        valor_total_os = valor_total_pecas + mao_de_obra

        os_formatada += f"\nValor das Peças: R$ {valor_total_pecas:.2f}\n"
        os_formatada += f"Valor da Mão de Obra: R$ {mao_de_obra:.2f}\n"
        os_formatada += f"**Valor Total da OS: R$ {valor_total_os:.2f}**"

        return os_formatada

    def gerar_link_whatsapp_orcamento(self):
        """Gera o link do WhatsApp para enviar o orçamento."""
        # Reutilização da lógica de gerar_link_whatsapp, adaptando a mensagem
        try:
            if self.cliente_dropdown.value:
                cliente_nome = self.cliente_dropdown.value.split(" (ID: ")[0]
                numero_telefone = self.buscar_numero_cliente(cliente_nome)

                if numero_telefone:
                    # Adaptação da mensagem para o orçamento
                    
                    
                    mensagem = self.gerar_texto_orcamento()
                    texto_codificado = urllib.parse.quote(mensagem)
                    link_whatsapp = f"https://web.whatsapp.com/send?phone={numero_telefone}&text={texto_codificado}"
                    print(f"Link do WhatsApp: {link_whatsapp}")
                    return link_whatsapp
                else:
                    print(
                        f"Número de telefone não encontrado para o cliente: {cliente_nome}"
                    )
                    return None
            else:
                print("Erro: Nenhum cliente selecionado no dropdown.")
                return None
        except Exception as e:
            print(f"Erro ao gerar link do WhatsApp: {e}")
            return None
        pass  # Implemente a lógica para gerar o link do WhatsApp

    def mostrar_erro(self, mensagem):
        ft.snack_bar = ft.SnackBar(ft.Text(mensagem))
        self.page.show_snack_bar(ft.snack_bar)

    def mostrar_sucesso(self, mensagem):
        ft.snack_bar = ft.SnackBar(ft.Text(mensagem))
        self.page.show_snack_bar(ft.snack_bar)



    