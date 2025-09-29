# Local do Arquivo: src/styles/style.py

# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE ESTILOS GLOBAIS (style.py)
#
# OBJETIVO: Centralizar todas as constantes de design da aplicação, como cores,
#           fontes, dimensões e estilos de componentes. Isso garante uma
#           identidade visual consistente e facilita a manutenção do design.
# ATUALIZAÇÃO:
#   - Ajustada a cor `error` do tema escuro para `RED_400` para melhor contraste
#     em fundos escuros.
# =================================================================================

import flet as ft

# =================================================================================
# PALETAS DE CORES
# =================================================================================

# Define o esquema de cores para o tema claro.
light_color_scheme = ft.ColorScheme(
    primary=ft.Colors.BLUE_GREY_800,
    on_primary=ft.Colors.WHITE,
    primary_container=ft.Colors.BLUE_GREY_100,
    on_primary_container=ft.Colors.BLUE_GREY_900,
    secondary=ft.Colors.TEAL_600,
    on_secondary=ft.Colors.WHITE,
    background=ft.Colors.WHITE,
    on_background=ft.Colors.BLACK87,
    surface=ft.Colors.GREY_50,
    on_surface=ft.Colors.BLACK87,
    error=ft.Colors.RED_700,
    on_error=ft.Colors.WHITE,
    error_container=ft.Colors.with_opacity(0.2, ft.Colors.RED_700),
    on_error_container=ft.Colors.RED_700,
)

# Define o esquema de cores para o tema escuro.
dark_color_scheme = ft.ColorScheme(
    primary=ft.Colors.CYAN_ACCENT_400,
    on_primary=ft.Colors.BLACK,
    primary_container=ft.Colors.CYAN_800,
    on_primary_container=ft.Colors.CYAN_50,
    secondary=ft.Colors.TEAL_ACCENT_400,
    on_secondary=ft.Colors.BLACK,
    background="#121212", # Um preto ligeiramente suave.
    on_background=ft.Colors.WHITE, # Texto branco sobre fundo escuro (alto contraste).
    surface="#1e1e1e", # Cor para superfícies como cards e barras.
    on_surface=ft.Colors.WHITE, # Texto branco sobre superfícies escuras.
    # --- ALTERAÇÃO ---
    # Ajustado para RED_400 para melhor visibilidade em fundo escuro.
    error=ft.Colors.RED_400, 
    on_error=ft.Colors.BLACK,
    error_container=ft.Colors.with_opacity(0.2, ft.Colors.RED_400),
    on_error_container=ft.Colors.RED_400,
)

# Esquema de cores personalizado para SUCESSO.
success_color_scheme = ft.ColorScheme(
    primary=ft.Colors.GREEN_600,
    on_primary=ft.Colors.WHITE,
    primary_container=ft.Colors.with_opacity(0.2, ft.Colors.GREEN_600),
    on_primary_container=ft.Colors.GREEN_600
)

# =================================================================================
# TEMAS COMPLETOS
# =================================================================================

class AppThemes:
    """Agrupa os objetos de Tema para fácil importação."""
    # Cria o objeto de tema claro completo.
    light_theme = ft.Theme(
        color_scheme=light_color_scheme, 
        visual_density=ft.VisualDensity.COMPACT
    )
    # Cria o objeto de tema escuro completo.
    dark_theme = ft.Theme(
        color_scheme=dark_color_scheme, 
        visual_density=ft.VisualDensity.COMPACT
    )

# =================================================================================
# FONTES E DIMENSÕES
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
    FIELD_WIDTH = 350
    BORDER_RADIUS = 10
    PAGE_PADDING = 15
    CARD_ELEVATION = 4