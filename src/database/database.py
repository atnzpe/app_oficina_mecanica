# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DE GERENCIAMENTO DO BANCO DE DADOS (database.py)
#
# OBJETIVO: Centralizar toda a lógica de conexão e criação do esquema (estrutura)
#           do banco de dados SQLite para a aplicação da oficina mecânica.
#
# VERSÃO ATUAL: Integra a lógica de conexão aprimorada fornecida, incluindo a
#              ativação de chaves estrangeiras (foreign keys) para maior
#              integridade dos dados.
# =================================================================================

# --- IMPORTAÇÕES DE BIBLIOTECAS ---

# Importa a biblioteca 'sqlite3', que é a interface padrão do Python para
# trabalhar com bancos de dados SQLite.
import sqlite3

# Importa a biblioteca 'logging' para registrar mensagens de status, avisos e erros.
# É uma prática muito superior ao uso de 'print()'.
import logging

# Importa a biblioteca 'os' para interagir com o sistema operacional,
# principalmente para manipular caminhos de arquivos de forma segura.
import os

# Importa a biblioteca 'queue' para criar a fila de tarefas assíncronas.
import queue

# --- CONFIGURAÇÃO GLOBAL E INICIALIZAÇÃO DO LOGGER ---

# Configura o sistema de logging para exibir mensagens com um formato padrão.
# Isso inclui a data/hora, o nível da mensagem (INFO, ERROR, etc.), o nome do logger
# e a mensagem em si.
logging.basicConfig(
    level=logging.INFO,  # Define o nível mínimo de mensagens a serem exibidas.
    format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
)
# Cria uma instância específica de logger para este módulo.
# Isso ajuda a identificar a origem das mensagens de log.
logger = logging.getLogger(__name__)

# --- DEFINIÇÃO DE CONSTANTES ---

# Define o nome da pasta onde o banco de dados será armazenado.
DB_FOLDER = "./data"
# Define o nome do arquivo do banco de dados.
DB_FILE = "database.db"
# Junta a pasta e o nome do arquivo para criar um caminho completo e seguro
# que funciona em qualquer sistema operacional (Windows, Linux, macOS).
NOME_BANCO_DE_DADOS = os.path.join(DB_FOLDER, DB_FILE)

# Cria uma fila global que será usada para processar operações de banco de dados
# de forma assíncrona (em uma thread separada), evitando que a interface do usuário trave.
fila_db = queue.Queue()

# --- FUNÇÃO DE CONEXÃO AO BANCO DE DADOS ---


def get_db_connection() -> sqlite3.Connection | None:
    """
    Cria e retorna um objeto de conexão com o banco de dados SQLite.

    Esta é a função central e única para obter uma conexão com o banco.
    Ela encapsula toda a lógica de criação de diretório, conexão e configuração.

    :return: Um objeto de conexão (sqlite3.Connection) em caso de sucesso,
             ou None em caso de falha.
    """
    # Log para registrar o início da tentativa de conexão.
    logger.debug(
        f"Tentando estabelecer conexão com o banco de dados em: {NOME_BANCO_DE_DADOS}"
    )
    try:
        # Garante que o diretório onde o banco de dados será salvo exista.
        # os.path.dirname(NOME_BANCO_DE_DADOS) -> obtém o nome do diretório ('./data')
        # os.makedirs(..., exist_ok=True) -> cria o diretório se ele não existir.
        os.makedirs(os.path.dirname(NOME_BANCO_DE_DADOS), exist_ok=True)
        logger.debug(f"Diretório '{DB_FOLDER}' verificado/criado com sucesso.")

        # Tenta conectar ao arquivo do banco de dados.
        # Se o arquivo não existir, o SQLite o criará automaticamente.
        conn = sqlite3.connect(NOME_BANCO_DE_DADOS)
        logger.debug("Conexão física com o arquivo do banco de dados estabelecida.")

        # Configura a conexão para que as linhas retornadas se comportem como dicionários.
        # Isso permite acessar colunas pelo nome (ex: row['nome']) em vez de índice (ex: row[1]),
        # tornando o código muito mais legível e menos propenso a erros.
        conn.row_factory = sqlite3.Row
        logger.debug("Row factory da conexão configurada para sqlite3.Row.")

        # Habilita a imposição de chaves estrangeiras (FOREIGN KEY).
        # Este comando é CRUCIAL para a integridade dos dados. Ele garante que você
        # não possa, por exemplo, criar uma 'ordem_servico' para um 'cliente_id' que não existe.
        conn.execute("PRAGMA foreign_keys = ON;")
        logger.debug("PRAGMA foreign_keys foi ativado para esta conexão.")

        # Log de sucesso final.
        logger.info(
            f"Conexão com o banco de dados '{NOME_BANCO_DE_DADOS}' pronta para uso."
        )
        # Retorna o objeto de conexão configurado.
        return conn

    # Captura qualquer exceção que possa ocorrer durante a conexão.
    except sqlite3.Error as e:
        # Registra o erro com detalhes completos, incluindo o traceback.
        logger.critical(
            f"FALHA CRÍTICA ao conectar ao banco de dados: {e}", exc_info=True
        )
        # Retorna None para indicar que a conexão falhou.
        return None


