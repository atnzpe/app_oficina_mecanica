# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE ESTILOS GLOBAIS (style.py)
# Local: src/styles/style.py
#
# OBJETIVO: Centralizar todas as constantes de design da aplicação, como cores,
#           fontes, dimensões e estilos de componentes. Isso garante uma
#           identidade visual consistente e facilita a manutenção do design.
#           Princípio do Zen of Python: "Não se repita."
# =================================================================================

import flet as ft

# =================================================================================
# PALETAS DE CORES
# Define esquemas de cores para os temas claro (light) e escuro (dark).
# =================================================================================

light_color_scheme = ft.ColorScheme(
    primary=ft.Colors.BLUE_GREY_800,
    on_primary=ft.Colors.WHITE,
    primary_container=ft.Colors.BLUE_GREY_100,
    secondary=ft.Colors.TEAL_600,
    on_secondary=ft.Colors.WHITE,
    background=ft.Colors.WHITE,
    on_background=ft.Colors.BLACK87,
    surface=ft.Colors.GREY_50,
    on_surface=ft.Colors.BLACK87,
    error=ft.Colors.RED_700,
    on_error=ft.Colors.WHITE,
)

dark_color_scheme = ft.ColorScheme(
    primary=ft.Colors.CYAN_ACCENT_400,
    on_primary=ft.Colors.BLACK,
    primary_container=ft.Colors.CYAN_800,
    secondary=ft.Colors.TEAL_ACCENT_400,
    on_secondary=ft.Colors.BLACK,
    background="#121212",
    on_background=ft.Colors.WHITE,
    surface="#1e1e1e",
    on_surface=ft.Colors.WHITE,
    error=ft.Colors.RED_ACCENT_200,
    on_error=ft.Colors.BLACK,
)

# =================================================================================
# TEMAS COMPLETOS
# Agrupa os esquemas de cores em objetos de Tema completos.
# =================================================================================

class AppThemes:
    """Agrupa os objetos de Tema para fácil importação."""
    light_theme = ft.Theme(color_scheme=light_color_scheme, visual_density=ft.VisualDensity.COMPACT)
    dark_theme = ft.Theme(color_scheme=dark_color_scheme, visual_density=ft.VisualDensity.COMPACT)

# =================================================================================
# FONTES E DIMENSÕES
# Define constantes reutilizáveis para tamanhos e dimensões.
# =================================================================================

class AppFonts:
    """Define os tamanhos de fonte padrão para a aplicação."""
    TITLE_LARGE = 32
    TITLE_MEDIUM = 28
    BODY_LARGE = 20
    BODY_MEDIUM = 16
    BODY_SMALL = 14

class AppDimensions:
    """Define dimensões e raios de borda reutilizáveis para os componentes."""
    FIELD_WIDTH = 350  # Largura padrão para campos de texto
    BORDER_RADIUS = 10 # Raio de borda padrão