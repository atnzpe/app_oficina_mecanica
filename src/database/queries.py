# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE CONSULTAS AO BANCO DE DADOS (queries.py)
#
# OBJETIVO: Centralizar TODAS as interações de leitura e escrita com o banco de
#           dados. Este arquivo é a única "porta" para a base de dados,
#           implementando o Padrão Repositório.
#
# ATUALIZAÇÃO:
#   - A função `buscar_clientes_por_termo` foi modificada para retornar
#     TODOS os clientes (ativos e inativos) que correspondem ao termo,
#     incluindo a coluna 'ativo' no resultado.
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
from src.models.models import Usuario, Cliente, Carro, Peca, Estabelecimento, Mecanico, Servico

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
        logger.error(
            f"Erro ao verificar a existência de usuário: {e}", exc_info=True)
        return True


def buscar_usuario_por_nome(nome_usuario: str) -> Usuario | None:
    """Busca um usuário pelo seu nome de login."""
    logger.debug(f"Buscando usuário pelo nome: {nome_usuario}")
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM usuarios WHERE nome = ?", (nome_usuario,))
            dados_usuario = cursor.fetchone()
            # Se encontrar, converte a linha do banco (que se comporta como dicionário)
            # em um objeto do tipo Usuario.
            return Usuario(**dados_usuario) if dados_usuario else None
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar usuário por nome: {e}", exc_info=True)
        return None


def criar_usuario(nome: str, senha_hash: str, perfil: str):
    """Insere um novo usuário no banco de dados."""
    logger.info(
        f"Executando query para criar usuário '{nome}' com perfil '{perfil}'.")
    try:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO usuarios (nome, senha, perfil) VALUES (?, ?, ?)",
                (nome, senha_hash, perfil),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        logger.warning(
            f"Tentativa de criar usuário com nome que já existe: '{nome}'.")
        raise
    except sqlite3.Error as e:
        logger.error(f"Erro ao criar usuário: {e}", exc_info=True)
        raise


