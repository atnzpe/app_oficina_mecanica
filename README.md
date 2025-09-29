# **OS \- Sistema de Gestão para Oficina Mecânica 🚗🔧**

\<p align="center"\>  
\<img src="https://www.google.com/search?q=https://raw.githubusercontent.com/atnzpe/app\_oficina\_mecanica/main/assets/ico.png" alt="Logotipo do Projeto" width="250"/\>  
\</p\>  
\<p align="center"\>  
\<img src="https://www.google.com/search?q=https://img.shields.io/badge/Plataforma-Desktop%2520%257C%2520Android-brightgreen%3Flogo%3Dandroid" alt="Plataforma"\>  
\<img src="https://www.google.com/search?q=https://img.shields.io/badge/Python-3.10%252B-blue%3Flogo%3Dpython" alt="Python Version"\>  
\<img src="https://www.google.com/search?q=https://img.shields.io/badge/Flet-Cross--Platform-green%3Flogo%3Dflutter" alt="Flet Framework"\>  
\<img src="https://www.google.com/search?q=https://img.shields.io/badge/Status-Est%C3%A1vel%2520(MVP)-blue" alt="Project Status"\>  
\</p\>

## **📄 Descrição**

O **Projeto OS** é uma solução multiplataforma (**Desktop Windows** e **Android**) para gestão de oficinas mecânicas, desenvolvida em Python com o framework Flet. O sistema foi projetado com uma arquitetura **Offline-First**, garantindo total funcionalidade mesmo sem conexão com a internet, tornando-o robusto e confiável para o dia a dia da oficina.

Ele oferece um controle completo sobre o fluxo de trabalho, desde o cadastro de clientes e veículos até a criação de Ordens de Serviço (OS), controle de estoque e geração de relatórios.

## **✨ Funcionalidades Principais**

| Funcionalidade | Status | Detalhes |
| :---- | :---- | :---- |
| **Arquitetura MVVM Robusta** | ✅ | O código está 100% refatorado, separando UI, lógica e dados. |
| **Fluxo de Autenticação Seguro** | ✅ | Cadastro do 1º admin, login com bcrypt, e navegação por rotas. |
| **Onboarding Inteligente** | ✅ | Guia o novo usuário na configuração inicial da oficina. |
| **Prompt para Primeiro Cliente** | ✅ | Incentiva o usuário a começar a usar o sistema ativamente. |
| **Gestão de Clientes** | 🚧 | CRUD (Criar, Ler, Atualizar, Apagar) de clientes. |
| **Gerenciamento de Carros** | 🚧 | CRUD de veículos, associados aos clientes. |
| **Controle de Peças/Estoque** | 🚧 | CRUD de peças e controle de inventário. |
| **Ordem de Serviço Completa** | 🚧 | Abertura e inclusão de peças/serviços. |
| **Perfis de Acesso** | ⏳ | Diferenciação entre Admin e Mecanico. |
| **Sincronização na Nuvem** | ⏳ | Backup e recuperação de dados via Firebase. |

## **🏛️ Arquitetura e Conceitos Chave**

Este projeto foi construído sobre princípios modernos de desenvolvimento de software para garantir escalabilidade, segurança e uma ótima experiência de usuário.

* **Arquitetura Offline-First (SQLite):** O coração da aplicação é um banco de dados **SQLite local** (database.db). Todas as operações (cadastros, edições, exclusões) são executadas diretamente neste banco de dados, garantindo que o sistema seja **100% funcional sem conexão com a internet**.  
* **Sincronização na Nuvem (Firebase Firestore):** (Planejado) Para garantir o backup e a utilização em múltiplos dispositivos, um serviço de sincronização irá operar em segundo plano. Quando conectado à internet, ele enviará as alterações do banco local (SQLite) para um banco de dados **Firebase Firestore** na nuvem e buscará por atualizações externas.  
* **Recuperação de Dados via Login Google (Firebase Auth):** (Planejado) A autenticação de usuários via **Login com Google** é a chave para a portabilidade. Ao logar em um novo dispositivo, o sistema se conectará ao Firebase, identificará o usuário e fará o download de todos os dados do Firestore para a base de dados SQLite local, restaurando completamente o ambiente de trabalho do usuário.  
* **Padrão MVVM (Model-View-ViewModel):** O código está estritamente estruturado no padrão MVVM, que separa claramente as responsabilidades:  
  * **Model:** As classes de dados (models.py) e a camada de acesso ao banco (database.py, queries.py).  
  * **View:** Os componentes visuais da UI (views/).  
  * **ViewModel:** O "cérebro" da UI, contendo a lógica e o estado (viewmodels/).

