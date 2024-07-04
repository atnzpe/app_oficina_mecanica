import bcrypt

from database import buscar_usuario_por_nome

def autenticar_usuario(conexao, nome_usuario, senha):
    usuario = buscar_usuario_por_nome(conexao, nome_usuario)
    if usuario:
        if bcrypt.checkpw(senha.encode(), usuario.senha.encode()):
            return usuario
    return None

#versao1.0