def atualizar_senha_usuario(usuario_id: int, nova_senha_hash: str) -> bool:
    """Atualiza a senha de um usuário específico no banco de dados."""
    logger.info(
        f"Executando query para atualizar a senha do usuário ID: {usuario_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE usuarios SET senha = ? WHERE id = ?",
                (nova_senha_hash, usuario_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao atualizar senha do usuário ID {usuario_id}: {e}", exc_info=True)
        return False


def registrar_log_auditoria(usuario_id: int, acao: str, detalhes: str = ""):
    """Registra um evento de auditoria no banco de dados."""
    logger.info(
        f"Registrando log de auditoria para o usuário ID {usuario_id}. Ação: {acao}")
    sql = "INSERT INTO auditoria_logs (usuario_id, acao, detalhes, data_hora) VALUES (?, ?, ?, ?)"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(sql, (usuario_id, acao, detalhes, data_hora_atual))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Erro ao registrar log de auditoria: {e}", exc_info=True)


def has_establishment(user_id: int) -> bool:
    """
    Verifica se um usuário já está vinculado a um estabelecimento.
    """
    logger.debug(
        f"Verificando se o usuário ID {user_id} possui estabelecimento.")
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
        logger.error(
            f"Erro ao verificar estabelecimento para o usuário {user_id}: {e}", exc_info=True)
        # Retorna True em caso de erro para não bloquear o usuário.
        return True


def complete_onboarding(user_id: int, user_name: str, establishment_name: str):
    """
    Salva os dados do onboarding.
    1. Cria o novo estabelecimento.
    2. Vincula o ID do novo estabelecimento ao usuário.
    3. Atualiza o nome do usuário.
    """
    logger.info(
        f"Iniciando transação de onboarding para o usuário ID {user_id}.")
    # Abre a conexão manualmente para controlar a transação.
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        # 1. Cria o novo estabelecimento.
        cursor.execute(
            "INSERT INTO estabelecimentos (nome) VALUES (?)", (establishment_name,))
        establishment_id = cursor.lastrowid
        logger.debug(
            f"Estabelecimento '{establishment_name}' criado com ID: {establishment_id}.")

        # 2. Vincula o estabelecimento ao usuário e atualiza o nome.
        cursor.execute(
            "UPDATE usuarios SET nome = ?, id_estabelecimento = ? WHERE id = ?",
            (user_name, establishment_id, user_id)
        )
        logger.debug(
            f"Usuário ID {user_id} vinculado ao estabelecimento ID {establishment_id}.")

        # Confirma todas as operações.
        conn.commit()
        logger.info(
            f"Onboarding concluído com sucesso para o usuário '{user_name}'.")
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao salvar dados do onboarding. A transação será revertida (rollback): {e}", exc_info=True)
        conn.rollback()
        # Re-levanta a exceção para o ViewModel saber que algo deu errado.
        raise
    finally:
        if conn:
            conn.close()

# =================================================================================
# QUERIES DE MECÂNICOS (NOVO)
# =================================================================================


def criar_mecanico(nome: str, cpf: str, endereco: str, telefone: str, especialidade: str) -> Mecanico | None:
    """Insere um novo mecânico no banco de dados."""
    logger.info(f"Executando query para criar mecânico: {nome}")
    sql = "INSERT INTO mecanicos (nome, cpf, endereco, telefone, especialidade) VALUES (?, ?, ?, ?, ?)"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (nome, cpf, endereco, telefone, especialidade))
            novo_id = cursor.lastrowid
            conn.commit()
            logger.info(
                f"Mecânico '{nome}' criado com sucesso com o ID: {novo_id}.")
            return Mecanico(id=novo_id, nome=nome, cpf=cpf, endereco=endereco, telefone=telefone, especialidade=especialidade, ativo=True)
    except sqlite3.Error:
        logger.error(f"Erro ao criar mecânico '{nome}'.", exc_info=True)
        raise


def buscar_mecanicos_por_termo(termo: str) -> List[Mecanico]:
    # (Esta função não precisa de alteração, pois busca em todas as colunas de texto relevantes)
    logger.debug(f"Executando busca de mecânicos pelo termo: '{termo}'")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT * FROM mecanicos
                WHERE nome LIKE ? OR cpf LIKE ? OR especialidade LIKE ?
                ORDER BY nome
            """
            like_termo = f"%{termo}%"
            cursor.execute(query, (like_termo, like_termo, like_termo))
            return [Mecanico(**row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar mecânicos por termo: {e}", exc_info=True)
        return []


def obter_mecanico_por_id(mecanico_id: int) -> Mecanico | None:
    # (Esta função não precisa de alteração)
    logger.debug(f"Buscando mecânico pelo ID: {mecanico_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            result = cursor.execute(
                "SELECT * FROM mecanicos WHERE id = ?", (mecanico_id,)).fetchone()
            return Mecanico(**result) if result else None
    except Exception as e:
        logging.error(
            f"Erro ao obter mecânico por ID {mecanico_id}: {e}", exc_info=True)
        return None


def atualizar_mecanico(mecanico_id: int, nome: str, cpf: str, endereco: str, telefone: str, especialidade: str) -> bool:
    """Atualiza os dados de um mecânico específico."""
    logger.info(f"Executando query para atualizar mecânico ID: {mecanico_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE mecanicos SET nome = ?, cpf = ?, endereco = ?, telefone = ?, especialidade = ? WHERE id = ?",
                (nome, cpf, endereco, telefone, especialidade, mecanico_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error:
        logger.error(
            f"Erro ao atualizar mecânico ID {mecanico_id}:", exc_info=True)
        raise


def desativar_mecanico_por_id(mecanico_id: int) -> bool:
    """Realiza a exclusão lógica de um mecânico."""
    logger.info(f"Executando query para desativar mecânico ID: {mecanico_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE mecanicos SET ativo = 0 WHERE id = ?", (mecanico_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao desativar mecânico ID {mecanico_id}: {e}", exc_info=True)
        return False


def ativar_mecanico_por_id(mecanico_id: int) -> bool:
    """Reativa um mecânico."""
    logger.info(f"Executando query para ATIVAR mecânico ID: {mecanico_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE mecanicos SET ativo = 1 WHERE id = ?", (mecanico_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao ativar mecânico ID {mecanico_id}: {e}", exc_info=True)
        return False

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
        logger.info(
            f"Cliente '{nome}' criado com sucesso com o ID: {novo_id}.")
        return Cliente(id=novo_id, nome=nome, telefone=telefone, endereco=endereco, email=email, ativo=True)


def verificar_existencia_cliente() -> bool:
    """Verifica se existe qualquer cliente ATIVO cadastrado."""
    logger.debug("Executando query para verificar se há clientes ativos.")
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM clientes WHERE ativo = 1 LIMIT 1")
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao verificar a existência de cliente: {e}", exc_info=True)
        return True


def obter_clientes() -> List[Cliente]:
    """Retorna uma lista de todos os clientes (ativos e inativos)."""
    logger.debug("Executando query para obter todos os clientes.")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # --- QUERY ATUALIZADA ---
            # Remove o filtro 'WHERE ativo = 1' para buscar todos.
            cursor.execute("SELECT * FROM clientes ORDER BY nome")
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
    """Busca clientes (ativos e inativos) no banco de dados por nome, telefone ou placa do carro."""
    logger.debug(f"Executando busca de clientes pelo termo: '{termo}'")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # --- QUERY ATUALIZADA ---
            # Remove a condição 'AND c.ativo = 1' para incluir clientes inativos na busca.
            # Adiciona a coluna 'c.ativo' ao SELECT para que a View possa usá-la.
            query = """
                SELECT DISTINCT c.id, c.nome, c.telefone, c.endereco, c.email, c.ativo
                FROM clientes c LEFT JOIN carros car ON c.id = car.cliente_id
                WHERE (c.nome LIKE ? OR c.telefone LIKE ? OR car.placa LIKE ?)
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
        logger.error(
            f"Erro ao atualizar cliente ID {cliente_id}: {e}", exc_info=True)
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
            cursor.execute(
                "UPDATE clientes SET ativo = 0 WHERE id = ?", (cliente_id,))
            conn.commit()
            # Retorna True se a operação afetou pelo menos uma linha.
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao desativar cliente ID {cliente_id}: {e}", exc_info=True)
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
            cursor.execute(
                "UPDATE clientes SET ativo = 1 WHERE id = ?", (cliente_id,))
            conn.commit()
            # Retorna True se a operação afetou pelo menos uma linha.
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao ativar cliente ID {cliente_id}: {e}", exc_info=True)
        return False

# --- FUNÇÕES DE CARRO ---


def criar_carro(modelo: str, ano: int, cor: str, placa: str, cliente_id: int) -> Carro | None:
    """Insere um novo carro no banco de dados. O carro é criado como 'ativo' por padrão."""
    logger.info(
        f"Executando query para criar carro: {modelo} - Placa: {placa}")
    sql = "INSERT INTO carros (modelo, ano, cor, placa, cliente_id) VALUES (?, ?, ?, ?, ?)"
    # A exceção de integridade (placa duplicada) será tratada no ViewModel.
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (modelo, ano, cor, placa, cliente_id))
        novo_id = cursor.lastrowid
        conn.commit()
        logger.info(
            f"Carro '{modelo}' com placa '{placa}' criado com sucesso com o ID: {novo_id}.")
        return Carro(id=novo_id, modelo=modelo, ano=ano, cor=cor, placa=placa, cliente_id=cliente_id, ativo=True)

