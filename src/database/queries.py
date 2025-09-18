# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE CONSULTAS AO BANCO DE DADOS (queries.py)
#
# OBJETIVO: Centralizar TODAS as interações de leitura e escrita com o banco de
#           dados. Este arquivo é a única "porta" para a base de dados,
#           implementando o Padrão Repositório.
#
# VERSÃO ATUAL: Contém as funções de negócio para usuários, clientes, carros,
#              peças e ordens de serviço, com gerenciamento de conexão seguro
#              e logging detalhado.
# =================================================================================

# --- IMPORTAÇÕES DE BIBLIOTECAS ---
import logging
import sqlite3
from datetime import datetime
from typing import List

# --- IMPORTAÇÕES DO PROJETO ---

# Importa a função de conexão do nosso módulo de banco de dados.
from src.database.database import get_db_connection

# Importa as classes de modelo para que as funções possam retornar objetos
# fortemente tipados (ex: uma lista de Clientes), o que melhora a clareza
# e a segurança do código nos ViewModels.
from src.models.models import Usuario, Cliente, Carro, Peca

# --- CONFIGURAÇÃO DO LOGGER ---
logger = logging.getLogger("DB_QUERIES")

# =================================================================================
# QUERIES DE USUÁRIO E ONBOARDING
# =================================================================================

def verificar_existencia_usuario() -> bool:
    """Verifica se existe qualquer usuário cadastrado no banco de dados."""
    logger.debug("Executando query para verificar se há usuários.")
    try:
        # Usa 'with' para garantir que a conexão seja aberta e fechada automaticamente.
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT 1 FROM usuarios LIMIT 1")
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Erro ao verificar a existência de usuário: {e}", exc_info=True)
        return True

def buscar_usuario_por_nome(nome_usuario: str) -> Usuario | None:
    """Busca um usuário pelo seu nome de login."""
    logger.debug(f"Buscando usuário pelo nome: {nome_usuario}")
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM usuarios WHERE nome = ?", (nome_usuario,))
            dados_usuario = cursor.fetchone()
            # Se encontrar, converte a linha do banco (que se comporta como dicionário)
            # em um objeto do tipo Usuario.
            return Usuario(**dados_usuario) if dados_usuario else None
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar usuário por nome: {e}", exc_info=True)
        return None

def criar_usuario(nome: str, senha_hash: str, perfil: str):
    """Insere um novo usuário no banco de dados."""
    logger.info(f"Executando query para criar usuário '{nome}' com perfil '{perfil}'.")
    try:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO usuarios (nome, senha, perfil) VALUES (?, ?, ?)",
                (nome, senha_hash, perfil),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        logger.warning(f"Tentativa de criar usuário com nome que já existe: '{nome}'.")
        raise
    except sqlite3.Error as e:
        logger.error(f"Erro ao criar usuário: {e}", exc_info=True)
        raise

def has_establishment(user_id: int) -> bool:
    """
    Verifica se um usuário já possui um estabelecimento (oficina) cadastrado.
    Isso determina se ele precisa passar pelo onboarding.
    """
    logger.debug(f"Verificando se o usuário ID {user_id} possui estabelecimento.")
    try:
        with get_db_connection() as conn:
            # Simplificação: assume que a existência de qualquer cliente significa que o onboarding foi feito.
            cursor = conn.execute("SELECT 1 FROM clientes LIMIT 1")
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Erro ao verificar estabelecimento para o usuário {user_id}: {e}", exc_info=True)
        return False

def complete_onboarding(user_id: int, user_name: str, establishment_name: str):
    """
    Salva os dados do onboarding.
    - Atualiza o nome do usuário.
    - Cria o primeiro 'cliente' que representa a própria oficina.
    """
    logger.info(f"Completando onboarding para o usuário ID {user_id}.")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET nome = ? WHERE id = ?", (user_name, user_id))
            cursor.execute(
                "INSERT INTO clientes (nome, telefone, endereco, email) VALUES (?, ?, ?, ?)",
                (establishment_name, "N/A", "N/A", "N/A"),
            )
            conn.commit()
            logger.info(f"Onboarding concluído. Usuário '{user_name}' e oficina '{establishment_name}' configurados.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao salvar dados do onboarding: {e}", exc_info=True)
        raise

# =================================================================================
# QUERIES DE CLIENTES E CARROS
# =================================================================================

