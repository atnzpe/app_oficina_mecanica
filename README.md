# **OS - Sistema de Gestão para Oficina Mecânica 🚗🔧**

<p align="center">  
<img src="https://raw.githubusercontent.com/atnzpe/app_oficina_mecanica/main/assets/ico.png" alt="Logotipo do Projeto" width="250"/>  
</p>  
<p align="center">  
<img src="https://img.shields.io/badge/Plataforma-Desktop%20%7C%20Android-brightgreen?logo=android" alt="Plataforma">  
<img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python Version">  
<img src="https://img.shields.io/badge/Flet-Cross--Platform-green?logo=flutter" alt="Flet Framework">  
<img src="https://img.shields.io/badge/Status-Est%C3%A1vel%20(MVP)-blue" alt="Project Status">  
</p>

## **📄 Descrição**

O **Projeto OS** é uma solução multiplataforma (**Desktop Windows** e **Android**) para gestão de oficinas mecânicas, desenvolvida em Python com o framework Flet. O sistema foi projetado com uma arquitetura **Offline-First**, garantindo total funcionalidade mesmo sem conexão com a internet, tornando-o robusto e confiável para o dia a dia da oficina.

Ele oferece um controle completo sobre o fluxo de trabalho, desde o cadastro de clientes e veículos até a criação de Ordens de Serviço (OS), controle de estoque e geração de relatórios.

## **✨ Funcionalidades Principais**

| Funcionalidade | Status | Detalhes |
| :--- | :--- | :--- |
| **Arquitetura MVVM Robusta** | ✅ | O código está 100% refatorado, separando UI, lógica e dados. |
| **Fluxo de Autenticação Seguro** | ✅ | Cadastro do 1º admin, login com bcrypt, e navegação por rotas. |
| **Onboarding Inteligente** | ✅ | Guia o novo usuário na configuração inicial completa da oficina. |
| **Gestão de Clientes** | ✅ | CRUD completo, com busca e gerenciamento de status (ativo/inativo). |
| **Gerenciamento de Carros** | ✅ | CRUD completo de veículos, associados aos seus proprietários. |
| **Controle de Peças/Estoque** | ✅ | CRUD completo de peças, base para o controle de inventário. |
| **Gestão de Mecânicos** | ✅ | CRUD completo para gerenciar os profissionais da oficina. |
| **Gestão de Serviços** | ✅ | CRUD completo para gerenciar serviços e "kits" de peças. |
| **Gestão de Conta de Usuário** | ✅ | Permite ao usuário logado alterar a própria senha. |
| **Gestão do Estabelecimento** | ✅ | Permite ao admin configurar/editar os dados da oficina (PIX, Endereço, etc). |
| **Entrada de Peças em Lote** | ✅ | Entrada transacional no estoque com histórico de movimentações. |
| **Consulta de Estoque / Venda de Peças** | ⏳ | Rotas existem no dashboard, mas ainda são placeholders. |
| **Ordem de Serviço Completa** | 🚧 | Tabelas e query base existem; falta a tela roteada, serviços na OS e baixa de estoque. |
| **Relatórios em PDF** | 🐞 | `report_service.py` legado precisa ser corrigido e integrado a uma tela. |
| **Gestão Administrativa** | ⏳ | CRUD de Usuários e controle de acesso por perfil. |

## **🏛️ Arquitetura e Conceitos Chave**

Este projeto foi construído sobre princípios modernos de desenvolvimento de software para garantir escalabilidade, segurança e uma ótima experiência de usuário.

* **Arquitetura Offline-First (SQLite):** O coração da aplicação é um banco de dados **SQLite local** (database.db). Todas as operações são executadas diretamente neste banco de dados, garantindo que o sistema seja **100% funcional sem conexão com a internet**.
* **Padrão MVVM (Model-View-ViewModel):** O código está estritamente estruturado no padrão MVVM, que separa claramente as responsabilidades:
    * **Model:** As classes de dados (`models/`) e a camada de acesso ao banco (`database/`).
    * **View:** Os componentes visuais da UI (`views/`).
    * **ViewModel:** O "cérebro" da UI, contendo a lógica e o estado (`viewmodels/`).

