
# Backend Labtrans  

API e Banco de dados que disponibiliza os GeoDados necessarios.





## Stack utilizada


**Back-end:** Python, FastAPI,uvicorn,peewee.

**Banco de Dados Suportados:**
Sqlite3, PostgreSQL.

**Detalhes Sobre a Infraestrutura:**
O PostgreSQL está rodando atualmente em Docker


## Instalação PostgreSQL in Docker

Instale e configure o PostgreSQL

```bash
  cd docker
  sudo bash dockerbuild.sh
```
O diretorio Docker, já possui um **DockerFile** para configuração da imagem e um **init.sql** para fazer a configuração das tabelas. 
O dockerbuild.sh apenas automatiza essa função.


## Instalação Principal


```bash
  sudo bash start.sh
```
O start.sh ele verifica a existencia de um ambiente virtual, se não houver ele cria e ativa,
em seguida executa a instalação do requirements.txt
``` bash
    pip install -r requirements.txt
```
E faz a execução do Uvicorn
``` bash
uvicorn main:app --reload

```
## Pronto seu servidor esta ON!

Ele ficara disponivel em
``` bash
http://localhost:8000

```
Para acessar a documentação da API, basta acessa
``` bash
http://localhost:8000/docs
```