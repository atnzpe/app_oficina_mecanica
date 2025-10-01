# Compartilhe aqui o CÓDIGO COMPLETO do ViewModel de forma explicita.
# O código deve estar comentado.

# -*- coding: utf-8 -*-
# =================================================================================
# MÓDULO DO VIEWMODEL DO DASHBOARD (dashboard_viewmodel.py)
#
# REATORAÇÃO:
#   - Simplificado para conter apenas a lógica do dashboard: navegação e
#     gerenciamento de tema.
#   - Adicionado o método `change_theme` para alternar entre os modos claro/escuro.
# =================================================================================
import flet as ft
import logging
from src.models.models import Usuario

class DashboardViewModel:
    """
    O ViewModel para a nova DashboardView. Focado em navegação e estado da UI.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'DashboardView' | None = None
        self.usuario_atual: Usuario | None = self.page.session.get("usuario_logado")
        
        if self.usuario_atual:
            logging.info("DashboardViewModel iniciado para o usuário: %s ",self.usuario_atual.nome)
        else:
            # Em uma aplicação real, se não houver usuário, deveríamos redirecionar para /login.
            logging.warning("DashboardViewModel iniciado sem um usuário na sessão.")

    def vincular_view(self, view: 'DashboardView'):
        """Vincula a View ao ViewModel."""
        self._view = view

    def change_theme(self, e):
        """Alterna o tema da página entre claro (LIGHT) e escuro (DARK)."""
        self.page.theme_mode = ft.ThemeMode.DARK if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        if self._view:
            # Comanda a view para atualizar o ícone do botão de tema.
            self._view.atualizar_icone_tema(self.page.theme_mode)
        self.page.update()

    def navigate(self, route: str):
        """Função genérica para navegar para uma rota específica."""
        logging.info(f"Navegando para a rota: {route}")
        self.page.go(route)
                
    def logout(self, e):
        """Executa o logout do usuário."""
        logging.info(f"Usuário '{self.usuario_atual.nome}' fazendo logout.")
        self.page.session.clear()
        self.usuario_atual = None
        self.page.go("/login")