# --- NOVAS FUNÇÕES ---


def obter_carro_por_id(carro_id: int) -> dict | None:
    """
    Busca um único carro pelo seu ID, juntando o nome do cliente.
    Retorna um dicionário para facilitar o uso no ViewModel.
    """
    logger.debug(f"Buscando carro e proprietário pelo ID do carro: {carro_id}")
    sql = """
        SELECT car.*, cli.nome as nome_cliente
        FROM carros car
        JOIN clientes cli ON car.cliente_id = cli.id
        WHERE car.id = ?
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            result = cursor.execute(sql, (carro_id,)).fetchone()
            return dict(result) if result else None
    except Exception as e:
        logging.error(
            f"Erro ao obter carro por ID {carro_id}: {e}", exc_info=True)
        return None


def buscar_carros_por_termo(termo: str) -> List[dict]:
    """
    Busca carros (ativos e inativos) por modelo, placa ou nome do proprietário.
    Retorna uma lista de dicionários com os dados do carro e do cliente.
    """
    logger.debug(f"Executando busca de carros pelo termo: '{termo}'")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT
                    car.id, car.modelo, car.placa, car.ativo,
                    cli.nome as nome_cliente
                FROM carros car
                JOIN clientes cli ON car.cliente_id = cli.id
                WHERE car.modelo LIKE ? OR car.placa LIKE ? OR cli.nome LIKE ?
                ORDER BY cli.nome, car.modelo
            """
            like_termo = f"%{termo}%"
            cursor.execute(query, (like_termo, like_termo, like_termo))
            # Retorna uma lista de dicionários para facilitar a manipulação na View/ViewModel
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar carros por termo: {e}", exc_info=True)
        return []


