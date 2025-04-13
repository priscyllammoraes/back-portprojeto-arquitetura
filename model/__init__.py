import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

# Importando as classes de modelo
from model.base import Base
from model.projeto import Projeto
from model.historico import Historico
from model.recurso import Recurso  

# Definindo o caminho do banco de dados
db_path = "database/"

# Criando o diretório para armazenar o banco de dados, caso não exista
if not os.path.exists(db_path):
    os.makedirs(db_path)

# Definindo a URL de conexão com o banco de dados SQLite
db_url = f"sqlite:///{db_path}/db.sqlite3"

# Criando o engine de conexão com o banco de dados
engine = create_engine(db_url, echo=True)

# Verificando se o banco de dados já existe, caso contrário, criando-o
if not database_exists(engine.url):
    create_database(engine.url)

# Criando as tabelas no banco de dados, se ainda não existirem
Base.metadata.create_all(engine)

# Criando a fábrica de sessões
Session = sessionmaker(bind=engine)

# Opcional: criando uma sessão para uso imediato (em testes)
# session = Session()
