# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE SERVIÇO DE AUTENTICAÇÃO (auth_service.py)
#
# OBJETIVO: Isolar toda a lógica de negócio relacionada à autenticação.
#           Este módulo lida com hashing de senhas e orquestra o registro
#           e a autenticação de usuários, usando o módulo de queries.
# =================================================================================
import sqlite3
import bcrypt
import logging
from src.database import queries  # Importa o módulo de queries.
from src.models.models import Usuario

# Configura o logger para este módulo.
logger = logging.getLogger(__name__)

def _hash_password(password: str) -> str:
    """
    Gera um hash seguro para uma senha usando bcrypt.

    :param password: A senha em texto plano.
    :return: A string do hash da senha.
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha em texto plano corresponde a um hash bcrypt.

    :param plain_password: A senha fornecida pelo usuário.
    :param hashed_password: O hash armazenado no banco de dados.
    :return: True se a senha corresponder, False caso contrário.
    """
    try:
        plain_password_bytes = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
    except (ValueError, TypeError) as e:
        logger.error(f"Erro ao verificar a senha (hash malformado?): {e}")
        return False

def register_user(name: str, password: str, profile: str) -> tuple[bool, str]:
    """
    Registra um novo usuário no sistema.

    :param name: Nome de usuário (login/e-mail).
    :param password: Senha em texto plano.
    :param profile: Perfil do usuário ('admin' ou 'mecanico').
    :return: Uma tupla (bool, str) indicando sucesso e uma mensagem.
    """
    logger.info(f"Tentativa de registro para o usuário: {name}")
    try:
        password_hash = _hash_password(password)
        queries.criar_usuario(nome=name, senha_hash=password_hash, perfil=profile)
        message = "Usuário cadastrado com sucesso!"
        logger.info(message)
        return True, message
    except sqlite3.IntegrityError:
        message = "Este nome de usuário já está cadastrado."
        logger.warning(message)
        return False, message
    except Exception as e:
        message = "Ocorreu um erro inesperado durante o cadastro."
        logger.error(f"{message} Erro: {e}", exc_info=True)
        return False, message

def authenticate_user(username: str, password: str) -> Usuario | None:
    """
    Autentica um usuário com base no nome de usuário e senha.

    :param username: O nome de usuário.
    :param password: A senha em texto plano.
    :return: O objeto Usuario se a autenticação for bem-sucedida, senão None.
    """
    if not username or not password:
        logger.warning("Tentativa de login com usuário ou senha vazios.")
        return None

    user_data = queries.buscar_usuario_por_nome(username)

    if user_data is None:
        logger.warning(f"Tentativa de login falhou: usuário '{username}' não encontrado.")
        return None

    stored_hash = user_data.senha

    if _verify_password(password, stored_hash):
        logger.info(f"Usuário '{username}' autenticado com sucesso.")
        return user_data
    else:
        logger.warning(f"Tentativa de login falhou: senha incorreta para o usuário '{username}'.")
        return None