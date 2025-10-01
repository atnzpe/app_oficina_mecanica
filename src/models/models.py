# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE MODELOS DE DADOS (models.py)
#
# OBJETIVO: Centralizar a definição das estruturas de dados (entidades de negócio)
#           da aplicação.
#
# CORREÇÃO (BUG FIX):
#   - A classe `Usuario` foi atualizada para incluir o atributo `perfil` em
#     seu construtor (`__init__`). Isso alinha o modelo de dados com a
#     estrutura da tabela `usuarios` no banco de dados, resolvendo o
#     `TypeError`.
# =================================================================================
from typing import Optional

class Estabelecimento:
    """Representa um estabelecimento (oficina) no sistema."""
    def __init__(self, id: int, nome: str):
        self.id: int = id
        self.nome: str = nome

class Usuario:
    """Representa um usuário do sistema."""
    # --- CONSTRUTOR CORRIGIDO ---
    # Adicionado `id_estabelecimento: Optional[int]` para corresponder à tabela.
    def __init__(self, id: int, nome: str, senha: str, perfil: str, id_estabelecimento: Optional[int]):
        self.id: int = id
        self.nome: str = nome
        self.senha: str = senha
        self.perfil: str = perfil
        # Chave estrangeira que vincula o usuário a um estabelecimento.
        self.id_estabelecimento: Optional[int] = id_estabelecimento


class Cliente:
    """Representa um cliente da oficina."""

    # --- CONSTRUTOR ATUALIZADO ---
    # Adicionado o atributo `ativo`, que será usado para exclusão lógica.
    def __init__(self, id: int, nome: str, telefone: str, endereco: str, email: str, ativo: bool = True):
        # ID único do cliente no banco de dados.
        self.id: int = id
        # Nome completo do cliente.
        self.nome: str = nome
        # Número de telefone para contato.
        self.telefone: str = telefone
        # Endereço físico do cliente.
        self.endereco: str = endereco
        # Endereço de e-mail do cliente.
        self.email: str = email
        # Flag para indicar se o cliente está ativo (1) ou desativado (0).
        self.ativo: bool = ativo


class Carro:
    """Representa um veículo pertencente a um cliente."""

    def __init__(
        self,
        id: int,
        modelo: str,
        ano: Optional[int],
        cor: Optional[str],
        placa: str,
        cliente_id: int,
    ):
        self.id: int = id
        self.modelo: str = modelo
        self.ano: Optional[int] = ano
        self.cor: Optional[str] = cor
        self.placa: str = placa
        self.cliente_id: int = cliente_id


class Peca:
    """Representa uma peça ou item de estoque."""

    def __init__(
        self,
        id: int,
        nome: str,
        referencia: str,
        fabricante: Optional[str],
        descricao: Optional[str],
        preco_compra: float,
        preco_venda: float,
        quantidade_em_estoque: int,
    ):
        self.id: int = id
        self.nome: str = nome
        self.referencia: str = referencia
        self.fabricante: Optional[str] = fabricante
        self.descricao: Optional[str] = descricao
        self.preco_compra: float = preco_compra
        self.preco_venda: float = preco_venda
        self.quantidade_em_estoque: int = quantidade_em_estoque