def atualizar_carro(carro_id: int, novos_dados: dict) -> bool:
    """Atualiza todos os dados de um carro específico no banco de dados."""
    logger.info(f"Executando query para atualizar carro ID: {carro_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE carros SET
                    modelo = ?, ano = ?, cor = ?, placa = ?, cliente_id = ?
                   WHERE id = ?""",
                (
                    novos_dados["modelo"],
                    novos_dados["ano"],
                    novos_dados["cor"],
                    novos_dados["placa"],
                    novos_dados["cliente_id"],
                    carro_id
                )
            )
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao atualizar carro ID {carro_id}: {e}", exc_info=True)
        # Levanta a exceção para ser tratada no ViewModel (ex: placa duplicada)
        raise


def desativar_carro_por_id(carro_id: int) -> bool:
    """Realiza a exclusão lógica de um carro, setando seu status para 'ativo = 0'."""
    logger.info(f"Executando query para desativar carro ID: {carro_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE carros SET ativo = 0 WHERE id = ?", (carro_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao desativar carro ID {carro_id}: {e}", exc_info=True)
        return False


def ativar_carro_por_id(carro_id: int) -> bool:
    """Reativa um carro que foi desativado, setando seu status para 'ativo = 1'."""
    logger.info(f"Executando query para ATIVAR carro ID: {carro_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE carros SET ativo = 1 WHERE id = ?", (carro_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Erro ao ativar carro ID {carro_id}: {e}", exc_info=True)
        return False

# =================================================================================
# QUERIES DE PEÇAS E ESTOQUE
# =================================================================================

# --- FUNÇÃO ATUALIZADA ---


def obter_pecas() -> List[Peca]:
    """Retorna uma lista de todas as peças (ativas e inativas)."""
    logger.debug("Executando query para obter todas as peças.")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # A query agora também busca peças inativas, ordenando por nome.
            cursor.execute("SELECT * FROM pecas ORDER BY nome")
            return [Peca(**row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Erro ao obter peças: {e}", exc_info=True)
        return []

# --- NOVAS FUNÇÕES ---


def criar_peca(dados: dict) -> Peca | None:
    """
    Insere uma nova peça no banco de dados. A peça é criada como 'ativa' por padrão.
    :param dados: Um dicionário contendo todos os campos da peça.
    :return: O objeto Peca recém-criado ou None em caso de falha.
    """
    logger.info(f"Executando query para criar a peça: {dados.get('nome')}")
    sql = """
        INSERT INTO pecas (
            nome, referencia, fabricante, descricao, preco_compra,
            preco_venda, quantidade_em_estoque
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                dados['nome'], dados['referencia'], dados['fabricante'],
                dados['descricao'], dados['preco_compra'], dados['preco_venda'],
                dados['quantidade_em_estoque']
            ))
            novo_id = cursor.lastrowid
            conn.commit()
            logger.info(
                f"Peça '{dados.get('nome')}' criada com sucesso com o ID: {novo_id}.")
            # Retorna uma instância do modelo Peca com os dados inseridos
            return Peca(id=novo_id, ativo=True, **dados)
    except sqlite3.Error as e:
        # A exceção (ex: UNIQUE constraint) será tratada no ViewModel
        logger.error(
            f"Erro ao criar a peça '{dados.get('nome')}': {e}", exc_info=True)
        raise


