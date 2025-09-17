# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE GERENCIAMENTO DO BANCO DE DADOS (database.py)
#
# OBJETIVO: Centralizar toda a lógica de interação com o banco de dados SQLite.
#
# SEÇÕES ALTERADAS NESTA REATORAÇÃO:
#   - Funções `criar_tabela_*` foram consolidadas numa única função `criar_tabelas`.
#   - Substituído `print()` por `logging` para um output mais profissional.
#   - Adicionada a função `buscar_usuario_por_nome` que estava em falta.
#   - A lógica de `criar_usuario_admin` foi integrada em `inicializar_banco_de_dados`.
# =================================================================================
import sqlite3
import os
from datetime import datetime
import queue
import logging
import bcrypt

# Importa os modelos para que as funções possam retornar objetos tipados
from src.models.models import Cliente, Carro, Peca, Usuario

# --- CONFIGURAÇÃO GLOBAL ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
NOME_BANCO_DE_DADOS = "./data/database.db"
fila_db = queue.Queue()

# --- FUNÇÕES DE CONEXÃO E ESTRUTURA ---

def criar_conexao_banco_de_dados(caminho_db: str) -> sqlite3.Connection | None:
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    try:
        diretorio = os.path.dirname(caminho_db)
        os.makedirs(diretorio, exist_ok=True)
        conexao = sqlite3.connect(caminho_db)
        conexao.row_factory = sqlite3.Row
        logging.info(f"Conexão com o banco de dados '{caminho_db}' estabelecida.")
        return conexao
    except sqlite3.Error as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def executar_consulta_sql(conexao: sqlite3.Connection, sql: str, parametros: tuple = ()):
    """Executa uma única consulta SQL (CREATE, INSERT, UPDATE, etc)."""
    try:
        cursor = conexao.cursor()
        cursor.execute(sql, parametros)
        conexao.commit()
    except sqlite3.Error as e:
        logging.error(f"Erro ao executar a consulta SQL: {e}\nQuery: {sql}")

def criar_tabelas(conexao: sqlite3.Connection):
    """Cria todas as tabelas do banco de dados se elas ainda não existirem."""
    logging.info("Verificando e criando tabelas do banco de dados...")
    queries = [
        """CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, senha TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, telefone TEXT, endereco TEXT, email TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS carros (
            id INTEGER PRIMARY KEY AUTOINCREMENT, modelo TEXT NOT NULL, ano INTEGER, cor TEXT,
            placa TEXT NOT NULL UNIQUE, cliente_id INTEGER, FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )""",
        """CREATE TABLE IF NOT EXISTS pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, referencia TEXT NOT NULL, fabricante TEXT,
            descricao TEXT, preco_compra REAL NOT NULL, preco_venda REAL NOT NULL,
            quantidade_em_estoque INTEGER NOT NULL CHECK (quantidade_em_estoque >= 0)
        )""",
        """CREATE TABLE IF NOT EXISTS ordem_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER NOT NULL, carro_id INTEGER NOT NULL,
            data_criacao TEXT NOT NULL, valor_total REAL NOT NULL, mao_de_obra REAL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id), FOREIGN KEY (carro_id) REFERENCES carros(id)
        )""",
        """CREATE TABLE IF NOT EXISTS PecasOrdemServico (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ordem_servico_id INTEGER NOT NULL, peca_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL, FOREIGN KEY (ordem_servico_id) REFERENCES ordem_servico (id),
            FOREIGN KEY (peca_id) REFERENCES pecas (id)
        )""",
        """CREATE TABLE IF NOT EXISTS movimentacao_pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, peca_id INTEGER NOT NULL, data_movimentacao TEXT NOT NULL,
            tipo_movimentacao TEXT NOT NULL CHECK (tipo_movimentacao IN ('entrada', 'saida')),
            quantidade INTEGER NOT NULL, ordem_servico_id INTEGER,
            FOREIGN KEY (peca_id) REFERENCES pecas(id), FOREIGN KEY (ordem_servico_id) REFERENCES ordem_servico(id)
        )"""
    ]
    for query in queries:
        executar_consulta_sql(conexao, query)
    logging.info("Finalizada a verificação/criação de tabelas.")

def inicializar_banco_de_dados():
    """Função de setup completo: cria conexão, tabelas e usuário admin."""
    logging.info("Inicializando o banco de dados...")
    conexao = criar_conexao_banco_de_dados(NOME_BANCO_DE_DADOS)
    if conexao:
        try:
            criar_tabelas(conexao)
            
            # --- LÓGICA DE CRIAÇÃO DO ADMIN IMPLEMENTADA AQUI ---
            cursor = conexao.cursor()
            admin_user = "admin@admin.com"
            admin_pass = "adm123"
            
            cursor.execute("SELECT id FROM usuarios WHERE nome = ?", (admin_user,))
            if not cursor.fetchone():
                senha_hash = bcrypt.hashpw(admin_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("INSERT INTO usuarios (nome, senha) VALUES (?, ?)", (admin_user, senha_hash))
                conexao.commit()
                logging.info(f"Utilizador administrador padrão '{admin_user}' criado com sucesso!")
            # ----------------------------------------------------

        finally:
            conexao.close()
            logging.info("Inicialização do banco de dados concluída. Conexão fechada.")

# --- FUNÇÕES DE LEITURA DE DADOS (SELECT) ---
def buscar_usuario_por_nome(conexao: sqlite3.Connection, nome_usuario: str) -> Usuario | None:
    """Busca um único usuário pelo seu nome de login."""
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nome = ?", (nome_usuario,))
        dados_usuario = cursor.fetchone()
        return Usuario(**dados_usuario) if dados_usuario else None
    except sqlite3.Error as e:
        logging.error(f"Erro ao buscar usuário por nome: {e}")
        return None

def obter_clientes(conexao: sqlite3.Connection) -> list[Cliente]:
    """Busca todos os clientes e retorna uma lista de objetos Cliente."""
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, telefone, endereco, email FROM clientes ORDER BY nome")
        return [Cliente(**row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logging.error(f"Erro ao obter clientes: {e}")
        return []

def obter_carros_por_cliente(conexao: sqlite3.Connection, cliente_id: int) -> list[Carro]:
    """Busca carros de um cliente e retorna uma lista de objetos Carro."""
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT id, modelo, ano, cor, placa, cliente_id FROM carros WHERE cliente_id = ?", (cliente_id,))
        return [Carro(**row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logging.error(f"Erro ao obter carros do cliente {cliente_id}: {e}")
        return []

def obter_pecas(conexao: sqlite3.Connection) -> list[Peca]:
    """Busca todas as peças e retorna uma lista de objetos Peca."""
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, referencia, fabricante, descricao, preco_compra, preco_venda, quantidade_em_estoque FROM pecas ORDER BY nome")
        return [Peca(**row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logging.error(f"Erro ao obter peças: {e}")
        return []

# --- BLOCO DE EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    inicializar_banco_de_dados()