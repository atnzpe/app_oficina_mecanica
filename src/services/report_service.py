from fpdf import FPDF
import os
import flet as ft
from src.database.database import criar_conexao_banco_de_dados, banco_de_dados, nome_banco_de_dados
import sqlite3
from datetime import datetime
from flet import SnackBar, AlertDialog, Text, Column, Dropdown, ElevatedButton, TextField

data_hora_criacao = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")


def gerar_relatorio_os(conexao, page):
    """Gera relatório em PDF com Data da OS, Cliente, Carro e Valor Total."""
    try:
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT 
                os.data_criacao,       -- Data da OS
                c.nome AS nome_cliente,  -- Nome do Cliente
                car.modelo || ' - ' || car.placa AS carro, -- Carro (Modelo - Placa)
                os.valor_total         -- Valor Total da OS
            FROM 
                ordem_servico os
            JOIN 
                clientes c ON os.cliente_id = c.id
            JOIN 
                carros car ON os.carro_id = car.id
        """
        )
        os_data = cursor.fetchall()

        headers = [
            "Data da OS",
            "Cliente",
            "Carro",
            "Valor Total da OS",
        ]
        data = [list(row) for row in os_data]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for header in headers:
            pdf.cell(45, 10, txt=header, border=1)
        pdf.ln()

        for row in data:
            for item in row:
                pdf.cell(45, 10, txt=str(item), border=1)
            pdf.ln()

        pdf.output(f"./report/relatorio_ordem_servico{data_hora_criacao}.pdf")
        os.startfile(f"./report/relatorio_ordem_servico{data_hora_criacao}.pdf")

        page.snack_bar = ft.SnackBar(ft.Text("Relatório de OSs gerado com sucesso!"))
        page.snack_bar.open = True
        page.update()

    except Exception as e:
        print(f"Erro ao gerar relatório de OSs: {e}")
        mostrar_erro(page, f"Erro ao gerar relatório de OSs: {e}")


def gerar_relatorio_estoque(conexao, page):
    """Gera um relatório de estoque em PDF."""
    try:
        movimentacoes = carregar_dados_saldo_estoque(conexao)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        headers = [
            "ID",
            "Nome",
            "Referência",
            "Total Entradas",
            "Total Saídas",
            "Estoque Final",
        ]
        for header in headers:
            pdf.cell(30, 10, txt=header, border=1)
        pdf.ln()

        for peca in movimentacoes:
            pdf.cell(30, 10, txt=str(peca[0]), border=1)
            pdf.cell(30, 10, txt=str(peca[1]), border=1)
            pdf.cell(30, 10, txt=str(peca[2]), border=1)
            pdf.cell(30, 10, txt=str(peca[3]), border=1)
            pdf.cell(30, 10, txt=str(peca[4]), border=1)
            pdf.cell(30, 10, txt=str(peca[3] - peca[4]), border=1)
            pdf.ln()

        pdf.output("./report/relatorio_estoque.pdf")

        page.snack_bar = ft.SnackBar(ft.Text("Relatório de estoque gerado com sucesso!"))
        page.snack_bar.open = True
        page.update()

    except Exception as e:
        print(f"Erro ao gerar relatório de estoque: {e}")
        mostrar_erro(page, f"Erro ao gerar relatório de estoque: {e}")


def carregar_dados_saldo_estoque(conexao):
    """Carrega os dados de movimentação de peças do banco de dados."""
    cursor = conexao.cursor()
    cursor.execute(
        """
        SELECT 
            p.id,
            p.nome, 
            p.referencia,
            COALESCE(SUM(CASE WHEN mp.tipo_movimentacao = 'entrada' THEN mp.quantidade ELSE 0 END), 0) AS total_entradas,
            COALESCE(SUM(CASE WHEN mp.tipo_movimentacao = 'saida' THEN mp.quantidade ELSE 0 END), 0) AS total_saídas
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


def mostrar_erro(page, mensagem):
    """Exibe uma snackbar de erro."""
    page.snack_bar = ft.SnackBar(ft.Text(mensagem), bgcolor="red")
    page.snack_bar.open = True
    page.update()

