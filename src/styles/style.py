# Local do Arquivo: src/styles/style.py

# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE ESTILOS GLOBAIS (style.py)
#
# OBJETIVO: Centralizar todas as constantes de design da aplicação, como cores,
#           fontes, dimensões e estilos de componentes. Isso garante uma
#           identidade visual consistente e facilita a manutenção do design.
# ATUALIZAÇÃO:
#   - Ajustada a cor `error` do tema escuro para `RED_400` para melhor contraste
#     em fundos escuros.
# =================================================================================

import flet as ft

# =================================================================================
# PALETAS DE CORES
# =================================================================================

# Define o esquema de cores para o tema claro (Light Mode).
# Este esquema é usado quando o fundo da aplicação é claro. As cores foram escolhidas
# para ter um bom contraste e uma aparência profissional e sóbria.
light_color_scheme = ft.ColorScheme(
    # Cor principal para elementos interativos importantes como botões, links ativos e app bars.
    # BLUE_GREY_800 é um azul-acinzentado escuro, forte e profissional.
    primary=ft.Colors.BLUE_GREY_800,
    
    # Cor do conteúdo (texto, ícones) que fica SOBRE a cor primária.
    # WHITE (branco) oferece contraste máximo sobre o azul-acinzentado escuro.
    on_primary=ft.Colors.WHITE,
    
    # Uma cor mais suave, usada para preencher "containers" ou fundos de seções relacionadas à cor primária.
    # BLUE_GREY_100 é um tom muito claro de azul-acinzentado.
    primary_container=ft.Colors.BLUE_GREY_100,
    
    # Cor do conteúdo que fica SOBRE o 'primary_container'.
    # BLUE_GREY_900 (quase preto) garante excelente legibilidade sobre o fundo claro do container.
    on_primary_container=ft.Colors.BLUE_GREY_900,
    
    # Cor secundária para elementos flutuantes ou de menor ênfase, como badges ou switches.
    # TEAL_600 é um verde-azulado vibrante que complementa a cor primária.
    secondary=ft.Colors.TEAL_600,
    
    # Cor do conteúdo (texto, ícones) que fica SOBRE a cor secundária.
    # WHITE (branco) tem ótimo contraste com o TEAL_600.
    on_secondary=ft.Colors.WHITE,
    
    # Cor de fundo principal da aplicação.
    # WHITE (branco) é o padrão para temas claros, oferecendo um visual limpo.
    background=ft.Colors.WHITE,
    
    # Cor do conteúdo que fica SOBRE o fundo principal.
    # BLACK87 é um preto com 87% de opacidade, padrão do Material Design para textos, sendo menos "duro" que o preto puro.
    on_background=ft.Colors.BLACK87,
    
    # Cor de "superfícies" como cards, dialogs e menus.
    # GREY_50 é um cinza muito claro, quase branco, para diferenciar levemente as superfícies do fundo.
    surface=ft.Colors.GREY_50,
    
    # Cor do conteúdo que fica SOBRE as superfícies.
    on_surface=ft.Colors.BLACK87,
    
    # Cor para indicar erros, como em campos de formulário inválidos ou mensagens de falha.
    # RED_700 é um vermelho escuro e forte, universalmente reconhecido como cor de erro.
    error=ft.Colors.RED_700,
    
    # Cor do conteúdo SOBRE a cor de erro.
    # WHITE (branco) garante legibilidade sobre o vermelho escuro.
    on_error=ft.Colors.WHITE,
    
    # Cor de fundo para "containers" de erro, como um fundo para uma mensagem de erro.
    # Usa o RED_700 com 20% de opacidade, criando um realce vermelho suave.
    error_container=ft.Colors.with_opacity(0.2, ft.Colors.RED_700),
    
    # Cor do conteúdo SOBRE o 'error_container'.
    on_error_container=ft.Colors.RED_700,
)