def buscar_pecas_por_termo(termo: str) -> List[Peca]:
    """
    Busca peças (ativas e inativas) no banco de dados por nome, referência ou fabricante.
    """
    logger.debug(f"Executando busca de peças pelo termo: '{termo}'")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT * FROM pecas
                WHERE nome LIKE ? OR referencia LIKE ? OR fabricante LIKE ?
                ORDER BY nome
            """
            like_termo = f"%{termo}%"
            cursor.execute(query, (like_termo, like_termo, like_termo))
            return [Peca(**row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar peças por termo: {e}", exc_info=True)
        return []


def obter_peca_por_id(peca_id: int) -> Peca | None:
    """
    Busca uma única peça pelo seu ID, independente de estar ativa ou não.
    """
    logger.debug(f"Buscando peça pelo ID: {peca_id}")
    sql = "SELECT * FROM pecas WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            result = cursor.execute(sql, (peca_id,)).fetchone()
            return Peca(**result) if result else None
    except Exception as e:
        logging.error(
            f"Erro ao obter peça por ID {peca_id}: {e}", exc_info=True)
        return None


def atualizar_peca(peca_id: int, novos_dados: dict) -> bool:
    """Atualiza todos os dados de uma peça específica no banco de dados."""
    logger.info(f"Executando query para atualizar peça ID: {peca_id}")
    sql = """
        UPDATE pecas SET
            nome = ?, referencia = ?, fabricante = ?, descricao = ?,
            preco_compra = ?, preco_venda = ?, quantidade_em_estoque = ?
        WHERE id = ?
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                novos_dados['nome'], novos_dados['referencia'], novos_dados['fabricante'],
                novos_dados['descricao'], novos_dados['preco_compra'], novos_dados['preco_venda'],
                novos_dados['quantidade_em_estoque'], peca_id
            ))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao atualizar peça ID {peca_id}: {e}", exc_info=True)
        raise


