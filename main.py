

import flet as ft  
import threading
from flet import Dropdown, dropdown  # Importa Dropdown e dropdown

from oficina_app import OficinaApp, processar_fila_db
from utils import criar_pastas


# Função principal para iniciar a aplicação.
def main(page: ft.Page):
    """
    Função principal para iniciar a aplicação.
    """

    # Define o título da página como "Oficina Guarulhos".
    page.title = "Oficina Guarulhos"
    # Define a orientação vertical para os controles na página.
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    # Cria uma instância da aplicação OficinaApp.
    app = OficinaApp(page)

    # Executa a função processar_fila_db em uma thread separada.
    thread_db = threading.Thread(target=processar_fila_db, args=(page,), daemon=True)
    thread_db.start()
    page.on_close = lambda e: page.window_destroy()

    # Inscreva-se para receber mensagens da thread do banco de dados
    page.pubsub.subscribe(app._on_message)

    # Criar as pastas necessárias
    criar_pastas(".")

    # Constrói a interface do usuário chamando o método build da instância app.
    
    page.add(app.build())


# Inicializa a aplicação Flet com a função main se este script for executado.
ft.app(target=main)