def abrir_modal_os_por_cliente(page, clientes):
    """Abre o modal para consulta de OSs por cliente e data."""

    cliente_dropdown = Dropdown(
        width=200,
        options=[ft.dropdown.Option(f"{cliente[1]} (ID: {cliente[0]})") for cliente in clientes],
    )
    data_inicio_field = TextField(label="Data Início (AAAA-MM-DD)", width=200)
    data_fim_field = TextField(label="Data Fim (AAAA-MM-DD)", width=200)

    def gerar_relatorio_os_por_cliente(e):
        """Gera o relatório de OSs por cliente e data."""
        cliente_selecionado = cliente_dropdown.value
        data_inicio = data_inicio_field.value
        data_fim = data_fim_field.value

        if not all([cliente_selecionado, data_inicio, data_fim]):
            mostrar_erro(page, "Preencha todos os campos!")
            return

        try:
            cliente_id = int(cliente_selecionado.split(" (ID: ")[1][:-1])
            datetime.strptime(data_inicio, "%Y-%m-%d")  # Valida formato da data
            datetime.strptime(data_fim, "%Y-%m-%d")  # Valida formato da data

            with criar_conexao_banco_de_dados(nome_banco_de_dados) as conexao:
                relatorio_os_por_cliente_data(conexao, page, cliente_id, data_inicio, data_fim)

            dlg.open = False
            page.update()

        except ValueError:
            mostrar_erro(page, "Formato de data inválido. Use AAAA-MM-DD.")
        except Exception as e:
            print(f"Erro ao gerar relatório de OSs por cliente: {e}")
            mostrar_erro(page, f"Erro ao gerar relatório: {e}")

    dlg = AlertDialog(
        modal=True,
        title=Text("Relatório de OSs por Cliente"),
        content=Column(
            [
                Text("Selecione o Cliente:"),
                cliente_dropdown,
                Text("Data Início (AAAA-MM-DD):"),
                data_inicio_field,
                Text("Data Fim (AAAA-MM-DD):"),
                data_fim_field,
                ElevatedButton("Gerar Relatório", on_click=gerar_relatorio_os_por_cliente),
            ]
        ),
        actions=[
            ft.TextButton("Fechar", on_click=fechar_modal),  # Botão Fechar
        ]
    )

    page.dialog = dlg
    dlg.open = True
    page.update()


def relatorio_os_por_cliente_data(conexao, page, cliente_id, data_inicio, data_fim):
    """Gera o relatório de OSs por cliente e data em PDF."""
    try:
        cursor = conexao.cursor()
        cursor.execute(
            """
            SELECT 
                os.data_criacao,
                c.nome AS nome_cliente,
                car.modelo || ' - ' || car.placa AS carro,
                os.valor_total
            FROM 
                ordem_servico os
            JOIN 
                clientes c ON os.cliente_id = c.id
            JOIN 
                carros car ON os.carro_id = car.id
            WHERE 
                os.cliente_id = ? AND os.data_criacao BETWEEN ? AND ?
        """,
            (cliente_id, data_inicio, data_fim),
        )
        os_data = cursor.fetchall()

        if not os_data:
            mostrar_erro(page, "Nenhuma OS encontrada para o período.")
            return

        headers = ["Data da OS", "Cliente", "Carro", "Valor Total da OS"]
        data = [list(row) for row in os_data]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for header in headers:
            pdf.cell(45, 10, txt=header, border=1)
        pdf.ln()

        for row in data:
            for item in row:
                pdf.cell(45, 10, txt=str(item), border=1)
            pdf.ln()

        nome_cliente = os_data[0][1]  # Obter o nome do cliente do resultado da consulta
        nome_arquivo = f"relatorio_os_{nome_cliente}_{data_inicio}_{data_fim}.pdf"
        caminho_pasta = "./report"
        os.makedirs(caminho_pasta, exist_ok=True)
        caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
        pdf.output(caminho_arquivo)

        os.startfile(caminho_arquivo)

        mostrar_sucesso(page, "Relatório de OSs por cliente gerado com sucesso!")

    except Exception as e:
        print(f"Erro ao gerar relatório de OSs por cliente: {e}")
        mostrar_erro(page, f"Erro ao gerar relatório: {e}")
        
def fechar_modal(self):
        """Fecha qualquer modal aberto."""
        self.page.dialog.open = False
        self.page.update()    