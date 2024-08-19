# SQLAlchemy Driver Exploration

Este projeto é um estudo sobre a utilização de diferentes drivers para conectar o SQLAlchemy, uma biblioteca de abstração e gerenciamento de bancos de dados relacionais em Python, ao banco de dados PostgreSQL.

## Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Utilização](#utilização)
- [Estrutura do Projeto](#estrutura-do-projeto)

## Visão Geral

O objetivo deste projeto é explorar e comparar diferentes drivers disponíveis para utilizados pelo SQLAlchemy para se conectar a um banco de dados PostgresSQL e formas diferentes de gerenciar a criação de tabelas e manipular objetos. 

O SQLAlchemy é uma poderosa ferramenta para interação com bancos de dados relacionais em Python. Ele fornece uma abstração de alto nível para realizar operações no banco de dados, permitindo que desenvolvedores trabalhem com objetos Python (uma poderosa biblioteca ORM (Object-Relational Mapping)) em vez de escrever consultas SQL diretamente, facilitando o trabalho com bancos de dados relacionais em Python. Dois conceitos fundamentais para entender como o SQLAlchemy opera são a engine e a session.

### Conceito de Engine no SQLAlchemy

A engine é o ponto de partida para qualquer operação com o SQLAlchemy. Ela é responsável por estabelecer a conexão com o banco de dados, gerenciar recursos, e executar as instruções SQL geradas pelo ORM ou escritas manualmente. A engine também encapsula detalhes sobre o dialeto do banco de dados, que é uma camada de abstração que permite ao SQLAlchemy gerar SQL compatível com diferentes bancos de dados.

### Conceito de Session no SQLAlchemy

A session no SQLAlchemy representa uma sessão de comunicação com o banco de dados. Ela funciona como um "carrinho de compras" onde as operações de consulta e modificação de dados são armazenadas antes de serem definitivamente enviadas para o banco. Com isso, a session permite que múltiplas operações sejam agrupadas em uma transação única, garantindo que todas as operações sejam aplicadas de forma atômica, ou seja, todas as operações ocorrem ou nenhuma ocorre, o que é crucial para manter a integridade dos dados.

### Conceitos de utlização assíncrona

No SQLAlchemy, a versão assíncrona da engine e session permite que operações com o banco de dados sejam executadas de forma não bloqueante, o que é essencial em aplicações que precisam lidar com I/O de maneira eficiente, como em servidores web de alta concorrência.

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
    └── async_db.py
    └── migrate_db.py
```

#### Driver Síncrono - psycopg2

`src/db.py`

A engine é criada usando a função create_engine() do SQLAlchemy, onde você especifica o URL de conexão do banco de dados, que inclui o driver sincrono que será utilizado, neste caso, o psycopg2 para o PostgreSQL.

Já a session é instanciada a partir de um sessionmaker, que por sua vez é configurado para usar a engine criada anteriormente.

#### Driver Assíncrono - asyncpg

`src/async_db.py`

Assim como a engine síncrona, a engine assíncrona (*async_engine*) é o ponto central para a conexão com o banco de dados, mas é projetada para operar no modo assíncrono. Isso permite que as operações sejam aguardadas (await), o que libera o loop de eventos para processar outras tarefas enquanto a operação de banco de dados é realizada.

A engine assíncrona é criada utilizando a função create_async_engine() do SQLAlchemy. Neste exemplo, o driver utilizado é o asyncpg, que é um driver nativo assíncrono para o PostgreSQL.

A session assíncrona (*AsyncSession*) funciona de maneira semelhante à versão síncrona, mas é projetada para suportar a execução assíncrona de operações no banco de dados. Isso significa que as operações de consulta e modificação de dados podem ser executadas de forma não bloqueante, utilizando await.

Assim como na versão síncrona, a session é instanciada a partir de um sessionmaker, mas configurada para utilizar a engine assíncrona.

##### Uso do asyncpg

No código fornecido, o driver asyncpg é utilizado para criar a engine assíncrona, que conecta o SQLAlchemy ao banco de dados PostgreSQL de forma assíncrona. A string de conexão utilizada é no formato `"postgresql+asyncpg://user:password@host:port/database"`:

```python
ASYNC_DB = "postgresql+asyncpg://admin:changethis@localhost:5432/async-asyncpg"
async_engine = create_async_engine(ASYNC_DB, echo=True, future=True)
```

Esse código cria uma engine assíncrona que será usada para todas as interações subsequentes com o banco de dados, incluindo a criação de tabelas e a geração de sessões.

A partir da async_engine, uma session assíncrona é gerada usando o async_sessionmaker

A partir da session criada é possível iniciar uma sessão para adicionar objetos ao banco de dados ou executar consultas, como demonstrado no código:

```python
async with get_session() as session:
    hero1 = Hero(name="spongebob")
    hero2 = Hero(name="sandy")
    session.add_all([hero1, hero2])
    await session.commit()

```

Aqui, a session é utilizada dentro de um contexto assíncrono (async with), garantindo que as operações de adição e commit sejam executadas de forma não bloqueante.


#### Utilização do Async Alembic

`src/migrate_db.py`

O Alembic é uma ferramenta de migração de banco de dados projetada para trabalhar com o SQLAlchemy. Ele permite que você gerencie mudanças no esquema do banco de dados de forma organizada, utilizando scripts de migração. Em um ambiente assíncrono, o Alembic pode ser configurado para trabalhar com a engine e session assíncronas do SQLAlchemy, permitindo que as migrações sejam executadas de forma não bloqueante.

O processo de migração com Alembic envolve a criação de scripts que descrevem as mudanças a serem aplicadas ao banco de dados, como a criação de tabelas, modificação de colunas, ou inserção de dados. Esses scripts podem ser gerados automaticamente com base nas definições dos modelos do SQLAlchemy, tornando a gestão do esquema do banco de dados mais simples e eficiente.

O Alembic será utilizado para criar e atualizar tabelas, schemas e suas interligações / dependências.

```shell
alembic init -t async alembic
```
Inicializa o Alembic com um template assíncrono.

Edite do arquivo `alembic/env.py` para configurar a engine assíncrona.

```text
from src.migrate_db import Base, MIGRATE_DB

... 

config = context.config
config.set_main_option("sqlalchemy.url", MIGRATE_DB)

...

target_metadata = Base.metadata

...
```

Uso do comando para gerar automaticamente um novo script de migração com base nas mudanças nos modelos: 

```shell
alembic revision --autogenerate -m "create heroes"

```

Aplicação da migração

```shell
alembic upgrade head
```

execute o script migrate_db.py para inserir novos dados na tabela criada.

Para verificar o histórico de migrações utilize:

```shell
alembic history
```

Para desfazer as migrações utilize:

```shell
 alembic downgrade -1
```

ou utilize o identificador apontado no histórico

```shell
alembic downgrade 2bc75cfe65ae
```

##### Uso do alembic em ambientes produtivos

O uso de Alembic para gerenciar migrações de banco de dados é uma prática recomendada para a maioria dos projetos, especialmente aqueles que exigem escalabilidade, consistência entre ambientes, e controle de versões. Manter e executar scripts SQL manualmente pode ser adequado em sistemas mais simples ou onde o controle total é necessário, mas requer muito mais cuidado para evitar erros e inconsistências. A automação, testes rigorosos, e uma documentação clara são essenciais, independentemente da abordagem escolhida.


###### Vantagens

- *Controle de Versões:* O Alembic permite rastrear todas as alterações no esquema do banco de dados através de migrações versionadas. Isso facilita a reverter, aplicar ou reverter alterações conforme necessário.

- *Automação:* Com Alembic, muitas das operações, como criar novas tabelas, alterar colunas, ou adicionar índices, podem ser geradas automaticamente com base nas mudanças no código dos modelos do SQLAlchemy.

- *Consistência:* Garantir que todos os ambientes (desenvolvimento, teste, produção) tenham o mesmo esquema de banco de dados é muito mais fácil com Alembic, uma vez que as migrações podem ser aplicadas de forma consistente em todos os ambientes.

- *Histórico e Rastreabilidade:* As migrações são armazenadas como scripts e versionadas, o que permite auditar e entender como e quando o esquema do banco de dados mudou ao longo do tempo.

- **Integração com CI/CD:* Alembic pode ser integrado em pipelines de CI/CD, automatizando a aplicação de migrações em ambientes de teste e produção, reduzindo o risco de erros manuais.

###### Desvantagens

- *Curva de Aprendizado:* Para desenvolvedores que não estão familiarizados com ferramentas de migração como o Alembic, pode haver uma curva de aprendizado significativa.

- *Complexidade em Cenários de Migrações Conflitantes:* Em ambientes onde várias equipes ou desenvolvedores fazem alterações no banco de dados, pode haver conflitos de migração que precisam ser resolvidos.

- **Dependência de Ferramentas:* O uso de Alembic introduz uma dependência adicional no projeto, o que pode ser um fator em ambientes onde simplicidade e controle total são priorizados.


#### Utilização do SQLAlchemy em uma aplicação com o AsyncSession

##### session.get()

Uso: Este método é ideal quando você quer buscar uma entrada específica da tabela pelo valor de sua chave primária.
Quando usar: Utilize get quando você souber o valor da chave primária de um registro e quiser recuperá-lo diretamente.

```python
hero = await db.get(HeroModel, hero_id)
```

##### select(Model).where()

Uso: Este método é usado para construir consultas SQL mais flexíveis com condições específicas (WHERE).
Quando usar: Utilize select().where() quando precisar buscar registros com base em uma ou mais condições.


```python
stmt = select(HeroModel).where(HeroModel.name == "spongebob")
result = await db.execute(stmt)
hero = result.scalar_one_or_none()
``` 

##### scalar()

Uso: Executa a consulta e retorna o primeiro elemento do primeiro resultado da query ou None se não houver resultados.
Quando usar: Use scalar quando espera apenas um único resultado da consulta.

```python
stmt = select(HeroModel).where(HeroModel.name == "spongebob")
hero = await db.scalar(stmt)
```
##### scalars()

Uso: Retorna um gerador sobre os valores da coluna selecionada, ou seja, itera sobre todas as entradas de uma coluna específica ou de todo o modelo.
Quando usar: Use scalars para buscar múltiplos registros quando a consulta pode retornar vários resultados.

```python
stmt = select(HeroModel).where(HeroModel.app_src == "async_app")
result = await db.execute(stmt)
heroes = result.scalars().all()
```



