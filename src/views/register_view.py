# =================================================================================
# MÓDULO DA VIEW DE CADASTRO (register_view.py)
# =================================================================================

import flet as ft
import logging
from app.services import auth_service

# --- NOVO: Importa a AppBar reutilizável ---
from app.components.app_bar import create_app_bar

logger = logging.getLogger(__name__)

# --- ATUALIZADO: A view agora aceita page e on_logout ---
def create_register_view(page: ft.Page, on_logout, on_register_success) -> ft.View:
    """
    Cria e retorna a View de Cadastro de novos usuários.
    """
    logger.info("Criando a interface gráfica e a lógica da tela de cadastro.")

    # --- ATUALIZADO: Cria a AppBar e define seu título ---
    app_bar = create_app_bar(page, on_logout)
    app_bar.title = ft.Text("Criar Nova Conta")
    
    # --- (O restante dos componentes permanece o mesmo) ---
    name_field = ft.TextField(
        label="Nome Completo", hint_text="Digite seu nome", 
        width=AppDimensions.FIELD_WIDTH,
        prefix_icon=ft.Icons.PERSON, 
        border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
    )
    email_field = ft.TextField(
        label="E-mail", hint_text="Digite seu e-mail", 
        width=AppDimensions.FIELD_WIDTH,
        keyboard_type=ft.KeyboardType.EMAIL, 
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
    )
    password_field = ft.TextField(
        label="Senha", hint_text="Crie uma senha", 
        width=AppDimensions.FIELD_WIDTH,
        password=True, can_reveal_password=True, 
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
    )
    confirm_password_field = ft.TextField(
        label="Confirmar Senha", hint_text="Digite a senha novamente", 
        width=AppDimensions.FIELD_WIDTH,
        password=True, can_reveal_password=True, 
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border_radius=ft.border_radius.all(AppDimensions.BORDER_RADIUS),
    )
    error_text = ft.Text(value="", visible=False)
    progress_ring = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)

    def handle_register_click(e):
        # ... (lógica de clique permanece a mesma)
        error_text.visible = False
        if not all([name_field.value, email_field.value, password_field.value, confirm_password_field.value]):
            error_text.value = "Todos os campos são obrigatórios."
            error_text.color = e.page.theme.color_scheme.error
            error_text.visible = True
            e.page.update()
            return
        if password_field.value != confirm_password_field.value:
            error_text.value = "As senhas não coincidem."
            error_text.color = e.page.theme.color_scheme.error
            error_text.visible = True
            e.page.update()
            return
        for field in [name_field, email_field, password_field, confirm_password_field, register_button]:
            field.disabled = True
        progress_ring.visible = True
        e.page.update()
        result, message = auth_service.register_user(
            name=name_field.value.strip(),
            email=email_field.value.strip(),
            password=password_field.value
        )
        if result:
            on_register_success()
        else:
            error_text.value = message
            error_text.color = e.page.theme.color_scheme.error
            error_text.visible = True
        for field in [name_field, email_field, password_field, confirm_password_field, register_button]:
            field.disabled = False
        progress_ring.visible = False
        e.page.update()

    register_button = ft.ElevatedButton(
        text="Cadastrar", 
        width=AppDimensions.FIELD_WIDTH, 
        height=45, 
        icon=ft.Icons.APP_REGISTRATION,
        on_click=handle_register_click
    )
    login_text = ft.Row(
        [ft.Text("Já tem uma conta?"), ft.TextButton("Faça o login", on_click=lambda e: e.page.go("/"))],
        alignment=ft.MainAxisAlignment.CENTER, spacing=5,
    )

    return ft.View(
        route="/register",
        appbar=app_bar, # Usa a AppBar padronizada
        controls=[
            ft.Column(
                [
                    name_field, email_field, password_field, confirm_password_field,
                    error_text,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Row([register_button, progress_ring], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    login_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
