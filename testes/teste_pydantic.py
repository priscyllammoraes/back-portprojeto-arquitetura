import pytest
from flask.testing import FlaskClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import app
from model.base import Base
from model.projeto import Projeto
from model.recurso import Recurso

# Banco de dados temporário (isolado da aplicação real)
test_engine = create_engine("sqlite:///:memory:", echo=False)
TestSession = sessionmaker(bind=test_engine)

@pytest.fixture
def client():
    Base.metadata.create_all(test_engine)
    app.config['TESTING'] = True
    app.session = TestSession
    with app.test_client() as client:
        yield client

@pytest.fixture
def dados_projeto_e_recurso():
    """Cria um projeto e um recurso únicos para os testes."""
    session = TestSession()
    projeto = Projeto(
        nome="Projeto Teste Unico",
        sigla="PRJTESTEUNICO",
        descricao="Projeto criado para testes com nome único",
        tipo="Desenvolvimento",
        custo=75000,
        status="Em andamento"
    )
    recurso = Recurso(
        nome="João Testador",
        papel="Desenvolvedor",
        alocacao="20h"
    )
    session.add_all([projeto, recurso])
    session.commit()
    session.refresh(projeto)
    session.refresh(recurso)
    session.close()
    return projeto.id, recurso.id

def test_criar_recurso_sem_projeto(client: FlaskClient):
    response = client.post("/recurso", json={
        "nome": "Ana Testadora",
        "papel": "Analista QA",
        "alocacao": "40h"
    })
    print("DEBUG criar_recurso:", response.status_code, response.json)
    assert response.status_code == 200
    assert "criado" in response.json["mensagem"].lower()

def test_criar_projeto(client: FlaskClient):
    response = client.post("/projeto", json={
        "nome": "Projeto Unico 2",
        "sigla": "PRJUNICO2",
        "descricao": "Projeto criado para evitar duplicidade",
        "tipo": "Banco de Dados",
        "custo": 35000,
        "status": "A iniciar"
    })
    print("DEBUG criar_projeto:", response.status_code, response.json)
    assert response.status_code == 200
    assert "id" in response.json

def test_vincular_recurso_a_projeto(client: FlaskClient, dados_projeto_e_recurso):
    projeto_id, recurso_id = dados_projeto_e_recurso
    response = client.post(f"/projeto/recurso?id_projeto={projeto_id}&id_recurso={recurso_id}")
    print("DEBUG vincular:", response.status_code, response.json)
    assert response.status_code == 200
    assert "vinculado" in response.json["mensagem"].lower()

def test_listar_recursos(client: FlaskClient):
    response = client.get("/recurso")
    print("DEBUG listar:", response.status_code, response.json)
    assert response.status_code == 200
    assert isinstance(response.json["recursos"], list)

def test_remover_vinculo_recurso(client: FlaskClient, dados_projeto_e_recurso):
    projeto_id, recurso_id = dados_projeto_e_recurso
    response = client.delete(f"/projeto/recurso?id_projeto={projeto_id}&id_recurso={recurso_id}")
    print("DEBUG desvincular:", response.status_code, response.json)
    assert response.status_code == 200
    assert "desvinculado" in response.json["mensagem"].lower()

def test_excluir_recurso_sem_vinculo(client: FlaskClient, dados_projeto_e_recurso):
    _, recurso_id = dados_projeto_e_recurso
    response = client.delete(f"/recurso?id={recurso_id}")
    print("DEBUG excluir:", response.status_code, response.json)
    assert response.status_code == 200
    assert "removido" in response.json["mensagem"].lower()
