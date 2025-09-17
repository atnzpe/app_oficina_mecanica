# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE CONSULTAS AO BANCO DE DADOS (queries.py)
#
# OBJETIVO: Centralizar todas as interações com o banco de dados.
#
# ATUALIZAÇÃO: Adicionadas as funções `has_establishment` e `complete_onboarding`
#             para suportar o novo fluxo de configuração inicial do usuário.
#             As tabelas foram adaptadas para o contexto da Oficina.
# =================================================================================

import logging
import sqlite3
from src.database.database import criar_conexao_banco_de_dados, NOME_BANCO_DE_DADOS
from src.models.models import Usuario

logger = logging.getLogger("DB_QUERIES")

# --- QUERIES DE USUÁRIO E ONBOARDING ---

def verificar_existencia_usuario() -> bool:
    # ... (função existente, sem alterações)
    logger.debug("Executando query para verificar se há usuários.")
    try:
        with criar_conexao_banco_de_dados(NOME_BANCO_DE_DADOS) as conn:
            cursor = conn.execute("SELECT 1 FROM usuarios LIMIT 1")
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Erro ao verificar a existência de usuário: {e}", exc_info=True)
        return True

def buscar_usuario_por_nome(nome_usuario: str) -> Usuario | None:
    # ... (função existente, sem alterações)
    logger.debug(f"Buscando usuário pelo nome: {nome_usuario}")
    try:
        with criar_conexao_banco_de_dados(NOME_BANCO_DE_DADOS) as conn:
            cursor = conn.execute("SELECT * FROM usuarios WHERE nome = ?", (nome_usuario,))
            dados_usuario = cursor.fetchone()
            return Usuario(**dados_usuario) if dados_usuario else None
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar usuário por nome: {e}", exc_info=True)
        return None

def criar_usuario(nome: str, senha_hash: str, perfil: str):
    # ... (função existente, sem alterações)
    logger.info(f"Criando usuário '{nome}' com perfil '{perfil}'.")
    try:
        with criar_conexao_banco_de_dados(NOME_BANCO_DE_DADOS) as conn:
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

# --- NOVA FUNÇÃO ---
def has_establishment(user_id: int) -> bool:
    """
    Verifica se um usuário já possui um estabelecimento (oficina) cadastrado.
    Isso determina se ele precisa passar pelo onboarding.

    :param user_id: O ID do usuário a ser verificado.
    :return: True se o usuário já tem um estabelecimento, False caso contrário.
    """
    logger.debug(f"Verificando se o usuário ID {user_id} possui estabelecimento.")
    try:
        with criar_conexao_banco_de_dados(NOME_BANCO_DE_DADOS) as conn:
            # A tabela 'clientes' será usada como análoga a 'estabelecimentos'.
            # O primeiro cliente cadastrado pode ser a própria oficina.
            # Para uma lógica mais robusta, uma tabela 'oficinas' seria ideal.
            # Por simplicidade, vamos assumir que o cadastro de um primeiro cliente
            # representa a conclusão do onboarding.
            # NOTA: Uma futura melhoria seria criar uma tabela `oficinas`.
            cursor = conn.execute("SELECT 1 FROM clientes LIMIT 1") # Simplificação
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Erro ao verificar estabelecimento para o usuário {user_id}: {e}", exc_info=True)
        return False

# --- NOVA FUNÇÃO ---
def complete_onboarding(user_id: int, user_name: str, establishment_name: str):
    """
    Salva os dados do onboarding.
    - Atualiza o nome do usuário.
    - Cria o primeiro 'cliente' que representa a própria oficina.

    :param user_id: O ID do usuário que está completando o onboarding.
    :param user_name: O nome completo do usuário.
    :param establishment_name: O nome da oficina a ser cadastrada como primeiro cliente.
    """
    logger.info(f"Completando onboarding para o usuário ID {user_id}.")
    try:
        with criar_conexao_banco_de_dados(NOME_BANCO_DE_DADOS) as conn:
            cursor = conn.cursor()
            # Atualiza o nome do usuário na tabela de usuários.
            cursor.execute("UPDATE usuarios SET nome = ? WHERE id = ?", (user_name, user_id))
            # Insere a oficina como o primeiro cliente.
            cursor.execute(
                "INSERT INTO clientes (nome, telefone, endereco, email) VALUES (?, ?, ?, ?)",
                (establishment_name, "N/A", "N/A", "N/A"),
            )
            conn.commit()
            logger.info(f"Onboarding concluído. Usuário '{user_name}' e oficina '{establishment_name}' configurados.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao salvar dados do onboarding: {e}", exc_info=True)
        raise