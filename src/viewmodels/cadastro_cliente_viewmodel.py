# =================================================================================
# MÓDULO DO VIEWMODEL DE CADASTRO DE CLIENTE (cadastro_cliente_viewmodel.py)
#
# ATUALIZAÇÃO (UX & Robustez):
#   - Substituída a lógica de feedback por um comando para a View exibir um
#     CupertinoAlertDialog, que é mais explícito.
#   - Adicionado tratamento de exceções (try...except) para robustez.
# =================================================================================
import flet as ft
import logging
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
        A navegação ocorre após o usuário fechar o diálogo.
        """
        # Garante que a view esteja vinculada para evitar erros.
        if not self._view:
            logging.error(
                "ViewModel: Ação 'salvar_cliente' chamada sem uma View vinculada.")
            return

        try:
            dados = self._view.obter_dados_formulario()
            nome = dados.get("nome")
            telefone = dados.get("telefone")
            endereco = dados.get("endereco")

            # Validação explícita: Simples é melhor que complexo.
            if not nome or not nome.strip():
                self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "O campo 'Nome do Cliente' é obrigatório.", None)
                return
            if not telefone or not telefone.strip():
                self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "O campo 'Telefone' é obrigatório.", None)
                return
            if not endereco or not endereco.strip():
                self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "O campo 'Endereço' é obrigatório.", None)
                return

            logger.info(f"ViewModel: Tentando salvar o novo cliente '{nome}'.")
            novo_cliente = queries.criar_cliente(
                nome=nome, telefone=telefone, endereco=endereco, email=dados.get(
                    "email")
            )

            if novo_cliente:
                logger.info(
                    f"Cliente '{nome}' salvo. Exibindo diálogo de sucesso.")
                # A ação de navegação é passada para a view, que a executará após o "OK".
                def on_ok_action(_): return self.page.go("/gerir_clientes")
                self._view.mostrar_dialogo_feedback(
                    "Sucesso!",
                    f"Cliente '{novo_cliente.nome}' cadastrado com sucesso!",
                    on_ok_action
                )
            else:
                # Se a query retornar None, é um erro interno do banco de dados.
                self._view.mostrar_dialogo_feedback(
                    "Erro Interno", "Ocorreu um erro ao salvar os dados no banco.", None)

        except Exception as e:
            # Erros devem ser explícitos e nunca passar silenciosamente.
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
