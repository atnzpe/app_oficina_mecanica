# =================================================================================
# MÓDULO DO VIEWMODEL DE EDIÇÃO DE CARRO (editar_carro_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de edição de carros,
#           incluindo carregamento de dados, validação, salvamento e
#           gerenciamento de feedback ao usuário.
# =================================================================================
import flet as ft
import logging
import sqlite3
from src.database import queries
from typing import Callable, Optional

# Configura o logger para este módulo.
logger = logging.getLogger(__name__)

class EditarCarroViewModel:
    def __init__(self, page: ft.Page, carro_id: int):
        self.page = page
        self.carro_id = carro_id
        self._view: 'EditarCarroView' | None = None
        # Armazena os dados do carro em edição, incluindo o nome do cliente.
        self.carro_em_edicao: dict | None = None
        logger.debug(f"ViewModel de Edição de Carro inicializado para o ID: {self.carro_id}")

    def vincular_view(self, view: 'EditarCarroView'):
        """Vincula a View ao ViewModel para comunicação."""
        self._view = view
        logger.debug("ViewModel de Edição de Carro vinculado à sua View.")

    def carregar_dados(self):
        """Busca os dados do carro e a lista de clientes para preencher o formulário."""
        if not self._view: return
        try:
            logger.info(f"ViewModel: buscando dados para o carro ID {self.carro_id}")
            carro = queries.obter_carro_por_id(self.carro_id)
            clientes = queries.obter_clientes() # Busca todos os clientes para o dropdown

            if carro:
                self.carro_em_edicao = carro
                self._view.popular_dropdown_clientes(clientes)
                self._view.preencher_formulario(carro)
                logger.info(f"ViewModel: Dados do carro placa '{carro['placa']}' carregados.")
            else:
                logger.warning(f"ViewModel: Carro com ID {self.carro_id} não encontrado.")
                acao_navegacao = lambda: self.page.go("/gerir_carros")
                self._view.mostrar_dialogo_feedback("Erro", "Carro não encontrado.", acao_navegacao)
        except Exception as e:
            logger.error(f"Erro crítico ao carregar dados do carro: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback("Erro Crítico", f"Não foi possível carregar os dados do carro.\nErro: {e}")

    def salvar_alteracoes(self):
        """Salva as alterações no banco de dados."""
        if not self._view: return

        try:
            novos_dados = self._view.obter_dados_formulario()
            placa = novos_dados.get("placa", "").strip().upper()
            modelo = novos_dados.get("modelo", "").strip()
            cliente_id = novos_dados.get("cliente_id")

            if not all([placa, modelo, cliente_id]):
                self._view.mostrar_dialogo_feedback("Erro de Validação", "Proprietário, Modelo e Placa são obrigatórios.")
                return

            logger.info(f"ViewModel: salvando alterações para o carro ID {self.carro_id}")
            sucesso = queries.atualizar_carro(self.carro_id, novos_dados)
            acao_navegacao = lambda: self.page.go("/gerir_carros")
            
            if sucesso:
                logger.info(f"ViewModel: Carro ID {self.carro_id} atualizado com sucesso.")
                self._view.mostrar_dialogo_feedback("Sucesso!", "Carro atualizado com sucesso!", acao_navegacao)
            else:
                # Isso pode ocorrer se nenhum dado foi realmente alterado.
                logger.warning(f"ViewModel: Nenhuma linha foi alterada para o carro ID {self.carro_id}.")
                self._view.mostrar_dialogo_feedback("Atenção", "Nenhuma alteração foi salva. Os dados podem ser os mesmos.")

        except sqlite3.IntegrityError:
            logger.warning(f"Tentativa de atualizar para uma placa duplicada: {placa}")
            self._view.mostrar_dialogo_feedback("Placa Duplicada", f"Já existe outro carro cadastrado com a placa '{placa}'.")
        except Exception as e:
            logger.error(f"Erro crítico ao salvar alterações do carro: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback("Erro Crítico", f"Não foi possível salvar as alterações.\nErro: {e}")