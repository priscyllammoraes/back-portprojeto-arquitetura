import pytest
import uuid
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
    session = TestSession()
    uid = str(uuid.uuid4())[:7]
    projeto = Projeto(
        nome=f"Projeto Teste {uid}",
        sigla=f"PRJ{uid.upper()}",
        descricao="Projeto criado para testes",
        tipo="Desenvolvimento",
        custo=60000,
        status="Em andamento"
    )
    recurso = Recurso(
        nome=f"Recurso Teste {uid}",
        papel="Dev",
        alocacao="20h"
    )
    session.add_all([projeto, recurso])
    session.commit()
    session.refresh(projeto)
    session.refresh(recurso)
    session.close()
    return projeto.id, recurso.id

def test_criar_recurso_sem_projeto(client: FlaskClient):
    uid = str(uuid.uuid4())[:6]
    response = client.post("/recurso", json={
        "nome": f"Ana {uid}",
        "papel": "QA",
        "alocacao": "40h"
    })
    assert response.status_code == 200
    assert "criado" in response.json["mensagem"].lower()

def test_criar_projeto(client: FlaskClient):
    uid = str(uuid.uuid4())[:7]
    response = client.post("/projeto", json={
        "nome": f"Projeto {uid}",
        "sigla": f"SIG{uid.upper()}",
        "descricao": "Projeto de teste",
        "tipo": "Infraestrutura",
        "custo": 55000,
        "status": "Concluído"
    })
    assert response.status_code == 200
    assert "id" in response.json

def test_vincular_recurso_a_projeto(client: FlaskClient, dados_projeto_e_recurso):
    projeto_id, recurso_id = dados_projeto_e_recurso
    response = client.post(f"/projeto/recurso?id_projeto={projeto_id}&id_recurso={recurso_id}")
    assert response.status_code == 200
    assert "vinculado" in response.json["mensagem"].lower()

def test_listar_recursos(client: FlaskClient, dados_projeto_e_recurso):
    response = client.get("/recurso")
    assert response.status_code == 200
    assert isinstance(response.json["recursos"], list)
    for recurso in response.json["recursos"]:
        assert "id" in recurso
        assert "nome" in recurso

def test_remover_vinculo_recurso(client: FlaskClient, dados_projeto_e_recurso):
    projeto_id, recurso_id = dados_projeto_e_recurso

    # Garante que o recurso esteja vinculado antes de remover
    client.post(f"/projeto/recurso?id_projeto={projeto_id}&id_recurso={recurso_id}")

    response = client.delete(f"/projeto/recurso?id_projeto={projeto_id}&id_recurso={recurso_id}")
    assert response.status_code == 200
    assert "desvinculado" in response.json["mensagem"].lower()

def test_excluir_recurso_sem_vinculo(client: FlaskClient, dados_projeto_e_recurso):
    _, recurso_id = dados_projeto_e_recurso
    response = client.delete(f"/recurso?id={recurso_id}")
    assert response.status_code == 200
    assert "removido" in response.json["mensagem"].lower()