def desativar_peca_por_id(peca_id: int) -> bool:
    """Realiza a exclusão lógica de uma peça, setando seu status para 'ativo = 0'."""
    logger.info(f"Executando query para desativar peça ID: {peca_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pecas SET ativo = 0 WHERE id = ?", (peca_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao desativar peça ID {peca_id}: {e}", exc_info=True)
        return False


def ativar_peca_por_id(peca_id: int) -> bool:
    """Reativa uma peça que foi desativada, setando seu status para 'ativo = 1'."""
    logger.info(f"Executando query para ATIVAR peça ID: {peca_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pecas SET ativo = 1 WHERE id = ?", (peca_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Erro ao ativar peça ID {peca_id}: {e}", exc_info=True)
        return False


def quantidade_em_estoque_suficiente(peca_id: int, quantidade_necessaria: int) -> bool:
    """Verifica se a quantidade em estoque é suficiente para a peça."""
    logger.debug(
        f"Verificando estoque para peça {peca_id}. Necessário: {quantidade_necessaria}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT quantidade_em_estoque FROM pecas WHERE id = ?", (peca_id,))
            resultado = cursor.fetchone()

            if resultado is None:
                logger.warning(
                    f"Peça com ID {peca_id} não encontrada ao verificar estoque.")
                return False

            quantidade_em_estoque = resultado["quantidade_em_estoque"]
            return quantidade_em_estoque >= quantidade_necessaria
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao verificar a quantidade em estoque da peça {peca_id}: {e}", exc_info=True)
        return False

# =================================================================================
# QUERIES DE SERVIÇOS
# =================================================================================


def criar_servico(nome: str, descricao: str, valor: float, pecas_ids: list) -> Servico | None:
    """
    Insere um novo serviço e suas peças associadas em uma única transação.
    """
    logger.info(f"Iniciando transação para criar o serviço: {nome}")
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()

        # 1. Insere o serviço principal
        sql_servico = "INSERT INTO servicos (nome, descricao, valor) VALUES (?, ?, ?)"
        cursor.execute(sql_servico, (nome, descricao, valor))
        novo_id = cursor.lastrowid
        logger.debug(f"Serviço '{nome}' inserido com ID: {novo_id}.")

        # 2. Se houver peças selecionadas, insere na tabela de junção
        if pecas_ids:
            sql_pecas = "INSERT INTO servicos_pecas (servico_id, peca_id) VALUES (?, ?)"
            dados_juncao = [(novo_id, peca_id) for peca_id in pecas_ids]
            cursor.executemany(sql_pecas, dados_juncao)
            logger.debug(
                f"Associadas {len(dados_juncao)} peças ao serviço ID: {novo_id}.")

        conn.commit()
        logger.info(
            f"Serviço '{nome}' e suas associações de peças criados com sucesso.")
        return Servico(id=novo_id, nome=nome, descricao=descricao, valor=valor, ativo=True)

    except sqlite3.Error as e:
        logger.error(
            f"Erro ao criar serviço '{nome}'. Transação revertida.", exc_info=True)
        conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def buscar_servicos_por_termo(termo: str) -> List[Servico]:
    """Busca serviços (ativos e inativos) por nome ou descrição."""
    logger.debug(f"Executando busca de serviços pelo termo: '{termo}'")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM servicos WHERE nome LIKE ? OR descricao LIKE ? ORDER BY nome"
            like_termo = f"%{termo}%"
            cursor.execute(query, (like_termo, like_termo))
            return [Servico(**row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar serviços por termo: {e}", exc_info=True)
        return []


def obter_servico_por_id(servico_id: int) -> Servico | None:
    """Busca um único serviço pelo seu ID, incluindo as peças associadas."""
    logger.debug(f"Buscando serviço completo pelo ID: {servico_id}")
    servico = None
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Busca o serviço principal
            result_servico = cursor.execute(
                "SELECT * FROM servicos WHERE id = ?", (servico_id,)).fetchone()
            if not result_servico:
                return None

            servico = Servico(**result_servico)

            # Busca as peças associadas
            sql_pecas = """
                SELECT p.* FROM pecas p
                JOIN servicos_pecas sp ON p.id = sp.peca_id
                WHERE sp.servico_id = ?
            """
            result_pecas = cursor.execute(sql_pecas, (servico_id,)).fetchall()
            servico.pecas = [Peca(**row) for row in result_pecas]

            return servico
    except Exception as e:
        logging.error(
            f"Erro ao obter serviço completo por ID {servico_id}: {e}", exc_info=True)
        return None


def atualizar_servico(servico_id: int, nome: str, descricao: str, valor: float, pecas_ids: list) -> bool:
    """Atualiza os dados de um serviço e suas peças associadas em uma transação."""
    logger.info(
        f"Iniciando transação para atualizar o serviço ID: {servico_id}")
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        # 1. Atualiza a tabela principal de serviços
        cursor.execute(
            "UPDATE servicos SET nome = ?, descricao = ?, valor = ? WHERE id = ?",
            (nome, descricao, valor, servico_id)
        )
        logger.debug(f"Tabela 'servicos' para o ID {servico_id} atualizada.")

        # 2. Remove todas as associações de peças existentes para este serviço
        cursor.execute(
            "DELETE FROM servicos_pecas WHERE servico_id = ?", (servico_id,))
        logger.debug(
            f"Associações de peças antigas para o serviço ID {servico_id} removidas.")

        # 3. Se houver novas peças selecionadas, insere as novas associações
        if pecas_ids:
            sql_pecas = "INSERT INTO servicos_pecas (servico_id, peca_id) VALUES (?, ?)"
            dados_juncao = [(servico_id, peca_id) for peca_id in pecas_ids]
            cursor.executemany(sql_pecas, dados_juncao)
            logger.debug(
                f"{len(dados_juncao)} novas associações de peças inseridas para o serviço ID: {servico_id}.")

        conn.commit()
        logger.info(
            f"Serviço ID {servico_id} e suas associações atualizados com sucesso.")
        return True
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao atualizar serviço ID {servico_id}. Transação revertida.", exc_info=True)
        conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def desativar_servico_por_id(servico_id: int) -> bool:
    """Realiza a exclusão lógica de um serviço."""
    logger.info(f"Executando query para desativar serviço ID: {servico_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE servicos SET ativo = 0 WHERE id = ?", (servico_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao desativar serviço ID {servico_id}: {e}", exc_info=True)
        return False


def ativar_servico_por_id(servico_id: int) -> bool:
    """Reativa um serviço."""
    logger.info(f"Executando query para ATIVAR serviço ID: {servico_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE servicos SET ativo = 1 WHERE id = ?", (servico_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao ativar serviço ID {servico_id}: {e}", exc_info=True)
        return False

# =================================================================================
# QUERIES DE ORDEM DE SERVIÇO E MOVIMENTAÇÕES
# =================================================================================


def inserir_ordem_servico(cliente_id: int, carro_id: int, pecas_quantidades: dict, valor_total: float, mao_de_obra: float) -> int | None:
    """
    Insere uma nova ordem de serviço e suas peças associadas no banco de dados.
    Esta função executa como uma transação: ou tudo é salvo, ou nada é.
    """
    logger.info(
        f"Iniciando transação para inserir nova Ordem de Serviço para o cliente {cliente_id}.")
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ordem_servico (cliente_id, carro_id, data_criacao, valor_total, mao_de_obra) VALUES (?, ?, ?, ?, ?)",
            (cliente_id, carro_id, datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"), valor_total, mao_de_obra),
        )
        ordem_servico_id = cursor.lastrowid
        logger.debug(
            f"Ordem de Serviço principal criada com ID: {ordem_servico_id}.")

        for peca_id, quantidade in pecas_quantidades.items():
            cursor.execute(
                "INSERT INTO PecasOrdemServico (ordem_servico_id, peca_id, quantidade) VALUES (?, ?, ?)",
                (ordem_servico_id, peca_id, quantidade),
            )
            logger.debug(
                f"Associada Peça ID {peca_id} (Qtd: {quantidade}) à OS ID {ordem_servico_id}.")

        conn.commit()
        logger.info(
            f"Ordem de serviço {ordem_servico_id} e suas peças inseridas com sucesso!")
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
    logger.info(
        f"Registrando movimentação de estoque: Peça ID {peca_id}, Tipo: {tipo_movimentacao}, Qtd: {quantidade}")
    try:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO movimentacao_pecas (peca_id, data_movimentacao, tipo_movimentacao, quantidade, ordem_servico_id) VALUES (?, ?, ?, ?, ?)",
                (peca_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 tipo_movimentacao, quantidade, ordem_servico_id),
            )
            conn.commit()
    except sqlite3.Error as e:
        logger.error(
            f"Erro ao inserir movimentação de peça: {e}", exc_info=True)
        raise
