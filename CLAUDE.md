# CLAUDE.md

Guia para agentes de IA (Claude Code) trabalharem neste repositório.
**Responda e escreva sempre em português (pt-BR)** — código, comentários, logs, commits e documentação.

## Visão Geral

Sistema de gestão para oficina mecânica (Ordens de Serviço, estoque, clientes, veículos),
em **Python 3.10+ com Flet**, alvo **Desktop Windows e Android**, arquitetura **Offline-First**
com **SQLite local** (`data/database.db`).

## Como Executar

```bash
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\activate
pip install -r requirements.txt # flet, bcrypt, reportlab, fpdf
flet run main.py                # ou: python main.py
```

- Não há testes automatizados nem CI ainda (ver Roadmap no README, Fase 5).
- Checagem rápida de sintaxe/imports sem abrir a UI: `python -m compileall -q src main.py`.
- O schema é criado em `initialize_database()` no início do app (`CREATE TABLE IF NOT EXISTS`).

## Arquitetura (MVVM)

```
main.py                 # Entrada: temas, init do DB, thread da fila, roteador (route_change)
utils.py                # criar_pastas(): historico, data, report, orcamento, backup, assets/uploads
src/
├── models/models.py    # Dataclasses: Estabelecimento, Usuario, Mecanico, Cliente, Carro, Peca, Servico, MovimentacaoPeca
├── database/
│   ├── database.py     # get_db_connection(), CREATE_TABLES_SQL, initialize_database(), fila_db
│   └── queries.py      # TODAS as queries SQL (funções por entidade)
├── services/
│   ├── auth_service.py        # bcrypt: register_user, authenticate_user, alterar_senha
│   ├── task_queue_service.py  # thread que consome fila_db (só "criar_ordem_servico" hoje)
│   └── report_service.py      # LEGADO/QUEBRADO (imports inexistentes) — não usar sem corrigir
├── viewmodels/         # Lógica/estado de cada tela (<nome>_viewmodel.py)
├── views/              # UI Flet (<nome>_view.py) + <Nome>ViewFactory(page) -> ft.View
├── styles/style.py     # AppThemes (claro/escuro), success_color_scheme
└── obsolet/            # Código antigo apenas para consulta — não importar
```

### Padrão de uma tela

1. `src/viewmodels/<tela>_viewmodel.py`: classe `<Tela>ViewModel(page)` com `vincular_view(view)`;
   chama `queries.*`/`services.*` e comanda a View (ex.: `self._view.mostrar_feedback_snackbar(...)`).
   Nunca monta controles Flet complexos.
2. `src/views/<tela>_view.py`: classe `<Tela>View(ft.Column)` que cria o ViewModel, faz
   `view_model.vincular_view(self)` e expõe métodos de atualização da UI; carrega dados em `did_mount()`.
   Termina com `def <Tela>ViewFactory(page: ft.Page) -> ft.View` (AppBar + SafeArea).
3. Registrar a rota em `main.py` → `route_change` (rotas de edição usam regex, ex.: `/editar_peca/(\d+)`).
4. Adicionar o atalho no card correspondente de `src/views/dashboard_view.py` (`_criar_sub_item`).

Convenções de nomes: `gerir_<entidade>` (listagem/busca/ativar-desativar), `cadastro_<entidade>`,
`editar_<entidade>`. Rotas ainda em placeholder: `/nova_os`, `/novo_orcamento`, `/venda_pecas`,
`/estoque`, `/relatorios`; `/usuarios` está comentada.

### Banco de Dados

- Sempre use `get_db_connection()` (ativa `PRAGMA foreign_keys = ON` e `row_factory = sqlite3.Row`).
  Cada função em `queries.py` abre, faz `commit`/`rollback` e fecha a conexão no `finally`.
- Operações com várias escritas devem ser **transacionais**: funções auxiliares recebem o `cursor`
  (ex.: `atualizar_estoque_peca(..., cursor)`, `inserir_movimentacao_peca(..., cursor)`),
  veja `registrar_entrada_estoque_lote` como referência.
- Toda alteração de estoque deve gravar em `movimentacao_pecas` (`tipo_movimentacao` = `entrada`|`saida`).
- Exclusão é **lógica** (`ativo = 0`) via `desativar_*_por_id` / `ativar_*_por_id`.
- Datas são `TEXT` no formato `"%Y-%m-%d %H:%M:%S"`.
- Não há migrações: `CREATE TABLE IF NOT EXISTS` **não** adiciona colunas em bancos existentes.
  Ao mudar o schema, trate a migração (ex.: `ALTER TABLE` condicionado a `PRAGMA table_info`) ou documente.
- `data/database.db` está versionado por engano — não faça commit de alterações nele.

### Sessão e Segurança

- Usuário logado: `page.session.get("usuario_logado")` (objeto `Usuario`, setado no `LoginViewModel`).
- Senhas só via `auth_service` (bcrypt). Ações sensíveis → `queries.registrar_log_auditoria(...)`.
- Fluxo inicial: sem usuários → `/register`; senão `/login`; sem estabelecimento → `/onboarding`.

## Regras de Desenvolvimento

- **Mudanças mínimas**: altere só o necessário e preserve nomes/maiúsculas existentes.
- **Comentários e docstrings** em português, didáticos (o projeto é lido por QA e estagiários);
  cada arquivo começa com cabeçalho `# MÓDULO ... (arquivo.py)` descrevendo objetivo/atualização.
- **Logging** em vez de `print`: `logger = logging.getLogger(__name__)`, registrando cada passo
  relevante (`info` para fluxo, `debug` para detalhes, `error(..., exc_info=True)` em exceções).
- Use `ft.Colors` / `ft.Icons` (API atual do Flet) e as cores do tema em `style.py`.
- Evite código específico de SO (ex.: `os.startfile`) — o app também roda em Android.
- Ao criar testes, use `pytest` em `tests/`, apontando o banco para um arquivo temporário
  (monkeypatch de `src.database.database.NOME_BANCO_DE_DADOS`).

## Git / GitHub

- Gitflow: branches `feat/...`, `fix/...`, `refactor/...` a partir de `develop`/`main`; PRs para `main`.
- Commits no padrão Conventional Commits em português, com escopo e issue:
  `feat(estoque): Implementa Entrada de Peças em Lote (Issue #32)`.
- Ao concluir uma funcionalidade, atualize a tabela de funcionalidades e o **Roadmap do README.md**.

## Próximos Passos Prioritários

Detalhados no Roadmap do `README.md`. Em resumo:
1. Consulta de Estoque (`/estoque`) e Venda/Saída de Peças (`/venda_pecas`).
2. Ordem de Serviço completa (status, mecânico, serviços, baixa de estoque transacional) e Orçamento.
3. Corrigir `report_service.py` e criar a tela de Relatórios.
4. Débito técnico: testes + CI, migrações de schema, controle de acesso por perfil, Issue #3.
5. Build Windows/Android (Issue #7), Firebase Auth/Sync (Issues #6, #5), CRUD de Usuários.