def obter_clientes() -> List[Cliente]:
    """Retorna uma lista de todos os clientes."""
    logger.debug("Executando query para obter todos os clientes.")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes ORDER BY nome")
            return [Cliente(**row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Erro ao obter clientes: {e}", exc_info=True)
        return []

def obter_carros_por_cliente(cliente_id: int) -> List[Carro]:
    """Retorna uma lista de carros de um cliente específico."""
    logger.debug(f"Executando query para obter carros do cliente ID: {cliente_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM carros WHERE cliente_id = ?", (cliente_id,))
            return [Carro(**row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Erro ao obter carros do cliente {cliente_id}: {e}", exc_info=True)
        return []

def atualizar_carro(carro_id: int, cliente_id: int) -> bool:
    """Atualiza o dono (cliente_id) de um carro no banco de dados."""
    logger.info(f"Executando query para atualizar dono do carro ID {carro_id} para cliente ID {cliente_id}.")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE carros SET cliente_id = ? WHERE id = ?", (cliente_id, carro_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Erro ao atualizar o carro no banco de dados: {e}", exc_info=True)
        return False

# =================================================================================
# QUERIES DE PEÇAS E ESTOQUE
# =================================================================================

def obter_pecas() -> List[Peca]:
    """Retorna uma lista de todas as peças."""
    logger.debug("Executando query para obter todas as peças.")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pecas ORDER BY nome")
            return [Peca(**row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Erro ao obter peças: {e}", exc_info=True)
        return []

def atualizar_estoque_peca(peca_id: int, quantidade_movimentada: int):
    """
    Atualiza o estoque de uma peça.
    :param peca_id: O ID da peça a ser atualizada.
    :param quantidade_movimentada: Quantidade a ser adicionada (positiva para entrada, negativa para saída).
    """
    logger.info(f"Executando query para atualizar estoque da peça {peca_id}. Movimentação: {quantidade_movimentada}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pecas SET quantidade_em_estoque = quantidade_em_estoque + ? WHERE id = ?",
                (quantidade_movimentada, peca_id),
            )
            conn.commit()
            logger.info(f"Estoque da peça {peca_id} atualizado com sucesso.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao atualizar o estoque da peça {peca_id}: {e}", exc_info=True)

def quantidade_em_estoque_suficiente(peca_id: int, quantidade_necessaria: int) -> bool:
    """Verifica se a quantidade em estoque é suficiente para a peça."""
    logger.debug(f"Verificando estoque para peça {peca_id}. Necessário: {quantidade_necessaria}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantidade_em_estoque FROM pecas WHERE id = ?", (peca_id,))
            resultado = cursor.fetchone()

            if resultado is None:
                logger.warning(f"Peça com ID {peca_id} não encontrada ao verificar estoque.")
                return False

            quantidade_em_estoque = resultado["quantidade_em_estoque"]
            return quantidade_em_estoque >= quantidade_necessaria
    except sqlite3.Error as e:
        logger.error(f"Erro ao verificar a quantidade em estoque da peça {peca_id}: {e}", exc_info=True)
        return False

# =================================================================================
# QUERIES DE ORDEM DE SERVIÇO E MOVIMENTAÇÕES
# =================================================================================

def inserir_ordem_servico(cliente_id: int, carro_id: int, pecas_quantidades: dict, valor_total: float, mao_de_obra: float) -> int | None:
    """
    Insere uma nova ordem de serviço e suas peças associadas no banco de dados.
    Esta função executa como uma transação: ou tudo é salvo, ou nada é.
    """
    logger.info(f"Iniciando transação para inserir nova Ordem de Serviço para o cliente {cliente_id}.")
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ordem_servico (cliente_id, carro_id, data_criacao, valor_total, mao_de_obra) VALUES (?, ?, ?, ?, ?)",
            (cliente_id, carro_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), valor_total, mao_de_obra),
        )
        ordem_servico_id = cursor.lastrowid
        logger.debug(f"Ordem de Serviço principal criada com ID: {ordem_servico_id}.")

        for peca_id, quantidade in pecas_quantidades.items():
            cursor.execute(
                "INSERT INTO PecasOrdemServico (ordem_servico_id, peca_id, quantidade) VALUES (?, ?, ?)",
                (ordem_servico_id, peca_id, quantidade),
            )
            logger.debug(f"Associada Peça ID {peca_id} (Qtd: {quantidade}) à OS ID {ordem_servico_id}.")

        conn.commit()
        logger.info(f"Ordem de serviço {ordem_servico_id} e suas peças inseridas com sucesso!")
        return ordem_servico_id

    except sqlite3.Error as e:
        logger.error(f"Erro ao inserir ordem de serviço: {e}", exc_info=True)
        conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def inserir_movimentacao_peca(peca_id: int, tipo_movimentacao: str, quantidade: int, ordem_servico_id: int | None):
    """Insere uma nova movimentação de peça no banco de dados."""
    logger.info(f"Registrando movimentação de estoque: Peça ID {peca_id}, Tipo: {tipo_movimentacao}, Qtd: {quantidade}")
    try:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO movimentacao_pecas (peca_id, data_movimentacao, tipo_movimentacao, quantidade, ordem_servico_id) VALUES (?, ?, ?, ?, ?)",
                (peca_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tipo_movimentacao, quantidade, ordem_servico_id),
            )
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Erro ao inserir movimentação de peça: {e}", exc_info=True)
        raise