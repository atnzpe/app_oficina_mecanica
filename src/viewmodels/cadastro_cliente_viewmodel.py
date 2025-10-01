# =================================================================================
# MÓDULO DO VIEWMODEL DE CADASTRO DE CLIENTE (cadastro_cliente_viewmodel.py)
#
# ATUALIZAÇÃO (UX & Robustez):
#   - Refatorado para usar o fluxo de feedback com diálogo explícito, passando
#     a navegação como uma ação de callback para a View.
#   - Adicionado tratamento de exceções (try...except) para robustez.
# =================================================================================
import logging
import sqlite3
import flet as ft

from src.database import queries

# Configura o logger para este módulo.
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
        Pega dados da View, valida, e comanda a exibição de um diálogo de feedback.
        A navegação ocorre somente após o usuário clicar em "OK" no diálogo.
        """
        if not self._view:
            logging.error(
                "ViewModel: Ação 'salvar_cliente' chamada sem uma View vinculada.")
            return

        try:
            # 1. SOLICITA OS DADOS DA VIEW
            dados = self._view.obter_dados_formulario()
            nome = dados.get("nome")
            telefone = dados.get("telefone")
            endereco = dados.get("endereco")

            # 2. LÓGICA DE VALIDAÇÃO
            if not nome or not nome.strip():
                return self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "O campo 'Nome do Cliente' é obrigatório.", None)
            if not telefone or not telefone.strip():
                self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "O campo 'Telefone' é obrigatório.", None)
                return
            if not endereco or not endereco.strip():
                self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "O campo 'Endereço' é obrigatório.", None)
                return

            # 3. INTERAÇÃO COM A CAMADA DE DADOS
            logger.info(f"ViewModel: Tentando salvar o novo cliente '{nome}'.")
            novo_cliente = queries.criar_cliente(
                nome=nome, telefone=telefone, endereco=endereco, email=dados.get(
                    "email")
            )

            # 4. COMANDA A VIEW COM BASE NO RESULTADO
            if novo_cliente:
                logger.info(f"Cadatrado cliente {nome}.")
                # Prepara a ação de navegação que será executada no futuro.
                
                
                #"""cadastro_cliente_viewmodel.py Função de callback para navegação após o diálogo."""
                logger.info(f"Indo para pagina gerir clientes.")
                self.page.go("/gerir_clientes")
                # Comanda a View para mostrar o diálogo de sucesso, passando a ação.
                

        except sqlite3.IntegrityError:
            # Trata o caso específico de cliente duplicado
            logging.warning(
                f"Tentativa de cadastrar cliente duplicado: {nome} / {telefone}")
            self._view.mostrar_dialogo_feedback(
                "Cliente Duplicado", "Já existe um cliente cadastrado com este nome e telefone.", None)

        except Exception as e:
            # Trata qualquer outro erro inesperado.
            logging.error(
                f"Erro inesperado ao salvar cliente: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Ocorreu uma falha inesperada:\n{e}", None)

    def cancelar_cadastro(self, e):
        """Navega de volta para a lista de clientes."""
        logger.info(
            "Cadastro de cliente cancelado. Redirecionando para /gerir_clientes.")
        self.page.go("/gerir_clientes")
