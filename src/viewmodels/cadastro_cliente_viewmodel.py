# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DO VIEWMODEL DE CADASTRO DE CLIENTE (cadastro_cliente_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio e o estado do formulário de cadastro
#           de novos clientes.
# =================================================================================
import flet as ft
import logging
from src.database import queries

logger = logging.getLogger(__name__)

class CadastroClienteViewModel:
    """
    O ViewModel para a CadastroClienteView.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'CadastroClienteView' | None = None

    def vincular_view(self, view: 'CadastroClienteView'):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view

    def salvar_cliente(self, e):
        """
        Pega os dados da View, valida e comanda a inserção no banco de dados.
        """
        if not self._view:
            return

        dados = self._view.obter_dados_formulario()
        nome = dados["nome"]
        
        if not nome:
            logger.warning("Tentativa de salvar cliente sem nome.")
            self._view.mostrar_feedback("O campo 'Nome' é obrigatório.", False)
            return

        logger.info(f"ViewModel: Tentando salvar o novo cliente '{nome}'.")
        novo_cliente = queries.criar_cliente(
            nome=nome,
            telefone=dados["telefone"],
            endereco=dados["endereco"],
            email=dados["email"]
        )

        if novo_cliente:
            self._view.fechar_modal()
            self._view.mostrar_feedback(f"Cliente '{novo_cliente.nome}' cadastrado com sucesso!", True)
        else:
            self._view.mostrar_feedback("Ocorreu um erro ao cadastrar o cliente.", False)
