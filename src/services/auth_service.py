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
        queries.criar_usuario(
            nome=name, senha_hash=password_hash, perfil=profile)
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
        logger.warning(
            f"Tentativa de login falhou: usuário '{username}' não encontrado.")
        return None

    stored_hash = user_data.senha

    if _verify_password(password, stored_hash):
        logger.info(f"Usuário '{username}' autenticado com sucesso.")
        return user_data
    else:
        logger.warning(
            f"Tentativa de login falhou: senha incorreta para o usuário '{username}'.")
        return None


def alterar_senha(usuario: Usuario, senha_atual: str, nova_senha: str) -> tuple[bool, str]:
    """
    Altera a senha de um usuário logado após verificar a senha atual.
    :param usuario: O objeto do usuário logado.
    :param senha_atual: A senha atual fornecida pelo usuário.
    :param nova_senha: A nova senha desejada.
    :return: Uma tupla (bool, str) indicando sucesso e uma mensagem.
    """
    logger.info(
        f"Tentativa de alteração de senha para o usuário: {usuario.nome}")

    # 1. Verifica se a senha atual está correta
    if not _verify_password(plain_password=senha_atual, hashed_password=usuario.senha):
        mensagem = "A senha atual está incorreta."
        logger.warning(
            f"Falha na alteração de senha para '{usuario.nome}': {mensagem}")
        return False, mensagem

    try:
        # 2. Gera o hash da nova senha
        nova_senha_hash = _hash_password(nova_senha)

        # 3. Atualiza a senha no banco de dados
        sucesso = queries.atualizar_senha_usuario(usuario.id, nova_senha_hash)

        if sucesso:
            # 4. Registra o log de auditoria
            queries.registrar_log_auditoria(usuario.id, "ALTERACAO_SENHA")
            mensagem = "Senha alterada com sucesso!"
            logger.info(
                f"Senha do usuário '{usuario.nome}' alterada com sucesso.")
            return True, mensagem
        else:
            mensagem = "Ocorreu um erro ao atualizar a senha no banco de dados."
            logger.error(mensagem)
            return False, mensagem

    except Exception as e:
        mensagem = "Ocorreu uma falha inesperada durante a alteração da senha."
        logger.error(f"{mensagem} Erro: {e}", exc_info=True)
        return False, mensagem
