# =================================================================================
# MÓDULO DO VIEWMODEL DE EDIÇÃO DE MECÂNICO (editar_mecanico_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de edição de mecânicos.
# =================================================================================
import flet as ft
import logging
import sqlite3
from src.database import queries
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class EditarMecanicoViewModel:
    def __init__(self, page: ft.Page, mecanico_id: int):
        self.page = page
        self.mecanico_id = mecanico_id
        self._view: 'EditarMecanicoView' | None = None
        logger.debug(
            f"ViewModel de Edição de Mecânico inicializado para o ID: {self.mecanico_id}")

    def vincular_view(self, view: 'EditarMecanicoView'):
        """Vincula a View ao ViewModel."""
        self._view = view
        logger.debug("ViewModel de Edição de Mecânico vinculado à sua View.")

    def carregar_dados(self):
        """Busca os dados do mecânico e comanda a View para preencher o formulário."""
        if not self._view:
            return
        try:
            logger.info(
                f"ViewModel: buscando dados para o mecânico ID {self.mecanico_id}")
            mecanico = queries.obter_mecanico_por_id(self.mecanico_id)
            if mecanico:
                self._view.preencher_formulario(mecanico)
                logger.info(
                    f"ViewModel: Dados do mecânico '{mecanico.nome}' carregados.")
            else:
                logger.warning(
                    f"ViewModel: Mecânico com ID {self.mecanico_id} não encontrado.")

                def acao_navegacao(): return self.page.go("/gerir_mecanicos")
                self._view.mostrar_dialogo_feedback(
                    "Erro", "Mecânico não encontrado.", acao_navegacao)
        except Exception as e:
            logger.error(
                f"Erro crítico ao carregar dados do mecânico: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Não foi possível carregar os dados do mecânico.\nErro: {e}")

    def salvar_alteracoes(self):
        """Valida e salva as alterações no banco de dados."""
        if not self._view:
            return
        try:
            dados = self._view.obter_dados_formulario()
            nome = dados.get("nome", "").strip()
            cpf = dados.get("cpf", "").strip()

            if not nome or not cpf:
                self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "Os campos 'Nome' e 'CPF' são obrigatórios.")
                return

            logger.info(
                f"ViewModel: salvando alterações para o mecânico ID {self.mecanico_id}")
            sucesso = queries.atualizar_mecanico(
                self.mecanico_id,
                nome,
                cpf,
                dados.get("endereco", "").strip(),
                dados.get("telefone", "").strip(),
                dados.get("especialidade", "").strip()
            )
            def acao_navegacao(): return self.page.go("/gerir_mecanicos")

            if sucesso:
                self._view.mostrar_dialogo_feedback(
                    "Sucesso!", "Mecânico atualizado com sucesso!", acao_navegacao)
            else:
                self._view.mostrar_dialogo_feedback(
                    "Atenção", "Nenhuma alteração foi salva.")
        except sqlite3.IntegrityError:
            self._view.mostrar_dialogo_feedback(
                "CPF Duplicado", f"Já existe outro mecânico cadastrado com o CPF '{cpf}'.")
        except Exception as e:
            logger.error(
                f"Erro crítico ao salvar alterações do mecânico: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Não foi possível salvar as alterações.\nErro: {e}")
