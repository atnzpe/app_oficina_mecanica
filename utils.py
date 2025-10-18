import flet as ft
import os

def criar_pastas(caminho_base):
    """Cria as pastas essenciais do projeto no caminho especificado, 
    caso ainda não existam.

    Args:
        caminho_base (str): O caminho base onde as pastas serão criadas.
    """
    
    # Adiciona o novo diretório de uploads
    pastas = ["historico", "data", "report", "orcamento", "backup", "assets/uploads"]

    for pasta in pastas:
        caminho_completo = os.path.join(caminho_base, pasta)
        if not os.path.exists(caminho_completo):
            try:
                # os.makedirs cria diretórios aninhados (como assets/uploads)
                os.makedirs(caminho_completo)
                print(f"Pasta '{pasta}' criada com sucesso em '{caminho_completo}'.")
            except OSError as e:
                print(f"Erro ao criar a pasta '{pasta}': {e}")
        else:
            print(f"Pasta '{pasta}' já existe em '{caminho_completo}'.")