\<details\> \<summary\>\<strong\>Clique para ver a Estrutura de Arquivos\</strong\>\</summary\>

src/  
├── models/             \# MODEL: Classes de dados (Cliente, Carro, etc.)  
├── database/           \# MODEL: Lógica de conexão e acesso ao banco de dados.  
├── views/              \# VIEW: Componentes visuais da UI (Flet).  
├── viewmodels/         \# VIEWMODEL: O "cérebro" da UI, com a lógica e o estado.  
├── services/           \# SERVIÇOS: Lógica desacoplada (auth, sync, reports).  
└── styles/             \# ESTILOS: Constantes de design (cores, fontes).

\</details\>

## **🛠️ Tecnologias Utilizadas**

| Tecnologia | Propósito |
| :---- | :---- |
| **Python 3.10+** | Linguagem principal do projeto. |
| **Flet** | Framework para construção da interface gráfica para Desktop e Android. |
| **SQLite3** | Banco de dados relacional local para a funcionalidade offline. |
| **Bcrypt** | Biblioteca para hashing seguro de senhas locais. |
| **FPDF** | Biblioteca para geração de relatórios em PDF. |
| **Firebase (Firestore/Auth)** | (Planejado) Serviços de nuvem para sincronização e autenticação. |

## **🚀 Como Executar o Projeto**

Siga os passos abaixo para configurar e rodar a aplicação em seu ambiente de desenvolvimento.

1. **Clone o Repositório:**  
   git clone \[https://github.com/atnzpe/app\_oficina\_mecanica.git\](https://github.com/atnzpe/app\_oficina\_mecanica.git)  
   cd app\_oficina\_mecanica

2. **Crie e Ative um Ambiente Virtual:**  
   * No Windows:  
     python \-m venv venv  
     .\\venv\\Scripts\\activate

   * No macOS/Linux:  
     python3 \-m venv venv  
     source venv/bin/activate

3. **Instale as Dependências:**  
   pip install \-r requirements.txt

4. **Execute a Aplicação:**  
   flet run main.py

   Na primeira execução, o banco de dados data/database.db e as pastas necessárias serão criados. Você será guiado para criar o primeiro usuário administrador e configurar a oficina.

## **🗺️ Roadmap do Projeto**

Nosso roadmap é gerenciado através das [**Issues do GitHub**](https://github.com/atnzpe/app_oficina_mecanica/issues). As principais frentes de trabalho são:

* ✅ **Issue \#1 & \#2: Refatoração Arquitetural para MVVM (Concluído)**  
  * \[x\] Estruturação do código em views, viewmodels, services.  
  * \[x\] Criação da camada de acesso a dados com database.py e queries.py.  
  * \[x\] Implementação de fluxo de login, onboarding e prompt seguros.  
* 🚧 **Issue \#8: Implementar CRUD de Clientes (Em Andamento)**  
  * \[ \] Desenvolver a View e o ViewModel para cadastro e edição de clientes.  
* ⏳ **Issue \#6: Modernização da Autenticação (Planejado)**  
  * \[ \] Integrar o Firebase Authentication para login com Google.  
* ⏳ **Issue \#5: Sincronização na Nuvem (Planejado)**  
  * \[ \] Configurar projeto no Firebase (Firestore).  
  * \[ \] Desenvolver o serviço de sincronização entre SQLite e Firestore.  
* ⏳ **Issue \#7: Pipeline de Build Multiplataforma (Planejado)**  
  * \[ \] Configurar script de build para Windows (.exe) e Android (.apk).

## **🤝 Contribuições**

Contribuições são muito bem-vindas\! Se você encontrar um bug ou tiver uma sugestão, por favor, abra uma [**Issue**](https://github.com/atnzpe/app_oficina_mecanica/issues).

## **👨‍💻 Desenvolvedores**

| \<img src="https://www.google.com/search?q=https://avatars.githubusercontent.com/u/89949983%3Fv%3D4" width=115\> \<sub\>Gleyson Atanázio\</sub\> | \<img src="https://avatars.githubusercontent.com/u/101737645?v=4" width=115\> \<sub\>Vanderson\</sub\> |
| :---- | :---- |

\<p align="center"\> ⌨️ com 💜 por Gleyson Atanázio e Vanderson \</p\>