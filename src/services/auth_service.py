# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE SERVIÇO DE AUTENTICAÇÃO (auth_service.py)
#
# OBJETIVO: Isolar toda a lógica de negócio relacionada à autenticação de
#           utilizadores.
#
# SEÇÕES ALTERADAS NESTA REATORAÇÃO:
#   - A lógica foi encapsulada dentro de uma classe `AuthService` para alinhar
#     com a arquitetura de serviços e resolver o `ImportError`.
#   - A função `autenticar_usuario` foi convertida num método da classe.
# =================================================================================
import bcrypt
import sqlite3
from src.models.models import Usuario
from src.database.database import buscar_usuario_por_nome

class AuthService:
    """
    Classe de serviço responsável por toda a lógica de autenticação.
    """
    def __init__(self, conexao: sqlite3.Connection):
        """
        Construtor do serviço de autenticação.
        
        :param conexao: Uma conexão ativa com a base de dados.
        """
        self.conexao = conexao

    def autenticar_usuario(self, nome_usuario: str, senha: str) -> Usuario | None:
        """
        Verifica as credenciais de um utilizador contra a base de dados.

        :param nome_usuario: O nome do utilizador a ser autenticado.
        :param senha: A senha em texto plano a ser verificada.
        :return: Um objeto Usuario se a autenticação for bem-sucedida, caso contrário, None.
        """
        # Busca o utilizador na base de dados pelo nome.
        usuario = buscar_usuario_por_nome(self.conexao, nome_usuario)
        
        # Se o utilizador existir, verifica se a senha fornecida corresponde ao hash guardado.
        if usuario:
            # bcrypt.checkpw compara a senha em texto plano com o hash.
            if bcrypt.checkpw(senha.encode('utf-8'), usuario.senha.encode('utf-8')):
                return usuario
                
        # Retorna None se o utilizador não existir ou se a senha estiver incorreta.
        return None