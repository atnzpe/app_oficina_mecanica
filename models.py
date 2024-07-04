from typing import Any

# Modelagem das classes para representação de dados no sistema.
class Oficina:
    def __init__(self):
        # Inicializa a classe Oficina, representando a oficina.
        pass  # Nenhum atributo adicional por enquanto


class Peca:
    # Inicializa a classe Peca, representando uma peça.
    def __init__(
        self,
        nome: str,
        referencia: str,
        fabricante: str,
        descricao: str,
        preco_compra: float,
        preco_venda: float,
        quantidade_em_estoque: int,
    ):
        # Define os atributos da peça.
        self.nome = nome
        self.referencia = referencia
        self.fabricante = fabricante
        self.descricao = descricao
        self.preco_compra = preco_compra
        self.preco_venda = preco_venda
        self.quantidade_em_estoque = quantidade_em_estoque


class Carro:
    def __init__(self, modelo, ano, cor, placa, cliente_id):
        # Inicializa a classe Carro, representando um carro.
        self.modelo = modelo
        self.ano = ano
        self.cor = cor
        self.placa = placa
        self.cliente_id = cliente_id

class Cliente:
    def __init__(self, id, nome, telefone, endereco, email):
        # Inicializa a classe Cliente, representando um cliente.
        self.id = id
        self.nome = nome
        self.telefone = telefone
        self.endereco = endereco
        self.email = email

class Usuario:
    def __init__(self, id, senha):
        # Inicializa a classe Usuario, representando um usuário.
        self.id = id
        self.senha = senha