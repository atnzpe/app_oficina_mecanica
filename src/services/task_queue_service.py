# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE SERVIÇO DA FILA DE TAREFAS (task_queue_service.py)
#
# OBJETIVO: Isolar a lógica da thread que processa operações de banco de dados
#           de forma assíncrona.
#
# CORREÇÃO (BUG FIX):
#   - Garantido que a 'fila_db' seja importada de sua fonte original,
#     'src.database.database', para que este serviço possa consumir as tarefas.
# =================================================================================
import flet as ft
import sqlite3
import queue
import logging

# --- IMPORT CORRIGIDO ---
# Importa a função de conexão e a fila de tarefas do módulo de database.
from src.database.database import get_db_connection, NOME_BANCO_DE_DADOS, fila_db
# Importa o módulo de queries para executar as operações de escrita.
from src.database import queries

def processar_fila_db(page: ft.Page):
    """
    Função executada numa thread para processar operações de banco de dados.
    Ela fica em um loop infinito, aguardando por tarefas na 'fila_db'.
    """
    logging.info("Thread de processamento do DB iniciada.")
    
    while True:
        try:
            # Tenta pegar uma tarefa da fila. Fica bloqueada por até 1 segundo.
            # Se não houver tarefa, uma exceção 'queue.Empty' é lançada.
            operacao, dados = fila_db.get(timeout=1.0)
            logging.info(f"Processando operação da fila: {operacao}")

            # --- LÓGICA DE PROCESSAMENTO DAS TAREFAS ---
            if operacao == "criar_ordem_servico":
                # Desempacota os dados recebidos.
                os_id = queries.inserir_ordem_servico(
                    cliente_id=dados["cliente_id"],
                    carro_id=dados["carro_id"],
                    pecas_quantidades=dados["pecas_quantidades"],
                    valor_total=dados["valor_total"],
                    mao_de_obra=dados["mao_de_obra"]
                )
                if os_id:
                    # Envia uma mensagem para a UI via PubSub para notificar o sucesso.
                    page.pubsub.send_all({"topic": "os_criada", "mensagem": f"OS #{os_id} criada com sucesso!"})
                else:
                    page.pubsub.send_all({"topic": "erro_os", "mensagem": "Falha ao criar a OS."})
            
            # Adicionar aqui a lógica para outras operações, como "cadastrar_carro", etc.

        except queue.Empty:
            # Se a fila estiver vazia, simplesmente continua o loop.
            continue
        except Exception as e:
            # Captura qualquer outro erro inesperado para não quebrar a thread.
            logging.error(f"Erro inesperado na thread do banco de dados: {e}", exc_info=True)