# Define o esquema de cores para o tema escuro (Dark Mode).
# Este esquema visa reduzir o cansaço visual em ambientes com pouca luz e economizar bateria em telas OLED.
dark_color_scheme = ft.ColorScheme(
    # Cor primária para o tema escuro.
    # CYAN_ACCENT_400 é um ciano vibrante, que se destaca bem em fundos escuros.
    primary=ft.Colors.CYAN_ACCENT_400,
    
    # Cor do conteúdo SOBRE a cor primária.
    # BLACK (preto) oferece o maior contraste possível sobre o ciano vibrante.
    on_primary=ft.Colors.BLACK,
    
    # Cor para containers relacionados à cor primária.
    # CYAN_800 é um ciano escuro, que funciona bem como fundo para seções.
    primary_container=ft.Colors.CYAN_800,
    
    # Cor do conteúdo SOBRE o 'primary_container'.
    # CYAN_50 é um ciano muito claro, quase branco, garantindo legibilidade.
    on_primary_container=ft.Colors.CYAN_50,
    
    # Cor secundária para o tema escuro.
    # TEAL_ACCENT_400 é um verde-azulado vibrante, complementar ao ciano.
    secondary=ft.Colors.TEAL_ACCENT_400,
    
    # Cor do conteúdo SOBRE a cor secundária.
    on_secondary=ft.Colors.BLACK,
    
    # Cor de fundo principal da aplicação.
    # "#121212" é o preto recomendado pelo Material Design para temas escuros, pois é menos "chapado" que o preto puro.
    background="#121212",
    
    # Cor do conteúdo SOBRE o fundo principal.
    # WHITE (branco) é a escolha óbvia para texto em fundo escuro, garantindo máximo contraste.
    on_background=ft.Colors.WHITE,
    
    # Cor para superfícies como cards e barras.
    # "#1e1e1e" é um cinza escuro que cria uma sutil elevação visual sobre o fundo #121212.
    surface="#1e1e1e",
    
    # Cor do conteúdo SOBRE as superfícies.
    on_surface=ft.Colors.WHITE,
    
    # Cor para indicar erros no tema escuro.
    # RED_400 é um tom de vermelho mais claro que o RED_700, otimizado para ter melhor visibilidade e contraste em fundos escuros.
    error=ft.Colors.RED_400,
    
    # Cor do conteúdo SOBRE a cor de erro.
    on_error=ft.Colors.BLACK,
    
    # Cor de fundo para "containers" de erro.
    error_container=ft.Colors.with_opacity(0.2, ft.Colors.RED_400),
    
    # Cor do conteúdo SOBRE o 'error_container'.
    on_error_container=ft.Colors.RED_400,
)

# Esquema de cores personalizado para feedback de SUCESSO.
# Pode ser usado em SnackBars ou notificações para indicar que uma operação foi bem-sucedida.
success_color_scheme = ft.ColorScheme(
    primary=ft.Colors.GREEN_600, # Verde universalmente associado ao sucesso.
    on_primary=ft.Colors.WHITE,  # Branco para contraste sobre o verde.
    primary_container=ft.Colors.with_opacity(0.2, ft.Colors.GREEN_600), # Fundo verde claro para containers.
    on_primary_container=ft.Colors.GREEN_600 # Texto verde escuro sobre o fundo claro.
)

# =================================================================================
# TEMAS COMPLETOS
# =================================================================================

class AppThemes:
    """
    Agrupa os objetos de Tema (ft.Theme) completos para fácil importação no main.py.
    Um Tema é a combinação de um esquema de cores com outras propriedades visuais.
    """
    # Cria o objeto de tema claro completo.
    light_theme = ft.Theme(
        color_scheme=light_color_scheme,
        # Define a densidade visual como "compacta", o que reduz os espaçamentos
        # dos componentes, ideal para aplicações desktop com muita informação.
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
    """
    Define os tamanhos de fonte padrão para a aplicação em uma escala semântica.
    Usar essas variáveis em vez de números "mágicos" (ex: size=28) torna o código
    mais legível e fácil de manter a consistência visual.
    """
    TITLE_LARGE = 32      # Para títulos de página muito importantes.
    TITLE_MEDIUM = 28     # Para títulos de seção ou de AppBar.
    BODY_LARGE = 20       # Para textos de corpo de destaque.
    BODY_MEDIUM = 16      # Tamanho padrão para a maioria dos textos.
    BODY_SMALL = 14       # Para textos secundários, como legendas ou hints.

class AppDimensions:
    """
    Define dimensões e raios de borda reutilizáveis para os componentes.
    Isso garante que elementos como campos de texto e botões tenham uma aparência
    uniforme em toda a aplicação.
    """
    FIELD_WIDTH = 350       # Largura padrão para campos de texto (TextFields) e botões.
    BORDER_RADIUS = 10      # Raio de borda para criar cantos arredondados consistentes.
    PAGE_PADDING = 15       # Preenchimento (espaçamento interno) padrão para as páginas.
    CARD_ELEVATION = 4      # Sombra padrão para componentes "elevados" como Cards.