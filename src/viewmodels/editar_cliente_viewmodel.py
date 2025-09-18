# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DO VIEWMODEL DE EDIÇÃO DE CLIENTE (editar_cliente_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio e o estado do componente de edição de
#           clientes. Ele busca dados, gere o estado do formulário e
#           comanda a View para se atualizar.
#
# SEÇÕES ALTERADAS NESTA REATORAÇÃO (ISSUE #1):
#   - Este é um ficheiro completamente novo, criado para separar a lógica
#     da apresentação, seguindo o padrão MVVM.
#
# SEÇÕES SEM ALTERAÇÃO:
#   - A lógica de base de dados (queries SQL) foi movida para aqui a partir do
#     antigo ficheiro `editar_cliente.py` sem alterações funcionais.
# =================================================================================
import logging
from typing import List
import flet as ft

from src.models.models import Cliente, Carro
from src.database import queries


class EditarClienteViewModel:
    """
    O ViewModel para a EditarClienteView. Contém o estado e a lógica da funcionalidade.
    """

    def __init__(self, page: ft.Page):
        """
        Construtor do ViewModel.
        :param page: A referência à página principal do Flet para controlo de modais.
        """
        self.page = page
        # Estabelece uma conexão com a base de dados.

        # Estado: armazena o cliente que está a ser editado no momento.
        self.cliente_em_edicao: Cliente | None = None
        # Referência à View que este ViewModel controla.
        self._view: "EditarClienteView" | None = None

    def vincular_view(self, view: "EditarClienteView"):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view

    # --- MÉTODOS DE LÓGICA DE NEGÓCIO ---

    

    def pesquisar_cliente(self, termo: str):
        """Busca clientes na base de dados e comanda a View para exibir os resultados."""
        logging.info(f"ViewModel: a pesquisar por %s'{termo}'")
        clientes_encontrados = queries.obter_clientes_por_termo(termo)
        # Comanda a View para atualizar a sua lista de resultados.
        if self._view:
            self._view.atualizar_lista_resultados(clientes_encontrados)

    

    def selecionar_cliente_para_edicao(self, cliente: Cliente):
        """Prepara o estado para a edição de um cliente específico."""
        logging.info(f"ViewModel: selecionado cliente '{cliente.nome}' para edição.")
        self.cliente_em_edicao = cliente
        carros_do_cliente = queries.obter_carros_por_cliente_id(cliente.id)
        # Comanda a View para abrir o modal de edição e o preenche com os dados.
        if self._view:
            self._view.abrir_modal_edicao(cliente, carros_do_cliente)

    

    def salvar_alteracoes(self, novos_dados: dict):
        """Salva as alterações do cliente no banco de dados."""
        if not self.cliente_em_edicao:
            logging.warning("ViewModel: Tentativa de salvar sem um cliente em modo de edição.")
            return

        cliente_id = self.cliente_em_edicao.id
        logging.info(f"ViewModel: Salvando alterações para o cliente ID: {cliente_id}")
        # --- CHAMADA CORRIGIDA (sem passar a conexão) ---
        sucesso = queries.atualizar_cliente(cliente_id, novos_dados)
        
        if self._view:
            self._view.fechar_todos_os_modais()
            if sucesso:
                self._view.mostrar_feedback("Cliente atualizado com sucesso!", success=True)
            else:
                self._view.mostrar_feedback("Erro ao salvar alterações.", success=False)
        
        self.cliente_em_edicao = None
