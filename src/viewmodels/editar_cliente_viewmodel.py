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
import flet as ft
import logging
from typing import List
from src.models.models import Cliente, Carro
from src.database.database import get_db_connection, NOME_BANCO_DE_DADOS

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
        self.conexao = get_db_connection()
        # Estado: armazena o cliente que está a ser editado no momento.
        self.cliente_em_edicao: Cliente | None = None
        # Referência à View que este ViewModel controla.
        self._view: 'EditarClienteView' | None = None

    def vincular_view(self, view: 'EditarClienteView'):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view

    # --- MÉTODOS DE LÓGICA DE NEGÓCIO ---

    def pesquisar_cliente(self, termo: str):
        """Busca clientes na base de dados e comanda a View para exibir os resultados."""
        logging.info(f"ViewModel: a pesquisar por '{termo}'")
        clientes_encontrados = self._obter_clientes_por_termo(termo)
        # Comanda a View para atualizar a sua lista de resultados.
        if self._view:
            self._view.atualizar_lista_resultados(clientes_encontrados)

    def _obter_clientes_por_termo(self, termo: str) -> List[Cliente]:
        """Busca clientes na base de dados. Retorna uma lista de objetos `Cliente`."""
        with self.conexao:
            cursor = self.conexao.cursor()
            cursor.execute(
                """
                SELECT DISTINCT c.id, c.nome, c.telefone, c.endereco, c.email
                FROM clientes c LEFT JOIN carros car ON c.id = car.cliente_id
                WHERE c.nome LIKE ? OR c.telefone LIKE ? OR car.placa LIKE ?
                """,
                (f"%{termo}%", f"%{termo}%", f"%{termo}%")
            )
            return [Cliente(**row) for row in cursor.fetchall()]

    def selecionar_cliente_para_edicao(self, cliente: Cliente):
        """Prepara o estado para a edição de um cliente específico."""
        logging.info(f"ViewModel: selecionado cliente '{cliente.nome}' para edição.")
        self.cliente_em_edicao = cliente
        carros_do_cliente = self._obter_carros_por_cliente_id(cliente.id)
        # Comanda a View para abrir o modal de edição e o preenche com os dados.
        if self._view:
            self._view.abrir_modal_edicao(cliente, carros_do_cliente)

    def _obter_carros_por_cliente_id(self, cliente_id: int) -> List[Carro]:
        """Busca os carros de um cliente pelo ID. Retorna uma lista de objetos `Carro`."""
        with self.conexao:
            cursor = self.conexao.cursor()
            cursor.execute("SELECT id, modelo, ano, cor, placa, cliente_id FROM carros WHERE cliente_id = ?", (cliente_id,))
            return [Carro(**row) for row in cursor.fetchall()]

    def salvar_alteracoes(self, novos_dados: dict):
        """Salva as alterações do cliente na base de dados."""
        if not self.cliente_em_edicao:
            logging.warning("ViewModel: Tentativa de salvar sem um cliente em modo de edição.")
            return

        cliente_id = self.cliente_em_edicao.id
        logging.info(f"ViewModel: Salvando alterações para o cliente ID: {cliente_id}")
        try:
            with self.conexao:
                cursor = self.conexao.cursor()
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
            if self._view:
                self._view.fechar_todos_os_modais()
                self._view.mostrar_feedback("Cliente atualizado com sucesso!", success=True)
        except Exception as ex:
            logging.error(f"ViewModel: Erro ao salvar edição do cliente ID {cliente_id}: {ex}")
            if self._view:
                self._view.mostrar_feedback(f"Erro ao salvar: {ex}", success=False)
        finally:
            self.cliente_em_edicao = None