# --- DEFINIÇÃO DA ESTRUTURA (SCHEMA) DO BANCO DE DADOS ---

# Lista contendo todos os comandos SQL para criar as tabelas da aplicação.
# Usar `CREATE TABLE IF NOT EXISTS` garante que o script não falhe se as tabelas já existirem.
CREATE_TABLES_SQL = [
    # --- NOVA TABELA ---
    # Tabela de Estabelecimentos: armazena os dados da oficina.
    """
    CREATE TABLE IF NOT EXISTS estabelecimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        endereco TEXT,
        telefone TEXT,
        responsavel TEXT,
        cpf_cnpj TEXT,
        logo_path IM,
        chave_pix TEXT
    );
    """,
    # Tabela de Usuários: agora com vínculo ao estabelecimento.
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        perfil TEXT NOT NULL CHECK (perfil IN ('admin', 'mecanico')) DEFAULT 'mecanico',
        id_estabelecimento INTEGER,
        FOREIGN KEY (id_estabelecimento) REFERENCES estabelecimentos(id)
    );
    """,
    
    #Tabela de Mecânicos: permanece a mesma, para os funcionários da oficina.
     """
    CREATE TABLE IF NOT EXISTS mecanicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT UNIQUE,
        endereco TEXT,  
        telefone TEXT,
        especialidade TEXT,
        ativo BOOLEAN DEFAULT 1
    );
    """,    
    
    # Tabela de Clientes: permanece a mesma, para os clientes da oficina.
    """
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT,
        endereco TEXT,
        email TEXT,
        ativo BOOLEAN DEFAULT 1,
        UNIQUE (nome)
    );
    """,
    # --- (As outras tabelas - carros, pecas, etc. - permanecem as mesmas) ---
    """
    CREATE TABLE IF NOT EXISTS carros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modelo TEXT NOT NULL,
        ano INTEGER,
        cor TEXT,
        placa TEXT NOT NULL UNIQUE,
        cliente_id INTEGER,
        ativo BOOLEAN DEFAULT 1,
        UNIQUE (placa),
        FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
    );
    """,
    
    # --- Tabela de Peças: permanece a mesma, para o inventário de peças.
    """
    CREATE TABLE IF NOT EXISTS pecas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        referencia TEXT NOT NULL,
        fabricante TEXT,
        descricao TEXT,
        preco_compra REAL NOT NULL,
        preco_venda REAL NOT NULL,
        quantidade_em_estoque INTEGER NOT NULL CHECK (quantidade_em_estoque >= 0),
        ativo BOOLEAN DEFAULT 1,
        UNIQUE (nome, referencia) -- Garante que a combinação de nome e referência seja única
    );
    """,
    # --- Tabela de Serviços: permanece a mesma, para os serviços oferecidos.
    """
    CREATE TABLE IF NOT EXISTS servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT,
        valor REAL NOT NULL,
        ativo BOOLEAN DEFAULT 1
    );
    """,
    # Tabela de Associação entre Serviços e Peças: permanece a mesma.
    # Permite definir quais peças são usadas em quais serviços.
    """
    CREATE TABLE IF NOT EXISTS servicos_pecas (
        servico_id INTEGER NOT NULL,
        peca_id INTEGER NOT NULL,
        PRIMARY KEY (servico_id, peca_id),
        FOREIGN KEY (servico_id) REFERENCES servicos(id) ON DELETE CASCADE,
        FOREIGN KEY (peca_id) REFERENCES pecas(id) ON DELETE CASCADE
    );
    """,
    # --- Tabela de Ordens de Serviço: permanece a mesma, para registrar os serviços realizados.
    
    
    """
    CREATE TABLE IF NOT EXISTS ordem_servico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        carro_id INTEGER NOT NULL,
        data_criacao TEXT NOT NULL,
        valor_total REAL NOT NULL,
        mao_de_obra REAL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (carro_id) REFERENCES carros(id)
    );
    """,
    # Tabela de Associação entre Ordens de Serviço e Serviços: permanece a mesma.
    # Permite registrar quais serviços foram realizados em cada ordem.
    """
    CREATE TABLE IF NOT EXISTS PecasOrdemServico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ordem_servico_id INTEGER NOT NULL,
        peca_id INTEGER NOT NULL,
        quantidade INTEGER NOT NULL,
        FOREIGN KEY (ordem_servico_id) REFERENCES ordem_servico(id),
        FOREIGN KEY (peca_id) REFERENCES pecas(id)
    );
    """,
    # Tabela de Movimentação de Peças: permanece a mesma.
    # Registra entradas e saídas de peças do estoque.
    """
    CREATE TABLE IF NOT EXISTS movimentacao_pecas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        peca_id INTEGER NOT NULL,
        data_movimentacao TEXT NOT NULL,
        tipo_movimentacao TEXT NOT NULL CHECK (tipo_movimentacao IN ('entrada', 'saida')),
        quantidade INTEGER NOT NULL,
        ordem_servico_id INTEGER,
        FOREIGN KEY (peca_id) REFERENCES pecas(id),
        FOREIGN KEY (ordem_servico_id) REFERENCES ordem_servico(id)
    );
    """,
    # Tabela de Auditoria
    # Registra ações importantes realizadas no sistema.
    """
    CREATE TABLE IF NOT EXISTS auditoria_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        acao TEXT NOT NULL,
        detalhes TEXT,
        data_hora TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
    """,
]

# --- FUNÇÃO DE INICIALIZAÇÃO DO BANCO DE DADOS ---


def initialize_database():
    """
    Executa o script de criação para todas as tabelas do banco de dados.
    Esta função deve ser chamada uma única vez na inicialização da aplicação.
    """
    # Log que marca o início do processo de setup do banco.
    logger.info("Iniciando a inicialização do esquema do banco de dados...")
    # Obtém uma conexão usando a função centralizada.
    conn = get_db_connection()

    # Verifica se a conexão falhou. Se sim, a aplicação não pode continuar.
    if conn is None:
        logger.critical(
            "NÃO FOI POSSÍVEL INICIALIZAR O BANCO DE DADOS: FALHA NA CONEXÃO."
        )
        return  # Interrompe a execução da função.

    try:
        # Cria um 'cursor', que é o objeto usado para executar comandos SQL.
        cursor = conn.cursor()
        logger.debug(
            "Cursor criado. Iniciando a execução dos comandos de criação de tabelas."
        )

        # Itera sobre a lista de comandos SQL definida anteriormente.
        for table_sql in CREATE_TABLES_SQL:
            # Log para cada tabela que está sendo criada/verificada.
            logger.debug(f"Executando comando: {table_sql.strip()}")
            # Executa o comando SQL.
            cursor.execute(table_sql)

        # Após executar todos os comandos, 'commita' as alterações.
        # Isso salva todas as criações de tabelas de uma vez.
        conn.commit()
        logger.info("Esquema do banco de dados verificado/criado com sucesso.")

    # Captura qualquer erro do SQLite que possa ocorrer durante a criação das tabelas.
    except sqlite3.Error as e:
        # Se um erro ocorrer, registra-o detalhadamente.
        logger.error(f"Ocorreu um erro ao criar as tabelas: {e}", exc_info=True)
        # E o mais importante: desfaz quaisquer alterações que possam ter sido feitas.
        # Isso garante que o banco não fique em um estado "meio criado" ou corrompido.
        conn.rollback()

    # O bloco 'finally' é sempre executado, tenha ocorrido um erro ou não.
    finally:
        # Garante que a conexão com o banco de dados seja sempre fechada.
        if conn:
            conn.close()
            logger.debug("Conexão com o banco de dados fechada após a inicialização.")


# --- BLOCO DE EXECUÇÃO PRINCIPAL ---

# Este bloco só é executado quando o arquivo é chamado diretamente pelo terminal
# (ex: `python -m src.database.database`).
# Isso permite criar e configurar o banco de dados sem precisar rodar a aplicação inteira.
if __name__ == "__main__":
    logger.info(
        "Módulo de banco de dados executado diretamente. Iniciando a inicialização."
    )
    initialize_database()
