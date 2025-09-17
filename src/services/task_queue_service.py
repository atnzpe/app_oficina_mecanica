# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE SERVIÇO DA FILA DE TAREFAS (task_queue_service.py)
#
# OBJETIVO: Isolar a lógica da thread que processa operações de banco de dados
#           de forma assíncrona. Este é um serviço de fundo que pode ser
#           iniciado pelo `main.py` e utilizado por qualquer ViewModel.
#
# SEÇÕES ALTERADAS NESTA REATORAÇÃO (ISSUE #1):
#   - Este é um ficheiro completamente novo.
#   - A função `processar_fila_db` foi movida do antigo `oficina_app.py` para cá,
#     seguindo a nossa nova arquitetura.
# =================================================================================
import flet as ft
import sqlite3
import queue
import logging
from src.database.database import criar_conexao_banco_de_dados, NOME_BANCO_DE_DADOS, fila_db

def processar_fila_db(page: ft.Page):
    """
    Função executada numa thread para processar operações de banco de dados.
    """
    logging.info("Thread de processamento do DB iniciada.")
    conexao_db = criar_conexao_banco_de_dados(NOME_BANCO_DE_DADOS)
    if not conexao_db:
        logging.error("FALHA CRÍTICA: A thread do banco de dados não conseguiu conectar-se.")
        return

    while True:
        try:
            # Aguarda por uma tarefa na fila.
            operacao, dados = fila_db.get(timeout=1.0)
            logging.info(f"Processando operação da fila: {operacao}")

            # A lógica para cada tipo de operação (ex: cadastrar_carro,
            # criar_ordem_servico, etc.) será expandida aqui.
            if operacao == "criar_ordem_servico":
                # Exemplo:
                # inserir_ordem_servico(conexao_db, **dados)
                page.pubsub.send_all({"topic": "os_criada", "mensagem": "OS criada com sucesso!"})

            elif operacao == "cadastrar_carro":
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

        except queue.Empty:
            continue
        except Exception as e:
            logging.error(f"Erro inesperado na thread do banco de dados: {e}")