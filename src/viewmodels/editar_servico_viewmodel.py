# =================================================================================
# MÓDULO DO VIEWMODEL DE EDIÇÃO DE SERVIÇO (editar_servico_viewmodel.py)
# =================================================================================
import flet as ft
import logging
import sqlite3
from src.database import queries
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class EditarServicoViewModel:
    def __init__(self, page: ft.Page, servico_id: int):
        self.page = page
        self.servico_id = servico_id
        self._view: 'EditarServicoView' | None = None
        logger.debug(
            f"ViewModel de Edição de Serviço inicializado para o ID: {self.servico_id}")

    def vincular_view(self, view: 'EditarServicoView'):
        """Vincula a View ao ViewModel."""
        self._view = view

    def carregar_dados_iniciais(self):
        """Busca os dados do serviço e a lista completa de peças."""
        if not self._view:
            return
        try:
            logger.info(
                f"ViewModel: buscando dados para o serviço ID {self.servico_id}")
            servico = queries.obter_servico_por_id(self.servico_id)
            todas_as_pecas = [p for p in queries.obter_pecas() if p.ativo]

            if servico:
                self._view.popular_lista_pecas(todas_as_pecas)
                self._view.preencher_formulario(servico)
                logger.info(
                    f"ViewModel: Dados do serviço '{servico.nome}' carregados.")
            else:
                logger.warning(
                    f"ViewModel: Serviço com ID {self.servico_id} não encontrado.")

                def acao_navegacao(): return self.page.go("/gerir_servicos")
                self._view.mostrar_dialogo_feedback(
                    "Erro", "Serviço não encontrado.", acao_navegacao)
        except Exception as e:
            logger.error(
                f"Erro crítico ao carregar dados do serviço: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Não foi possível carregar os dados.\nErro: {e}")

    def salvar_alteracoes(self):
        """Valida e salva as alterações no banco de dados."""
        if not self._view:
            return
        try:
            dados = self._view.obter_dados_formulario()
            nome = dados.get("nome", "").strip()
            valor = dados.get("valor")

            if not nome or valor is None:
                self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "Nome e Valor são obrigatórios.")
                return

            logger.info(
                f"ViewModel: salvando alterações para o serviço ID {self.servico_id}")
            sucesso = queries.atualizar_servico(
                self.servico_id,
                nome,
                dados.get("descricao", "").strip(),
                valor,
                dados.get("pecas_selecionadas", [])
            )
            def acao_navegacao(): return self.page.go("/gerir_servicos")

            if sucesso:
                self._view.mostrar_dialogo_feedback(
                    "Sucesso!", "Serviço atualizado com sucesso!", acao_navegacao)
            else:
                # Na prática, com nossa query, isso não deve ocorrer a menos que haja um erro.
                self._view.mostrar_dialogo_feedback(
                    "Atenção", "Nenhuma alteração foi salva.")
        except sqlite3.IntegrityError:
            self._view.mostrar_dialogo_feedback(
                "Nome Duplicado", "Já existe outro serviço com este nome.")
        except Exception as e:
            logger.error(
                f"Erro crítico ao salvar alterações do serviço: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Não foi possível salvar as alterações.\nErro: {e}")