<details> <summary><strong>Clique para ver a Estrutura de Arquivos</strong></summary>

src/
├── models/             # MODEL: Classes de dados
├── database/           # MODEL: Lógica de conexão e acesso a dados
├── views/              # VIEW: Componentes visuais da UI
├── viewmodels/         # VIEWMODEL: Lógica e estado da UI
├── services/           # SERVIÇOS: Lógica de negócio desacoplada
└── styles/             # ESTILOS: Constantes de design

</details>

## **🛠️ Tecnologias Utilizadas**

| Tecnologia | Propósito |
| :--- | :--- |
| **Python 3.10+** | Linguagem principal do projeto. |
| **Flet** | Framework para construção da interface gráfica para Desktop e Android. |
| **SQLite3** | Banco de dados relacional local para a funcionalidade offline. |
| **Bcrypt** | Biblioteca para hashing seguro de senhas locais. |
| **FPDF** | Biblioteca para geração de relatórios em PDF. |
| **Firebase (Firestore/Auth)** | (Planejado) Serviços de nuvem para sincronização e autenticação. |

## **🚀 Como Executar o Projeto**

Siga os passos abaixo para configurar e rodar a aplicação em seu ambiente de desenvolvimento.

1.  **Clone o Repositório:** `git clone https://github.com/atnzpe/app_oficina_mecanica.git`
2.  **Crie e Ative um Ambiente Virtual:** `python -m venv venv` e `.\venv\Scripts\activate` (Windows)
3.  **Instale as Dependências:** `pip install -r requirements.txt`
4.  **Execute a Aplicação:** `flet run main.py`

## **🗺️ Roadmap do Projeto**

