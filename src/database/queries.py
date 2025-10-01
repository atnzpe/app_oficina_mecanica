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
from src.models.models import Usuario, Cliente, Carro, Peca, Estabelecimento

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
    Verifica se um usuário já está vinculado a um estabelecimento.
    """
    logger.debug(f"Verificando se o usuário ID {user_id} possui estabelecimento.")
    try:
        with get_db_connection() as conn:
            # A query agora verifica diretamente na tabela de usuários.
            cursor = conn.execute(
                "SELECT id_estabelecimento FROM usuarios WHERE id = ?",
                (user_id,)
            )
            user_data = cursor.fetchone()
            # Retorna True se o usuário foi encontrado e o campo id_estabelecimento não é nulo.
            return user_data is not None and user_data['id_estabelecimento'] is not None
    except sqlite3.Error as e:
        logger.error(f"Erro ao verificar estabelecimento para o usuário {user_id}: {e}", exc_info=True)
        # Retorna True em caso de erro para não bloquear o usuário.
        return True

def complete_onboarding(user_id: int, user_name: str, establishment_name: str):
    """
    Salva os dados do onboarding.
    1. Cria o novo estabelecimento.
    2. Vincula o ID do novo estabelecimento ao usuário.
    3. Atualiza o nome do usuário.
    """
    logger.info(f"Iniciando transação de onboarding para o usuário ID {user_id}.")
    # Abre a conexão manualmente para controlar a transação.
    conn = get_db_connection()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        
        # 1. Cria o novo estabelecimento.
        cursor.execute("INSERT INTO estabelecimentos (nome) VALUES (?)", (establishment_name,))
        establishment_id = cursor.lastrowid
        logger.debug(f"Estabelecimento '{establishment_name}' criado com ID: {establishment_id}.")
        
        # 2. Vincula o estabelecimento ao usuário e atualiza o nome.
        cursor.execute(
            "UPDATE usuarios SET nome = ?, id_estabelecimento = ? WHERE id = ?",
            (user_name, establishment_id, user_id)
        )
        logger.debug(f"Usuário ID {user_id} vinculado ao estabelecimento ID {establishment_id}.")
        
        # Confirma todas as operações.
        conn.commit()
        logger.info(f"Onboarding concluído com sucesso para o usuário '{user_name}'.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao salvar dados do onboarding. A transação será revertida (rollback): {e}", exc_info=True)
        conn.rollback()
        raise # Re-levanta a exceção para o ViewModel saber que algo deu errado.
    finally:
        if conn:
            conn.close()

# =================================================================================
# QUERIES DE CLIENTES E CARROS
# =================================================================================


# --- FUNÇÕES DE CLIENTE ---
def criar_cliente(nome: str, telefone: str, endereco: str, email: str) -> Cliente | None:
    """
    Insere um novo cliente no banco de dados. O cliente é criado como 'ativo' por padrão.
    """
    logger.info(f"Executando query para criar cliente: {nome}")
    
    sql = "INSERT INTO clientes (nome, telefone, endereco, email) VALUES (?, ?, ?, ?)"
    # O bloco `try...except` foi movido para o ViewModel para um tratamento de erro mais específico.
    # A camada de queries agora apenas executa a operação e permite que a exceção suba.
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (nome, telefone, endereco, email))
        novo_id = cursor.lastrowid
        conn.commit()
        logger.info(f"Cliente '{nome}' criado com sucesso com o ID: {novo_id}.")
        return Cliente(id=novo_id, nome=nome, telefone=telefone, endereco=endereco, email=email, ativo=True)

def verificar_existencia_cliente() -> bool:
    """Verifica se existe qualquer cliente ATIVO cadastrado."""
    logger.debug("Executando query para verificar se há clientes ativos.")
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT 1 FROM clientes WHERE ativo = 1 LIMIT 1")
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Erro ao verificar a existência de cliente: {e}", exc_info=True)
        return True

def obter_clientes() -> List[Cliente]:
    """Retorna uma lista de todos os clientes ATIVOS."""
    logger.debug("Executando query para obter todos os clientes ativos.")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # --- QUERY ATUALIZADA ---
            # Filtra para retornar apenas clientes com 'ativo = 1'.
            cursor.execute("SELECT * FROM clientes WHERE ativo = 1 ORDER BY nome")
            return [Cliente(**row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Erro ao obter clientes: {e}", exc_info=True)
        return []

def obter_cliente_por_id(cliente_id: int) -> Cliente | None:
    """
    Busca um único cliente pelo seu ID, independente de estar ativo ou não.
    """
    logger.debug(f"Buscando cliente pelo ID: {cliente_id}")
    sql = "SELECT * FROM clientes WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            result = cursor.execute(sql, (cliente_id,)).fetchone()
            # Converte o resultado (que é uma linha de banco de dados) em um objeto Cliente.
            return Cliente(**result) if result else None
    except Exception as e:
        logging.error(f"Erro ao obter cliente por ID {cliente_id}: {e}")
        return None

def buscar_clientes_por_termo(termo: str) -> List[Cliente]:
    """Busca clientes ATIVOS no banco de dados por nome, telefone ou placa do carro."""
    logger.debug(f"Executando busca de clientes ativos pelo termo: '{termo}'")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # --- QUERY ATUALIZADA ---
            # Adicionada a condição 'c.ativo = 1' para filtrar a busca.
            query = """
                SELECT DISTINCT c.id, c.nome, c.telefone, c.endereco, c.email
                FROM clientes c LEFT JOIN carros car ON c.id = car.cliente_id
                WHERE (c.nome LIKE ? OR c.telefone LIKE ? OR car.placa LIKE ?) AND c.ativo = 1
            """
            like_termo = f"%{termo}%"
            cursor.execute(query, (like_termo, like_termo, like_termo))
            return [Cliente(**row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar clientes por termo: {e}", exc_info=True)
        return []

def atualizar_cliente(cliente_id: int, novos_dados: dict) -> bool:
    """
    Atualiza os dados de um cliente específico no banco de dados.
    """
    logger.info(f"Executando query para atualizar cliente ID: {cliente_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes SET nome = ?, telefone = ?, endereco = ?, email = ? WHERE id = ?",
                (
                    novos_dados["nome"],
                    novos_dados["telefone"],
                    novos_dados["endereco"],
                    novos_dados["email"],
                    cliente_id
                )
            )
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Erro ao atualizar cliente ID {cliente_id}: {e}", exc_info=True)
        return False


def desativar_cliente_por_id(cliente_id: int) -> bool:
    """
    Realiza a exclusão lógica de um cliente, setando seu status para 'ativo = 0'.
    
    :param cliente_id: O ID do cliente a ser desativado.
    :return: True se a operação foi bem-sucedida, False caso contrário.
    """
    logger.info(f"Executando query para desativar cliente ID: {cliente_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Executa o UPDATE para marcar o cliente como inativo.
            cursor.execute("UPDATE clientes SET ativo = 0 WHERE id = ?", (cliente_id,))
            conn.commit()
            # Retorna True se a operação afetou pelo menos uma linha.
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Erro ao desativar cliente ID {cliente_id}: {e}", exc_info=True)
        return False

def ativar_cliente_por_id(cliente_id: int) -> bool:
    """
    Reativa um cliente que foi desativado, setando seu status para 'ativo = 1'.
    
    :param cliente_id: O ID do cliente a ser ativado.
    :return: True se a operação foi bem-sucedida, False caso contrário.
    """
    logger.info(f"Executando query para ATIVAR cliente ID: {cliente_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Executa o UPDATE para marcar o cliente como ativo.
            cursor.execute("UPDATE clientes SET ativo = 1 WHERE id = ?", (cliente_id,))
            conn.commit()
            # Retorna True se a operação afetou pelo menos uma linha.
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Erro ao ativar cliente ID {cliente_id}: {e}", exc_info=True)
        return False

# --- FUNÇÕES DE CARRO ---
def criar_carro(modelo: str, ano: int, cor: str, placa: str, cliente_id: int) -> Carro | None:
    """Insere um novo carro no banco de dados."""
    logger.info(f"Executando query para criar carro: {modelo} - Placa: {placa}")
    sql = "INSERT INTO carros (modelo, ano, cor, placa, cliente_id) VALUES (?, ?, ?, ?, ?)"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (modelo, ano, cor, placa, cliente_id))
            novo_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Carro '{modelo}' com placa '{placa}' criado com sucesso com o ID: {novo_id}.")
            return Carro(id=novo_id, modelo=modelo, ano=ano, cor=cor, placa=placa, cliente_id=cliente_id)
    except sqlite3.Error as e:
        logger.error(f"Erro ao criar carro '{modelo}' com placa '{placa}': {e}", exc_info=True)
        return None

def obter_carros_por_cliente_id(cliente_id: int) -> List[Carro]:
    """Busca os carros de um cliente pelo ID. Retorna uma lista de objetos `Carro`."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, modelo, ano, cor, placa, cliente_id FROM carros WHERE cliente_id = ?",
            (cliente_id,),
        )
    return [Carro(**row) for row in cursor.fetchall()]

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