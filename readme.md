# SQLAlchemy Driver Exploration

Este projeto é um estudo sobre a utilização de diferentes drivers para conectar o SQLAlchemy, uma biblioteca de abstração e gerenciamento de bancos de dados relacionais em Python, ao banco de dados PostgreSQL.

## Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Utilização](#utilização)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Visão Geral

O objetivo deste projeto é explorar e comparar diferentes drivers disponíveis para SQLAlchemy ao se conectar com o banco de dados PostgreSQL. 

O SQLAlchemy é uma poderosa ferramenta para interação com bancos de dados relacionais em Python. Ele fornece uma abstração de alto nível para realizar operações no banco de dados, permitindo que desenvolvedores trabalhem com objetos Python (uma poderosa biblioteca ORM (Object-Relational Mapping)) em vez de escrever consultas SQL diretamente, facilitando o trabalho com bancos de dados relacionais em Python. Dois conceitos fundamentais para entender como o SQLAlchemy opera são a engine e a session.

### Conceito de Engine no SQLAlchemy

A engine é o ponto de partida para qualquer operação com o SQLAlchemy. Ela é responsável por estabelecer a conexão com o banco de dados, gerenciar recursos, e executar as instruções SQL geradas pelo ORM ou escritas manualmente. A engine também encapsula detalhes sobre o dialeto do banco de dados, que é uma camada de abstração que permite ao SQLAlchemy gerar SQL compatível com diferentes bancos de dados.

### Conceito de Session no SQLAlchemy
A session no SQLAlchemy representa uma sessão de comunicação com o banco de dados. Ela funciona como um "carrinho de compras" onde as operações de consulta e modificação de dados são armazenadas antes de serem definitivamente enviadas para o banco. Com isso, a session permite que múltiplas operações sejam agrupadas em uma transação única, garantindo que todas as operações sejam aplicadas de forma atômica, ou seja, todas as operações ocorrem ou nenhuma ocorre, o que é crucial para manter a integridade dos dados.

## Pré-requisitos

Antes de começar, certifique-se de ter os seguintes itens instalados:

- [Python 3.10+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Configuração do Ambiente

### 1. Clonar o repositório

Clone este repositório para a sua máquina local:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 2. Configurar o ambiente

Um arquivo docker-compose.yml está incluído no projeto para facilitar a configuração de um banco de dados PostgreSQL localmente. Para iniciar o banco de dados, execute:

```bash
docker-compose up -d
```

### 3. Instale as dependencias

Crie um ambiente virtual Python e instale as dependências do projeto:

```bash
python -m venv .venv
source .venv/bin/activate  # No Windows, use `.venv\Scripts\activate`
pip install -r requirements.txt

```

## Utilização

Nos arquivos desse repositório também estão as configurações do de inicialização do debugger do VSCode. Selecione o arquivo de teste e execute o debug selecionando `Inicializador de Módulo`

### Estrtura do Projeto

```text
├── README.md
├── docker-compose.yml
├── requirements.txt
├── test_driver.py
└── src
    └── db.py
```

#### Driver Síncrono - psycopg2

`src/db.py`

A engine é criada usando a função create_engine() do SQLAlchemy, onde você especifica o URL de conexão do banco de dados, que inclui o driver sincrono que será utilizado, neste caso, o psycopg2 para o PostgreSQL.

Já a session é instanciada a partir de um sessionmaker, que por sua vez é configurado para usar a engine criada anteriormente.

#### Uso do psycopg2

No código fornecido, o driver psycopg2 é utilizado para criar a engine, o que conecta o SQLAlchemy ao banco de dados PostgreSQL. Isso é feito através da string de conexão no formato `"postgresql+psycopg2://user:password@host:port/database"`. No exemplo:

```python
DB = "postgresql+psycopg2://admin:changethis@localhost:5432/sync-psycopg2"
engine = create_engine(DB, echo=True)
```

Aqui, o psycopg2 é o driver especificado para se conectar ao PostgreSQL. A engine criada com essa configuração será usada para todas as interações subsequentes com o banco de dados, incluindo a criação de tabelas e a geração de sessões.

A partir da engine, uma session é gerada usando o sessionmaker.

A partir da session criada é possível iniciar uma sessão para adicionar objetos ao banco de dados ou executar consultas, como demonstrado no código:

```python
with Session() as session:
    hero1 = Hero(name="spongebob")
    hero2 = Hero(name="sandy")
    session.add_all([hero1, hero2])
    session.commit()
```