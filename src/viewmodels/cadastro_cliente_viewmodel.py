# -*- coding: utf-8 -*-

## =================================================================================
# MÓDULO DO VIEWMODEL DE CADASTRO DE CLIENTE (cadastro_cliente_viewmodel.py)
#
# ATUALIZAÇÃO:
#   - `salvar_cliente`: Após o sucesso, agora usa `self.page.go()` para navegar
#     de volta ao dashboard em vez de fechar um modal.
#   - `cancelar_cadastro`: Novo método para lidar com o clique no botão "Cancelar",
#     navegando de volta ao dashboard.
# =================================================================================
import flet as ft
import logging
from src.database import queries

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
        Pega os dados da View, valida, comanda a inserção no banco de dados e
        redireciona o usuário.
        """
        if not self._view:
            return

        dados = self._view.obter_dados_formulario()
        nome = dados.get("nome")
        
        # A lógica de validação permanece a mesma.
        if not nome or not nome.strip():
            logger.warning("Tentativa de salvar cliente sem nome.")
            self._view.mostrar_feedback("O campo 'Nome' é obrigatório.", False)
            return

        logger.info(f"ViewModel: Tentando salvar o novo cliente '{nome}'.")
        novo_cliente = queries.criar_cliente(
            nome=nome,
            telefone=dados.get("telefone"),
            endereco=dados.get("endereco"),
            email=dados.get("email")
        )

        if novo_cliente:
            # SUCESSO: Mostra o feedback e NAVEGA de volta para o dashboard.
            logger.info(f"Cliente '{nome}' salvo com sucesso. Redirecionando para /dashboard.")
            # A snackbar ainda será exibida na tela atual antes da navegação.
            self._view.mostrar_feedback(f"Cliente '{novo_cliente.nome}' cadastrado com sucesso!", True)
            self.page.go("/dashboard")
        else:
            # FALHA: Apenas mostra o feedback de erro.
            self._view.mostrar_feedback("Ocorreu um erro ao cadastrar o cliente.", False)
    
    def cancelar_cadastro(self, e):
        """
        Navega de volta para o dashboard sem salvar nenhuma informação.
        """
        logger.info("Cadastro de cliente cancelado. Redirecionando para /dashboard.")
        self.page.go("/dashboard")
        