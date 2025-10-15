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
| **Onboarding Inteligente** | ✅ | Guia o novo usuário na configuração inicial da oficina. |
| **Gestão de Clientes** | ✅ | CRUD completo, com busca e gerenciamento de status (ativo/inativo). |
| **Gerenciamento de Carros** | ✅ | CRUD completo de veículos, associados aos seus proprietários. |
| **Controle de Peças/Estoque** | ✅ | CRUD completo de peças, base para o controle de inventário. |
| **Gestão de Mecânicos** | ✅ | CRUD completo para gerenciar os profissionais da oficina. |
| **Gestão de Serviços** | ✅ | CRUD completo para gerenciar serviços e "kits" de peças. |
| **Gestão Administrativa** | 🚧 | CRUDs de Usuários, Minha Conta e Estabelecimento. |
| **Ordem de Serviço Completa** | 🚧 | Abertura e inclusão de peças/serviços. |

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

### **FASE 1: Estrutura e Cadastros Base (Concluída)**
* ✅ **Issues #1, #2:** Refatoração Arquitetural para MVVM.
* ✅ **Issue #8:** CRUD de Clientes.
* ✅ **Issue #16:** CRUD de Carros.
* ✅ **Issue #18:** CRUD de Peças.
* ✅ **Issue #20:** CRUD de Mecânicos.

### **FASE 2: Módulos Administrativos (Em Andamento)**
* ✅ **Issue #21: CRUD de Serviços (Concluído)**
* 🚧 **CRUD de Minha Conta:** Permitir que o usuário logado altere seus próprios dados.
* 🚧 **CRUD de Usuários:** Gerenciamento de contas de acesso ao sistema.
* 🚧 **CRUD de Estabelecimento:** Gerenciar dados da oficina (logo, chave PIX).

### **FASE 3: Módulos Operacionais (Planejado)**
* ⏳ **Entrada de Peças:** Registrar a compra de novas peças.
* ⏳ **Saída de Peças Avulsa:** Registrar a venda de peças fora de uma OS.
* ⏳ **Criação de Ordem de Serviço (OS):** Módulo central da aplicação.

### **FASE 4: Inteligência e Relatórios (Planejado)**
* ⏳ **Geração de Relatórios:** Módulo para gerar relatórios diversos.
* ⏳ **Sistema de Alertas de Manutenção:** Notificações sobre revisões futuras.

### **FASE 5: Funcionalidades Futuras (Planejado)**
* ⏳ **Modernização da Autenticação:** Login com Google (Firebase Auth).
* ⏳ **Sincronização na Nuvem:** Backup e sincronia via Firebase Firestore.
* ⏳ **Pipeline de Build:** Geração de executáveis (.exe) e pacotes (.apk).

## **👨‍💻 Desenvolvedores**

| <img src="https://avatars.githubusercontent.com/u/15948634?v=4" width=115> <sub>Gleyson Atanázio</sub> | <img src="https://avatars.githubusercontent.com/u/108997883?v=4" width=115> <sub>Vanderson</sub> | <img src="https://avatars.githubusercontent.com/u/89957139?v=4" width=115> <sub>Rudimacy Duprat</sub> |
| :--- | :--- | :--- |

<p align="center"> ⌨️ com 💜 por Gleyson Atanázio, Vanderson e Rudimacy Duprat </p>