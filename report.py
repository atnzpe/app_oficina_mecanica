from fpdf import FPDF
import os
import flet as ft
from database import criar_conexao_banco_de_dados,banco_de_dados, nome_banco_de_dados
import sqlite3
from flet import SnackBar


def gerar_relatorio_os(conexao, page):
    """
    Gera um relatório em PDF com a Data da OS, Cliente, Carro e Valor Total da OS.

    Args:
        conexao (sqlite3.Connection): Conexão com o banco de dados.
        page (flet.Page): Página do Flet para exibir mensagens.
    """
    try:
        cursor = conexao.cursor()

        # Consulta SQL para obter os dados da OS, cliente e carro
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

        # Formatar os dados para o relatório
        headers = [
            "Data da OS",
            "Cliente",
            "Carro",
            "Valor Total da OS"
        ]
        data = []

        for row in os_data:
            data.append(list(row))

        # Criar o relatório em PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Adicionar cabeçalho
        for header in headers:
            pdf.cell(40, 10, txt=header, border=1)
        pdf.ln()

        # Adicionar dados das OSs
        for row in data:
            for item in row:
                pdf.cell(40, 10, txt=str(item), border=1)
            pdf.ln()

        # Salvar o relatório
        pdf.output("./report/relatorio_ordem_servico.pdf")
        
        # Abrir o relatório gerado
        os.startfile("./report/relatorio_ordem_servico.pdf")

        # Exibir mensagem de sucesso
        page.snack_bar = ft.SnackBar(ft.Text("Relatório de OSs gerado com sucesso!"))
        page.snack_bar.open = True
        page.update()

    except Exception as e:
        print(f"Erro ao gerar relatório de OSs: {e}")
        page.snack_bar = ft.SnackBar(
            ft.Text(f"Erro ao gerar relatório de OSs: {e}"), bgcolor="red"
        )
        page.snack_bar.open = True
        page.update()


def gerar_relatorio_estoque(conexao, page):
    """
    Gera um relatório de estoque em PDF com base nos dados de movimentação de peças.

    Args:
        conexao (sqlite3.Connection): Conexão com o banco de dados.
        page (flet.Page): Página do Flet para exibir mensagens.
    """
    try:
        # Carregar os dados do estoque
        movimentacoes = carregar_dados_saldo_estoque(conexao)

        # Criar o relatório em PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Adicionar cabeçalho
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

        # Adicionar dados das peças
        for peca in movimentacoes:
            pdf.cell(30, 10, txt=str(peca[0]), border=1)  # ID
            pdf.cell(30, 10, txt=str(peca[1]), border=1)  # Nome
            pdf.cell(30, 10, txt=str(peca[2]), border=1)  # Referência
            pdf.cell(30, 10, txt=str(peca[3]), border=1)  # Total Entradas
            pdf.cell(30, 10, txt=str(peca[4]), border=1)  # Total Saídas
            pdf.cell(30, 10, txt=str(peca[3] - peca[4]), border=1)  # Estoque Final
            pdf.ln()

        # Salvar o relatório
        pdf.output("relatorio_estoque.pdf")

        # Exibir mensagem de sucesso
        page.snack_bar = ft.SnackBar(
            ft.Text("Relatório de estoque gerado com sucesso!")
        )
        page.snack_bar.open = True
        page.update()

    except Exception as e:
        print(f"Erro ao gerar relatório de estoque: {e}")
        page.snack_bar = ft.SnackBar(
            ft.Text(f"Erro ao gerar relatório de estoque: {e}"), bgcolor="red"
        )
        page.snack_bar.open = True
        page.update()


def carregar_dados_saldo_estoque(conexao):
    """
    Carrega os dados de movimentação de peças do banco de dados,
    calculando o saldo final para cada peça.

    Args:
        conexao (sqlite3.Connection): Conexão com o banco de dados.

    Returns:
        list: Lista de tuplas contendo os dados de movimentação de cada peça.
    """
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


def abrir_modal_os_por_cliente(self, e):
    """Abre o modal para selecionar as OSs por cliente."""
    # Implementar lógica para exibir e selecionar OSs por cliente aqui
    print("Abrir modal de OSs por cliente...")
    self.fechar_modal(e)