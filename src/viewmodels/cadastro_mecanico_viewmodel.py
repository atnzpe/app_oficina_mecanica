# =================================================================================
# MÓDULO DO VIEWMODEL DE CADASTRO DE MECÂNICO (cadastro_mecanico_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio para a tela de cadastro de mecânicos,
#           incluindo validação de formulário e interação com a camada de dados.
# =================================================================================
import flet as ft
import logging
import sqlite3
from src.database import queries

logger = logging.getLogger(__name__)

class CadastroMecanicoViewModel:
    """
    O ViewModel para a CadastroMecanicoView.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'CadastroMecanicoView' | None = None
        logger.debug("CadastroMecanicoViewModel inicializado.")

    def vincular_view(self, view: 'CadastroMecanicoView'):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view
        logger.debug("ViewModel de Cadastro de Mecânico vinculado à sua View.")

    def salvar_mecanico(self):
        """Pega dados da View, valida, e comanda a criação do novo mecânico."""
        if not self._view:
            logger.error("ViewModel: Ação 'salvar_mecanico' chamada sem uma View vinculada.")
            return

        try:
            dados = self._view.obter_dados_formulario()
            nome = dados.get("nome", "").strip()
            cpf = dados.get("cpf", "").strip()

            # --- LÓGICA DE VALIDAÇÃO ---
            if not nome or not cpf:
                self._view.mostrar_dialogo_feedback("Erro de Validação", "Os campos 'Nome' e 'CPF' são obrigatórios.")
                return

            # --- INTERAÇÃO COM A CAMADA DE DADOS ---
            logger.info(f"ViewModel: Tentando salvar o novo mecânico '{nome}'.")
            novo_mecanico = queries.criar_mecanico(
                nome=nome,
                cpf=cpf,
                endereco=dados.get("endereco", "").strip(),
                telefone=dados.get("telefone", "").strip(),
                especialidade=dados.get("especialidade", "").strip()
            )

            if novo_mecanico:
                logger.info(f"Mecânico '{nome}' cadastrado com sucesso.")
                acao_navegacao = lambda: self.page.go("/gerir_mecanicos")
                self._view.mostrar_dialogo_feedback("Sucesso!", "Mecânico cadastrado com sucesso!", acao_navegacao)

        except sqlite3.IntegrityError:
            logger.warning(f"Tentativa de cadastrar mecânico com CPF duplicado: {cpf}")
            self._view.mostrar_dialogo_feedback("CPF Duplicado", f"Já existe um mecânico cadastrado com este CPF.")
        except Exception as e:
            logger.error(f"Erro inesperado ao salvar mecânico: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback("Erro Crítico", f"Ocorreu uma falha inesperada:\n{e}")

    def cancelar_cadastro(self, e):
        """Navega de volta para a lista de mecânicos."""
        logger.info("Cadastro de mecânico cancelado. Redirecionando para /gerir_mecanicos.")
        self.page.go("/gerir_mecanicos")