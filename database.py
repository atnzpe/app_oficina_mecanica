import bcrypt
import sqlite3
import os
from datetime import datetime
import queue

# BANCO DE DADOS E FILA
nome_banco_de_dados = "./data/oficina_guarulhos.db"
banco_de_dados = nome_banco_de_dados
#conexao = criar_conexao_banco_de_dados(nome_banco_de_dados)
# Fila para operações do banco de dados (se necessário)
fila_db = queue.Queue()

# Versão do banco de dados
VERSAO_BANCO_DE_DADOS = "1.1"  # Incrementada a versão após a alteração

# FUNÇÕES DE BANCO DE DADOS

def criar_conexao_banco_de_dados(banco_de_dados):
    """
    Cria uma conexão com o banco de dados SQLite.
    Cria o banco de dados e as tabelas se não existirem.
    """
    banco_existe = os.path.exists(banco_de_dados)
    conexao = None
    try:
        print(f"Tentando abrir banco de dados em: {os.path.abspath(banco_de_dados)}")
        conexao = sqlite3.connect(banco_de_dados)
        if not banco_existe:
            criar_tabelas(conexao)
        print(f"Conexão com o banco de dados '{banco_de_dados}' estabelecida!")
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    return conexao



def executar_consulta_sql(conexao, sql, parametros=None):
    """Executa uma consulta SQL na conexão fornecida."""
    try:
        cursor = conexao.cursor()
        if parametros:
            cursor.execute(sql, parametros)
        else:
            cursor.execute(sql)
        conexao.commit()
    except sqlite3.Error as e:
        print(f"Erro ao executar a consulta SQL: {e}")


def criar_usuario_admin(conexao):
    """Cria o usuário administrador 'admin' se ele não existir."""
    with criar_conexao_banco_de_dados(banco_de_dados) as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT 1 FROM usuarios WHERE nome = 'admin'")
        if not cursor.fetchone():
            senha_hash = bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode()
            cursor.execute(
                "INSERT INTO usuarios (nome, senha) VALUES (?, ?)", ("admin", senha_hash)
            )
            conexao.commit()
            print("Usuário 'admin' criado com sucesso!")


