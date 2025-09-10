# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE MODELOS DE DADOS (models.py)
#
# OBJETIVO: Centralizar a definição das estruturas de dados (entidades de negócio)
# da aplicação. Cada classe representa uma tabela ou um conceito do domínio da oficina.
# Usar classes em vez de tuplas ou dicionários torna o código mais legível,
# seguro (graças ao autocompletar da IDE) e fácil de manter.
# =================================================================================
from typing import Optional


class Usuario:
    """Representa um usuário do sistema."""

    def __init__(self, id: int, nome: str, senha: str):
        self.id: int = id
        self.nome: str = nome
        self.senha: str = senha


class Cliente:
    """Representa um cliente da oficina."""

    def __init__(self, id: int, nome: str, telefone: str, endereco: str, email: str):
        self.id: int = id
        self.nome: str = nome
        self.telefone: str = telefone
        self.endereco: str = endereco
        self.email: str = email


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
