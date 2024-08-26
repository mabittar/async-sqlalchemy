# SQLAlchemy Driver Exploration

Este projeto é um estudo sobre a utilização de diferentes drivers para conectar o SQLAlchemy, uma biblioteca de abstração e gerenciamento de bancos de dados relacionais em Python, ao banco de dados PostgreSQL.

## Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Utilização](#utilização)
- [Testes de Conexão](#teste-de-conexao)
- [Utilização diferentes Drivers com FastAPI](#drivers)
- [Testes de Carga](#testes-de-carga)
- [Conclusão](#conclusão)

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
git clone https://github.com/mabittar/async-sqlalchemy
cd async-sqlalchemy
```

### 2. Configurar o ambiente

Um arquivo docker-compose.yml está incluído no projeto para facilitar a configuração de um banco de dados PostgreSQL localmente. Para iniciar o banco de dados, execute:

```bash
docker-compose build
docker-compose up -d
```

Caso queira executar localmente as diferentes aplicações, remova ou comente as linhas do arquivo `docker-compose.yml` para evitar que as mesmas sejam executadas com os comandos acima.

Caso queira encerrar ou mesmo paralizar a execução das aplicações utilize:

```bash
docker-compose down
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

### Teste de Conexão

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

Assim como a engine síncrona, a engine assíncrona (_async_engine_) é o ponto central para a conexão com o banco de dados, mas é projetada para operar no modo assíncrono. Isso permite que as operações sejam aguardadas (await), o que libera o loop de eventos para processar outras tarefas enquanto a operação de banco de dados é realizada.

A engine assíncrona é criada utilizando a função create_async_engine() do SQLAlchemy. Neste exemplo, o driver utilizado é o asyncpg, que é um driver nativo assíncrono para o PostgreSQL.

A session assíncrona (_AsyncSession_) funciona de maneira semelhante à versão síncrona, mas é projetada para suportar a execução assíncrona de operações no banco de dados. Isso significa que as operações de consulta e modificação de dados podem ser executadas de forma não bloqueante, utilizando await.

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

- _Controle de Versões:_ O Alembic permite rastrear todas as alterações no esquema do banco de dados através de migrações versionadas. Isso facilita a reverter, aplicar ou reverter alterações conforme necessário.

- _Automação:_ Com Alembic, muitas das operações, como criar novas tabelas, alterar colunas, ou adicionar índices, podem ser geradas automaticamente com base nas mudanças no código dos modelos do SQLAlchemy.

- _Consistência:_ Garantir que todos os ambientes (desenvolvimento, teste, produção) tenham o mesmo esquema de banco de dados é muito mais fácil com Alembic, uma vez que as migrações podem ser aplicadas de forma consistente em todos os ambientes.

- _Histórico e Rastreabilidade:_ As migrações são armazenadas como scripts e versionadas, o que permite auditar e entender como e quando o esquema do banco de dados mudou ao longo do tempo.

- \*_Integração com CI/CD:_ Alembic pode ser integrado em pipelines de CI/CD, automatizando a aplicação de migrações em ambientes de teste e produção, reduzindo o risco de erros manuais.

###### Desvantagens

- _Curva de Aprendizado:_ Para desenvolvedores que não estão familiarizados com ferramentas de migração como o Alembic, pode haver uma curva de aprendizado significativa.

- _Complexidade em Cenários de Migrações Conflitantes:_ Em ambientes onde várias equipes ou desenvolvedores fazem alterações no banco de dados, pode haver conflitos de migração que precisam ser resolvidos.

- \*_Dependência de Ferramentas:_ O uso de Alembic introduz uma dependência adicional no projeto, o que pode ser um fator em ambientes onde simplicidade e controle total são priorizados.

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

### Utilização de Diferentes Drivers

```text
├── README.md
├── docker-compose.yml
├── Dockerfile.yml
├── Dockerfile-psycopg2.yml
├── Dockerfile-psycopg3.yml
├── requirements.txt
├── locustfile.py
├── toys.sql
└── app
    └── shared
        └── async_database.py
        └── database.py
        └── models.py
        └── schema.py
    └── application.py
    └── async_application.py
    └── async_router.py
    └── asyncpg_main.py
    └── psycopg2_main.py
    └── psycopg3_main.py
    └── router.py
    └── settings.py
```


Já que diferentes formas de realizar a conexão com o banco Postgres foi implementada anteriormente, agora será utilizadas as diferentes técnicas e iremos comparar os resultados.
O cenário de teste envolve criar uma banco de dados com tabelas que possuam relacionamento many-to-many, pois a tendência é aumentar rapidamente com o tempo de utilização da Aplicação.

A biblioteca `Locust` foi utilizada para implementar os testes de carga.

Mas antes vamos aos detalhes.

#### Shared

Neste diretório estão arquivos que são compartilhados entre as as aplicação, como o modelo do banco de dados e o shema de input dos dados.

##### Modelo do banco de Dados.

`app/shared/models.py`
Este projeto utiliza SQLAlchemy para a modelagem do banco de dados, adotando uma estrutura relacional que inclui entidades e relacionamentos.

A classe Base é uma classe base declarativa que define colunas comuns a todas as tabelas do projeto, como created_at e updated_on, que registram automaticamente a data de criação e a última atualização dos registros, respectivamente.

```python
class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

```

Tabela de Associação: *user_toy_association*
A tabela user_toy_association é uma tabela de associação para implementar um relacionamento muitos-para-muitos entre usuários (UserModel) e brinquedos (ToyModel). Cada registro na tabela associa um usuário a um brinquedo específico.

Modelo *ToyModel*
A tabela toys armazena informações sobre os brinquedos. Cada brinquedo tem um identificador único (id) e um nome (name). A coluna id é do tipo UUID e é gerada automaticamente para garantir unicidade.

Modelo *UserModel*
A tabela users armazena informações sobre os usuários. Cada usuário possui um identificador único (id) e um nome (name). A relação muitos-para-muitos entre usuários e brinquedos é gerida pela tabela de associação user_toy_association. A propriedade toys define essa relação, utilizando relationship com o parâmetro secondary, que referencia a tabela de associação.

Esta estrutura permite gerenciar eficientemente as entidades e seus relacionamentos, mantendo a base de dados bem estruturada e fácil de expandir conforme as necessidades do projeto evoluem.

##### Schema

`app/shared/schema.py`
Utilizado o `Pydantic` para validação do input e composição da respota esperada para cada endpoint.

##### Database

`app/shared/async_database.py` e `app/shared/database.py`
É o arquivo responsável por criar e gerenciar a sessão do banco de dados, assim como a injeção de dependência utilizada pelo FastAPI. Foi necessário criar dois arquivos separados, pois um utiliza a sessão assíncrona e outro síncrona.

#### async_application e application

`app/async_application.py` e `app/application.py`
Ambas as abordagens compartilham uma estrutura semelhante e são projetadas para serem facilmente intercambiáveis, dependendo das necessidades do projeto. A escolha entre uma aplicação assíncrona e uma síncrona deve ser baseada nos requisitos de desempenho e escalabilidade da aplicação. 
São os scripts responsáveis por criar a instância do FastAPI, utilizando os recursos do script database, conforme necessidade. Esse script também é reponsável por injetar as respectivas rotas (async_router e router), assim como a demais configurações.


#### Assíncrona
A aplicação assíncrona utiliza `asyncsessionmanager` para gerenciar a conexão com o banco de dados de forma assíncrona, garantindo que todas as operações de I/O (Input/Output) sejam não-bloqueantes. Esta abordagem é ideal para cenários onde a aplicação lida com um grande número de requisições simultâneas, pois permite melhor escalabilidade e performance.



#### Síncrona
A aplicação síncrona utiliza `sessionmanager` para gerenciar a conexão com o banco de dados de forma síncrona. Esta abordagem é adequada para aplicações mais simples ou onde a latência e o volume de requisições simultâneas não são críticos. A simplicidade de uma abordagem síncrona pode ser mais fácil de entender e depurar, especialmente em ambientes de desenvolvimento ou em sistemas de baixa carga.


#### main.py

Os arquivos `app/asyncpg_main.py`, `app/psycopg2_main.py`e `app/psycopg3_main.py` são responsáveis por iniciar as diferentes aplicações, cada qual utilizando drivers ou dialetos diferentes de conexão com o Postgres. Esses arquivos também são utilizados para indicar ao respectivo Dockerfile, qual aplicação deve ser iniciado.


## Testes de Carga

Para avaliar o desempenho das duas abordagens de acesso ao banco de dados (assíncrona e síncrona), utilizei a ferramenta Locust, que é uma estrutura de teste de carga open-source em Python. O teste simulou várias requisições para os endpoints de criação e leitura de users e toys.

### Resultados Obtidos
Os resultados dos testes de carga foram coletados para comparar as abordagens síncrona e assíncrona. Abaixo estão as imagens dos resultados dos testes utilizando os drivers psycopg2 (síncrono) e asyncpg (assíncrono).

Resultados com psycopg2 (Síncrono):
psycopg (apesar da ausência da numeração essa é a biblioteca mais atual)
![psycopg](assets/psycopg.png)

Resultados com asyncpg (Assíncrono):
Asyncpg
![alt text](assets/asyncpg.png)


## Conclusão
Os testes de carga indicaram diferenças significativas no comportamento de desempenho entre as abordagens síncronas e assíncronas.

Abordagem Síncrona (psycopg2): O tempo de resposta foi consistente em níveis mais baixos de carga, mas aumentou significativamente à medida que o número de requisições cresceu. Isso pode ser atribuído ao bloqueio nas operações de I/O, que afeta a escalabilidade em cenários de alta concorrência.

Abordagem Assíncrona (asyncpg): Demonstrou uma melhor capacidade de lidar com um grande número de requisições simultâneas, mantendo os tempos de resposta mais baixos em comparação com a abordagem síncrona. Essa vantagem é decorrente da natureza não bloqueante das operações assíncronas.

Portanto, a escolha entre essas abordagens depende do caso de uso específico. Para aplicações com alta concorrência e onde o tempo de resposta é crítico, a abordagem assíncrona com asyncpg se mostrou superior. No entanto, para cenários com menos concorrência ou onde a simplicidade da implementação é priorizada, a abordagem síncrona com psycopg2 pode ser suficiente.