def criar_tabela_usuarios(conexao):
    """Cria a tabela de usuários."""
    sql = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """
    executar_consulta_sql(conexao, sql)
    print("Tabela 'usuarios' criada!")


def criar_tabela_clientes(conexao):
    """Cria a tabela de clientes."""
    sql = """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            telefone TEXT,
            endereco TEXT,
            email TEXT
        )
    """
    executar_consulta_sql(conexao, sql)
    print("Tabela 'clientes' criada!")


def criar_tabela_carros(conexao):
    """Cria a tabela de carros."""
    sql = """
    CREATE TABLE IF NOT EXISTS carros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modelo TEXT NOT NULL,
        ano INTEGER,
        cor TEXT,
        placa TEXT NOT NULL UNIQUE,
        cliente_id INTEGER,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)            
        )
    """
    executar_consulta_sql(conexao, sql)
    print("Tabela 'carros' criada!")

def criar_tabela_clientes_carros(conexao):
    """Cria a tabela de relacionamento clientes_carros."""
    sql = """
    CREATE TABLE IF NOT EXISTS clientes_carros (
        cliente_id INTEGER,
        carro_id INTEGER,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (carro_id) REFERENCES carros(id),
        PRIMARY KEY (cliente_id, carro_id)
        )
    """
    executar_consulta_sql(conexao, sql)
    print("Tabela 'clientes_carros' criada!")


def criar_tabela_movimentacao_pecas(conexao):
    """Cria a tabela de movimentação de peças."""
    sql = """
    CREATE TABLE IF NOT EXISTS movimentacao_pecas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        peca_id INTEGER NOT NULL,
        data_movimentacao DATETIME DEFAULT CURRENT_TIMESTAMP,
        tipo_movimentacao TEXT NOT NULL CHECK (tipo_movimentacao IN ('entrada', 'saida')),
        quantidade INTEGER NOT NULL,
        ordem_servico_id INTEGER, 
        FOREIGN KEY (peca_id) REFERENCES pecas(id),
        FOREIGN KEY (ordem_servico_id) REFERENCES ordem_servico(id)
    )
    """
    executar_consulta_sql(conexao, sql)
    print("Tabela 'movimentacao_pecas' criada!")


def criar_tabela_servicos(conexao):
    """Cria a tabela de serviços."""
    sql = """
    CREATE TABLE IF NOT EXISTS servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        carro_id INTEGER NOT NULL,
        valor_total REAL,
        FOREIGN KEY (carro_id) REFERENCES carros(id)
        )
    """
    executar_consulta_sql(conexao, sql)
    print("Tabela 'servicos' criada!")


def criar_tabela_pecas_utilizadas(conexao):
    """Cria a tabela de peças utilizadas em serviços."""
    sql = """
        CREATE TABLE IF NOT EXISTS pecas_utilizadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servico_id INTEGER NOT NULL,
            peca_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            valor_unitario REAL NOT NULL,
            FOREIGN KEY (servico_id) REFERENCES servicos(id),
            FOREIGN KEY (peca_id) REFERENCES pecas(id)
);
        """
    executar_consulta_sql(conexao, sql)
    print("Tabela 'pecas_utilizadas' criada!")


def criar_tabela_pecas(conexao):
    """Cria a tabela de peças."""
    sql = """
        CREATE TABLE IF NOT EXISTS pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            referencia TEXT NOT NULL,
            fabricante TEXT,
            descricao TEXT,
            preco_compra REAL NOT NULL,
            preco_venda REAL NOT NULL,
            quantidade_em_estoque INTEGER NOT NULL CHECK (quantidade_em_estoque >= 0)
        )
    """
    executar_consulta_sql(conexao, sql)
    print("Tabela 'pecas' criada!")


def criar_tabela_ordem_servico(conexao):
    """Cria a tabela de ordens de serviço."""
    sql = """
        CREATE TABLE IF NOT EXISTS ordem_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            carro_id INTEGER NOT NULL,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            valor_total REAL NOT NULL,
            mao_de_obra REAL,  -- <<<--- Coluna 'mao_de_obra' adicionada
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (carro_id) REFERENCES carros(id)
        )
    """
    executar_consulta_sql(conexao, sql)
    print("Tabela 'ordem_servico' criada!")


def criar_tabela_pecas_ordem_servico(conexao):
    """Cria a tabela de relacionamento entre peças e ordens de serviço."""
    sql = """
        CREATE TABLE IF NOT EXISTS PecasOrdemServico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ordem_servico_id INTEGER,
            peca_id INTEGER,
            quantidade INTEGER NOT NULL,
            FOREIGN KEY (ordem_servico_id) REFERENCES OrdensDeServico (id),
            FOREIGN KEY (peca_id) REFERENCES Pecas (id)
        )
    """
    executar_consulta_sql(conexao, sql)
    print("Tabela 'PecasOrdemServico' criada!")


def criar_tabelas(conexao):
    """Cria todas as tabelas do banco de dados."""
    criar_tabela_usuarios(conexao)
    criar_tabela_clientes(conexao)
    criar_tabela_carros(conexao)
    criar_tabela_clientes_carros(conexao)
    criar_tabela_movimentacao_pecas(conexao)
    criar_tabela_servicos(conexao)
    criar_tabela_pecas_utilizadas(conexao)
    criar_tabela_pecas(conexao)
    criar_tabela_ordem_servico(conexao)
    criar_tabela_pecas_ordem_servico(conexao)
    criar_usuario_admin(conexao)


def inserir_dados_iniciais(conexao):
    """Insere dados iniciais no banco de dados."""
    cursor = conexao.cursor()

    cursor.execute("INSERT INTO clientes (nome) VALUES ('João Silva')")
    cursor.execute("INSERT INTO clientes (nome) VALUES ('Maria Oliveira')")

    cursor.execute(
        "INSERT INTO carros (cliente_id, modelo, placa) VALUES (1, 'Carro do batman', 'ABC-1234')"
    )
    cursor.execute(
        "INSERT INTO carros (cliente_id, modelo, placa) VALUES (2, 'Motoloca', 'DEF-5678')"
    )

    cursor.execute(
        "INSERT INTO pecas (nome, preco_compra, preco_venda, quantidade_em_estoque) VALUES ('Teste 1r', 50.00, 60.00, 100)"
    )
    cursor.execute(
        "INSERT INTO pecas (nome, preco_compra, preco_venda, quantidade_em_estoque) VALUES ('Teste 2', 20.00, 30.00, 50)"
    )
    cursor.execute(
        "INSERT INTO pecas (nome, preco_compra, preco_venda, quantidade_em_estoque) VALUES ('Teste3', 80.00, 90.00, 30)"
    )

    conexao.commit()
    print("Dados iniciais inseridos com sucesso!")


def obter_clientes(conexao):
    """Retorna uma lista de todos os clientes."""
    with criar_conexao_banco_de_dados(banco_de_dados) as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM clientes")
        return cursor.fetchall()


def obter_carros_por_cliente(conexao, cliente_id):
    """Retorna uma lista de carros de um cliente específico."""
    with criar_conexao_banco_de_dados(banco_de_dados) as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM carros WHERE cliente_id = ?", (cliente_id,))
        return cursor.fetchall()


def obter_pecas(conexao):
    """Retorna uma lista de todas as peças."""
    with criar_conexao_banco_de_dados(banco_de_dados) as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM pecas")
        return cursor.fetchall()


def inserir_ordem_servico(
    conexao, cliente_id, carro_id, pecas_quantidades, valor_total, mao_de_obra=0.00
):
    """
    Insere uma nova ordem de serviço no banco de dados.

    Args:
        conexao: A conexão com o banco de dados SQLite.
        cliente_id (int): O ID do cliente.
        carro_id (int): O ID do carro.
        pecas_quantidades (dict): Dicionário com ID da peça como chave 
                                e quantidade como valor.
        valor_total (float): Valor total da ordem de serviço.
        mao_de_obra (float, optional): Valor da mão de obra. Default: 0.00.

    Returns:
        int: ID da ordem de serviço criada ou None em caso de erro.
    """
    try:
        cursor = conexao.cursor()
        cursor.execute(
            """
            INSERT INTO ordem_servico (cliente_id, carro_id, data_criacao, valor_total, mao_de_obra)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                cliente_id,
                carro_id,
                datetime.now(),
                valor_total,
                mao_de_obra,
            ),
        )
        conexao.commit()

        ordem_servico_id = cursor.lastrowid

        for peca_id, quantidade in pecas_quantidades.items():
            cursor.execute(
                """
                INSERT INTO PecasOrdemServico (ordem_servico_id, peca_id, quantidade)
                VALUES (?, ?, ?)
                """,
                (ordem_servico_id, peca_id, quantidade),
            )
        conexao.commit()

        print(f"Ordem de serviço {ordem_servico_id} inserida com sucesso!")
        return ordem_servico_id

    except sqlite3.Error as e:
        print(f"Erro ao inserir ordem de serviço: {e}")
        conexao.rollback()
        return None


