# =================================================================================
# MÓDULO DO VIEWMODEL DE CADASTRO DE CARRO (cadastro_carro_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de cadastro de carros,
#           incluindo validação de formulário, carregamento de clientes e
#           interação com a camada de dados.
# =================================================================================
import flet as ft
import logging
import sqlite3
from src.database import queries
from typing import List
from src.models.models import Cliente

# Configura o logger para este módulo.
logger = logging.getLogger(__name__)

class CadastroCarroViewModel:
    """
    O ViewModel para a CadastroCarroView.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'CadastroCarroView' | None = None
        # Cache para a lista de clientes para evitar múltiplas buscas no DB.
        self.lista_clientes: List[Cliente] = []
        logger.debug("CadastroCarroViewModel inicializado.")

    def vincular_view(self, view: 'CadastroCarroView'):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view
        logger.debug("ViewModel de Cadastro de Carro vinculado à sua View.")

    def carregar_clientes(self):
        """Busca a lista de clientes ativos e comanda a View para popular o dropdown."""
        if not self._view: return
        logger.info("ViewModel: Carregando lista de clientes para o dropdown.")
        try:
            self.lista_clientes = queries.obter_clientes()
            self._view.popular_dropdown_clientes(self.lista_clientes)
        except Exception as e:
            logger.error(f"Erro ao carregar clientes: {e}", exc_info=True)
            self._view.mostrar_dialogo_feedback("Erro Crítico", f"Não foi possível carregar a lista de clientes.\nErro: {e}")

    def salvar_carro(self, e):
        """
        Pega dados da View, valida, e comanda a criação do novo carro.
        """
        if not self._view:
            logger.error("ViewModel: Ação 'salvar_carro' chamada sem uma View vinculada.")
            return

        try:
            dados = self._view.obter_dados_formulario()
            placa = dados.get("placa", "").strip().upper()
            modelo = dados.get("modelo", "").strip()
            cliente_id = dados.get("cliente_id")

            # LÓGICA DE VALIDAÇÃO
            if not all([placa, modelo, cliente_id]):
                self._view.mostrar_dialogo_feedback("Erro de Validação", "Proprietário, Modelo e Placa são obrigatórios.")
                return

            # INTERAÇÃO COM A CAMADA DE DADOS
            logger.info(f"ViewModel: Tentando salvar o novo carro com placa '{placa}'.")
            novo_carro = queries.criar_carro(
                modelo=modelo,
                ano=int(dados.get("ano")) if dados.get("ano") else None,
                cor=dados.get("cor"),
                placa=placa,
                cliente_id=int(cliente_id)
            )

            # COMANDA A VIEW COM BASE NO RESULTADO
            if novo_carro:
                logger.info(f"Carro com placa '{placa}' cadastrado com sucesso.")
                acao_navegacao = lambda: self.page.go("/gerir_carros")
                self._view.mostrar_dialogo_feedback("Sucesso!", "Carro cadastrado com sucesso!", acao_navegacao)

        except sqlite3.IntegrityError:
            logger.warning(f"Tentativa de cadastrar carro com placa duplicada: {placa}")
            self._view.mostrar_dialogo_feedback("Placa Duplicada", f"Já existe um carro cadastrado com a placa '{placa}'.")

        except Exception as e:
            logger.error(f"Erro inesperado ao salvar carro: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback("Erro Crítico", f"Ocorreu uma falha inesperada:\n{e}")

    def cancelar_cadastro(self, e):
        """Navega de volta para a lista de carros."""
        logger.info("Cadastro de carro cancelado. Redirecionando para /gerir_carros.")
        self.page.go("/gerir_carros")