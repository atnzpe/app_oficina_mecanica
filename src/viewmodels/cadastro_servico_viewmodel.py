# =================================================================================
# MÓDULO DO VIEWMODEL DE CADASTRO DE SERVIÇO (cadastro_servico_viewmodel.py)
#
# OBJETIVO: Conter a lógica para a tela de cadastro de serviços, incluindo a
#           lógica de busca e filtragem para a seleção de peças.
# =================================================================================
import flet as ft
import logging
import sqlite3
from src.database import queries
from src.models.models import Peca
from typing import List

logger = logging.getLogger(__name__)


class CadastroServicoViewModel:
    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'CadastroServicoView' | None = None
        # Estado: Armazena a lista completa de peças para a busca
        self._todas_as_pecas: List[Peca] = []
        logger.debug("CadastroServicoViewModel inicializado.")

    def vincular_view(self, view: 'CadastroServicoView'):
        self._view = view

    def carregar_pecas_iniciais(self):
        """Busca a lista de peças ativas para popular a seleção inicial."""
        if not self._view:
            return
        logger.info("ViewModel: Carregando lista de peças para o formulário.")
        try:
            # Armazena a lista completa de peças no ViewModel
            self._todas_as_pecas = [
                p for p in queries.obter_pecas() if p.ativo]
            # Manda a lista completa para a View popular os checkboxes
            self._view.popular_lista_pecas(self._todas_as_pecas)
        except Exception as e:
            logger.error(f"Erro ao carregar peças: {e}", exc_info=True)
            self._view.mostrar_dialogo_feedback(
                "Erro Crítico", "Não foi possível carregar a lista de peças.")

    def filtrar_pecas(self, termo_busca: str):
        """Filtra a lista de peças com base no termo de busca e comanda a View."""
        if not self._view:
            return
        termo = termo_busca.lower().strip()
        if not termo:
            # Se a busca estiver vazia, exibe todas as peças
            pecas_filtradas = self._todas_as_pecas
        else:
            # Filtra a lista em memória
            pecas_filtradas = [
                peca for peca in self._todas_as_pecas
                if termo in peca.nome.lower() or termo in peca.referencia.lower()
            ]

        logger.debug(
            f"Filtrando peças com o termo '{termo}'. {len(pecas_filtradas)} resultados.")
        # Comanda a View para atualizar a lista de checkboxes visível
        self._view.atualizar_lista_filtrada_pecas(pecas_filtradas)

    def salvar_servico(self):
        """Pega dados da View, valida, e comanda a criação do novo serviço."""
        if not self._view:
            return

        try:
            dados = self._view.obter_dados_formulario()
            nome = dados.get("nome", "").strip()
            valor = dados.get("valor")

            if not nome or valor is None:
                self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "Os campos 'Nome do Serviço' e 'Valor' são obrigatórios e devem ser válidos.")
                return

            logger.info(f"ViewModel: Tentando salvar o novo serviço '{nome}'.")
            novo_servico = queries.criar_servico(
                nome=nome,
                descricao=dados.get("descricao", "").strip(),
                valor=valor,
                pecas_ids=dados.get("pecas_selecionadas", [])
            )

            if novo_servico:
                logger.info(f"Serviço '{nome}' cadastrado com sucesso.")
                def acao_navegacao(): return self.page.go("/gerir_servicos")
                self._view.mostrar_dialogo_feedback(
                    "Sucesso!", "Serviço cadastrado com sucesso!", acao_navegacao)

        except sqlite3.IntegrityError:
            logger.warning(
                f"Tentativa de cadastrar serviço com nome duplicado: {nome}")
            self._view.mostrar_dialogo_feedback(
                "Nome Duplicado", "Já existe um serviço cadastrado com este nome.")
        except Exception as e:
            logger.error(
                f"Erro inesperado ao salvar serviço: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Ocorreu uma falha inesperada:\n{e}")

    def cancelar_cadastro(self, e):
        self.page.go("/gerir_servicos")