def atualizar_estoque_peca(conexao, peca_id, quantidade_utilizada):
    """
    Atualiza o estoque de uma peça.

    Args:
        conexao: A conexão com o banco de dados SQLite.
        peca_id (int): O ID da peça a ser atualizada.
        quantidade_utilizada (int): Quantidade utilizada da peça (valor negativo 
                                    para saída do estoque).
    """
    try:
        with criar_conexao_banco_de_dados(banco_de_dados) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                """
                UPDATE pecas
                SET quantidade_em_estoque = quantidade_em_estoque + ? 
                WHERE id = ?
                """,
                (quantidade_utilizada, peca_id),
            )
            conexao.commit()
            print(
                f"Estoque da peça {peca_id} atualizado. Quantidade utilizada: {quantidade_utilizada}"
            )

    except Exception as e:
        print(f"Erro ao atualizar o estoque da peça: {e}")


def atualizar_carro(carro_id, cliente_id, conexao=None):
    """
    Atualiza o dono de um carro no banco de dados.

    Args:
        carro_id (int): ID do carro a ser atualizado.
        cliente_id (int): ID do novo dono do carro.
        conexao (opcional): Conexão existente com o banco de dados.
                            Se None, uma nova conexão será criada e fechada 
                            dentro da função.

    Returns:
        bool: True se a atualização for bem-sucedida, False caso contrário.
    """
    fechar_conexao = False
    if conexao is None:
        conexao = criar_conexao_banco_de_dados(nome_banco_de_dados)
        fechar_conexao = True

    try:
        cursor = conexao.cursor()
        cursor.execute(
            "UPDATE carros SET cliente_id = ? WHERE id = ?", (cliente_id, carro_id)
        )
        conexao.commit()
        return True
    except Exception as e:
        print(f"Erro ao atualizar o carro no banco de dados: {e}")
        return False
    finally:
        if fechar_conexao:
            conexao.close()


def quantidade_em_estoque_suficiente(conexao, peca_id, quantidade_necessaria):
    """
    Verifica se a quantidade em estoque é suficiente para a peça.

    Args:
        conexao: Conexão com o banco de dados SQLite.
        peca_id (int): ID da peça.
        quantidade_necessaria (int): Quantidade necessária da peça.

    Returns:
        bool: True se a quantidade em estoque for suficiente, False caso contrário.
    """
    try:
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT quantidade_em_estoque FROM pecas WHERE id = ?", (peca_id,)
        )
        resultado = cursor.fetchone()

        if resultado is None:
            print(f"Peça com ID {peca_id} não encontrada.")
            return False

        quantidade_em_estoque = resultado[0]
        return quantidade_em_estoque >= quantidade_necessaria

    except Exception as e:
        print(f"Erro ao verificar a quantidade em estoque: {e}")
        return False


def inserir_movimentacao_peca(
    conexao, peca_id, tipo_movimentacao, quantidade, ordem_servico_id
):
    """
    Insere uma nova movimentação de peça no banco de dados.

    Args:
        conexao: Conexão com o banco de dados SQLite.
        peca_id (int): ID da peça.
        tipo_movimentacao (str): 'entrada' ou 'saida'.
        quantidade (int): Quantidade da peça movimentada.
        ordem_servico_id (int, optional): ID da ordem de serviço relacionada, se houver.
    """
    try:
        cursor = conexao.cursor()
        cursor.execute(
            """
            INSERT INTO movimentacao_pecas (peca_id, tipo_movimentacao, quantidade, ordem_servico_id)
            VALUES (?, ?, ?, ?)
            """,
            (peca_id, tipo_movimentacao, quantidade, ordem_servico_id),
        )
        conexao.commit()
        print(
            f"Movimentação da peça {peca_id} ({tipo_movimentacao}, {quantidade}) inserida com sucesso!"
        )
    except Exception as e:
        print(f"Erro ao inserir movimentação da peça: {e}")


if __name__ == "__main__":
    conexao = criar_conexao_banco_de_dados(nome_banco_de_dados)
    if conexao is not None:
        criar_tabelas(conexao)
        inserir_dados_iniciais(conexao)
        conexao.close()