Nosso roadmap é gerenciado através das [**Issues do GitHub**](https://github.com/atnzpe/app_oficina_mecanica/issues).
Legenda: ✅ Concluído · 🚧 Em andamento · ⏳ Planejado · 🐞 Débito técnico / correção

### **FASE 1: Estrutura e Cadastros Base (Concluída)**
* ✅ **Issues #1, #2:** Refatoração Arquitetural para MVVM.
* ✅ **Issue #8:** CRUD de Clientes.
* ✅ **Issue #16:** CRUD de Carros.
* ✅ **Issue #18:** CRUD de Peças.
* ✅ **Issue #20:** CRUD de Mecânicos.

### **FASE 2: Módulos Administrativos (Concluída)**
* ✅ **Issue #21:** CRUD de Serviços (com "kit" de peças).
* ✅ **Issue #29:** Minha Conta (alteração de senha + log de auditoria).
* ✅ **Issue #30:** CRUD de Estabelecimento (dados da oficina, PIX e logo).

### **FASE 3: Módulos Operacionais (Em Andamento)**
* ✅ **Issue #32:** Entrada de Peças em lote (transacional, com `movimentacao_pecas`).
* ⏳ **Consulta de Estoque (`/estoque`):** Listagem do saldo atual, alerta de estoque mínimo e histórico de movimentações por peça.
* ⏳ **Saída de Peças Avulsa / Venda de Peças (`/venda_pecas`):** Baixa no estoque com registro de `saida` em `movimentacao_pecas`, validando saldo disponível.
* ⏳ **Ordem de Serviço (`/nova_os`)** — módulo central. Subtarefas:
    * Evoluir a tabela `ordem_servico`: `status` (aberta, em andamento, concluída, cancelada), `mecanico_id`, `km`, `observacoes`, `desconto`, `forma_pagamento`, `data_conclusao`.
    * Criar tabela `ServicosOrdemServico` (serviços executados na OS) e aplicar o "kit" de peças do serviço automaticamente.
    * Baixar o estoque e registrar a `saida` em `movimentacao_pecas` dentro da **mesma transação** de criação/conclusão da OS.
    * Reescrever `os_formulario_view`/`os_formulario_viewmodel` como View Factory roteada (hoje é um modal legado, sem rota).
    * Telas de listagem/consulta de OS (por cliente, veículo, status) e edição/cancelamento com estorno de estoque.
* ⏳ **Orçamento (`/novo_orcamento`):** OS em status "orçamento" (não movimenta estoque), com conversão em OS.
* ⏳ **Impressão/Compartilhamento da OS em PDF:** Com logo, dados da oficina e QR Code/chave PIX.

### **FASE 4: Inteligência e Relatórios (Planejado)**
* 🐞 **Corrigir `report_service.py`:** Importa funções que não existem mais em `database.py` (`criar_conexao_banco_de_dados`, etc.) e usa `os.startfile` (só Windows). Migrar para `get_db_connection()` e uma única biblioteca de PDF (hoje há `fpdf` **e** `reportlab`).
* ⏳ **Tela de Relatórios (`/relatorios`):** OS por período/cliente, saldo e movimentação de estoque, faturamento (peças x mão de obra), serviços mais vendidos.
* ⏳ **Dashboard com indicadores:** OS abertas, faturamento do mês, peças abaixo do estoque mínimo.
* ⏳ **Histórico do Veículo:** Linha do tempo de OS por placa.
* ⏳ **Sistema de Alertas de Manutenção:** Revisões futuras por data/KM.

### **FASE 5: Qualidade, Segurança e Débito Técnico (Contínua)**
* 🐞 **Issue #3:** Gestão centralizada da conexão com o banco (hoje cada query abre/fecha sua conexão; a `fila_db` só trata `criar_ordem_servico`).
* ⏳ **Testes automatizados:** Criar `tests/` com `pytest` (queries com SQLite em memória/arquivo temporário, services e viewmodels com `page` mockada).
* ⏳ **CI (GitHub Actions):** Lint (`ruff`) + testes a cada PR.
* ⏳ **Migrações de schema versionadas:** Hoje só há `CREATE TABLE IF NOT EXISTS`; colunas novas não chegam a bancos já existentes (usar `PRAGMA user_version` + scripts `ALTER TABLE`).
* ⏳ **Controle de acesso por perfil:** O campo `usuarios.perfil` (admin/mecânico) existe, mas nenhuma rota o verifica; também não há guarda de rota para usuário não autenticado.
* ⏳ **Higiene do repositório:** Remover `data/database.db` do versionamento (adicionar ao `.gitignore`), fixar versões no `requirements.txt` (ou migrar para `pyproject.toml`) e remover `src/obsolet/`.
* ⏳ **Backup/Restauração local:** Exportar/importar o `database.db` (pasta `backup/` já é criada por `utils.criar_pastas`).

### **FASE 6: Funcionalidades Futuras (Planejado)**
* ⏳ **Issue #7:** Pipeline de Build — `flet build windows` / `flet build apk` e documentação do processo.
* ⏳ **Issue #6:** Modernização da Autenticação — Login com Google (Firebase Auth).
* ⏳ **Issue #5:** Sincronização na Nuvem — Backup e sincronia via Firebase Firestore (Offline-First).
* ⏳ **CRUD de Usuários (`/usuarios`):** Gerenciamento de contas de acesso (Admin, Mecânico) — rota já prevista e comentada em `main.py`.

## **👨‍💻 Desenvolvedores**

| <img src="https://avatars.githubusercontent.com/u/15948634?v=4" width=115> <sub>Gleyson Atanázio</sub> | <img src="https://avatars.githubusercontent.com/u/108997883?v=4" width=115> <sub>Vanderson</sub> | <img src="https://avatars.githubusercontent.com/u/89957139?v=4" width=115> <sub>Rudimacy Duprat</sub> |
| :--- | :--- | :--- |

<p align="center"> ⌨️ com 💜 por Gleyson Atanázio, Vanderson e Rudimacy Duprat </p>