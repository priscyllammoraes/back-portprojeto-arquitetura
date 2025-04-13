from flask import Flask, jsonify, request, redirect
from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from typing import List
import requests

# ======================= Imports Internos =======================
from model import Session
from model.projeto import Projeto
from model.historico import Historico
from model.recurso import Recurso
from model.projeto_recurso import projeto_recurso

from schema.projeto_schema import (
    ProjetoSchema, ProjetoIdSchema, ProjetoEditSchema,
    ProjetoMsgSchema, ProjetoBuscaIdSchema, ListagemProjetoSchema
)
from schema.historico_schema import HistoricoSchema, HistoricoViewSchema, HistoricoIdSchema
from schema.recurso_schema import RecursoSchema, RecursoEditSchema, RecursoViewSchema, ListagemRecursoSchema, RecursoBuscaIdSchema, RecursoMsgSchema
from schema.error_schema import ErrorSchema
from logger import logger


# ======================= Configuração da API =======================
info = Info(
    title="Portfólio de Projetos",
    version="1.0.0",
    description="API para gerenciar o portfólio de projetos, incluindo a criação, edição, histórico e alocação de recursos."
)

app = OpenAPI(__name__, info=info)
CORS(app)

'''
Rotas criadas:
    
    PROJETO:
    POST   /projeto              → Adicionar novo projeto
    GET    /projetos             → Listar todos os projetos
    GET    /projeto?id=1         → Buscar projeto por ID
    PUT    /projeto              → Editar projeto existente
    DELETE /projeto?id=1         → Deletar projeto

    HISTÓRICO:
    POST   /historico?id=1       → Adicionar histórico a um projeto
    GET    /historico?id=1       → Listar históricos de um projeto

    RECURSO:
    POST   /recurso              → Cadastrar recurso (com ou sem vínculo a projeto)
    GET    /recurso              → Listar todos os recursos
    PUT    /recurso              → Atualizar dados de um recurso
    DELETE /recurso?id=1         → Excluir recurso (caso não esteja vinculado a projetos)

    PROJETO_RECURSO:
    POST   /projeto/recurso?id_projeto=1&id_recurso=2   → Vincular recurso a projeto
    DELETE /projeto/recurso?id_projeto=1&id_recurso=2   → Remover vínculo recurso ↔ projeto
    GET    /projeto/recursos?id=1                       → Listar recursos vinculados a um projeto

'''

# ======================= Tags da Documentação =======================
projeto_tag = Tag(name="Projeto", description="Gerenciamento de Projetos")
historico_tag = Tag(name="Histórico", description="Gerenciamento de Histórico")
recurso_tag = Tag(name="Recurso", description="Gerenciamento de Recursos")
projeto_recurso_tag = Tag(name="Projeto_Recurso", description="Vínculos entre Projetos e Recursos")

# ======================= Rota Inicial =======================
@app.route("/")
def home():
    return redirect("/openapi")

# ======================= API Externa: Conversão de Moeda =======================
@app.route("/conversao", methods=["GET"])
def converter_moeda():
    valor = request.args.get("valor")
    de = request.args.get("de", "BRL")
    para = request.args.get("para", "USD")

    if not valor:
        return jsonify({"erro": "Parâmetro 'valor' é obrigatório."}), 400

    try:
        float(valor)
    except ValueError:
        return jsonify({"erro": "O valor informado não é numérico."}), 400

    url = f"https://api.frankfurter.app/latest?amount={valor}&from={de}&to={para}"
    resposta = requests.get(url)

    if resposta.status_code == 200:
        dados = resposta.json()
        convertido = dados.get("rates", {}).get(para)

        return jsonify({
            "valor_original": float(valor),
            "de": de,
            "para": para,
            "valor_convertido": convertido
        })

    return jsonify({"erro": "Erro ao buscar taxa de câmbio."}), 500


# ======================= ROTAS: Projetos =======================
@app.post("/projeto", tags=[projeto_tag], responses={"200": ProjetoMsgSchema, "400": ErrorSchema, "409": ErrorSchema})
def criar_projeto(body: ProjetoSchema):
    """Adiciona um novo projeto na base de dados."""
    session = Session()
    try:
        projeto = Projeto(**body.dict())
        session.add(projeto)
        session.commit()
        logger.info(f"Projeto '{projeto.id}' criado com sucesso!")
        return {"mensagem": "Projeto criado com sucesso!", "id": projeto.id}, 200
    except IntegrityError:
        session.rollback()
        logger.warning(f"Erro ao criar o projeto '{body.nome}': Nome ou sigla já existentes.")
        return {"mensagem": "Projeto com mesmo nome ou sigla já existe."}, 409
    except Exception as e:
        session.rollback()
        logger.error(f"Erro inesperado ao criar projeto: {e}")
        return {"mensagem": f"Erro ao criar projeto: {str(e)}"}, 400


@app.get("/projetos", tags=[projeto_tag], responses={"200": ListagemProjetoSchema, "404": ErrorSchema})
def listar_projetos():
    """Lista todos os projetos cadastrados."""
    session = Session()
    projetos = session.query(Projeto).all()

    if not projetos:
        logger.info("Nenhum projeto encontrado na base de dados.")
        return jsonify({"mensagem": "Nenhum projeto encontrado."}), 200

    logger.info(f"{len(projetos)} projeto(s) encontrados.")
    return jsonify([ProjetoIdSchema.from_orm(p).dict() for p in projetos]), 200


@app.get("/projeto", tags=[projeto_tag], responses={"200": ProjetoIdSchema, "500": ErrorSchema})
def buscar_projeto(query: ProjetoBuscaIdSchema):
    """Buscar um projeto pelo ID fornecido."""
    session = Session()
    try:
        projeto = session.query(Projeto).filter(Projeto.id == query.id).first()

        if not projeto:
            return jsonify({"mensagem": "Projeto não encontrado"}), 404

        projeto_dict = ProjetoIdSchema.from_orm(projeto).dict()
        return jsonify(projeto_dict), 200

    except Exception as e:
        logger.error(f"Erro ao buscar projeto: {e}")
        return {"mensagem": f"Erro ao buscar projeto: {str(e)}"}, 500


@app.delete("/projeto", tags=[projeto_tag], responses={"200": ProjetoMsgSchema, "404": ErrorSchema, "500": ErrorSchema})
def deletar_projeto(query: ProjetoBuscaIdSchema):
    """Remove um projeto da base de dados pelo ID."""
    session = Session()
    try:
        projeto = session.query(Projeto).filter(Projeto.id == query.id).first()
        if not projeto:
            return {"mensagem": f"Projeto com ID {query.id} não encontrado."}, 404

        session.delete(projeto)
        session.commit()
        logger.info(f"Projeto com ID {query.id} deletado.")
        return {"mensagem": "Projeto removido", "id": query.id}, 200

    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao deletar projeto: {e}")
        return {"mensagem": f"Erro ao deletar projeto: {str(e)}"}, 500


@app.put("/projeto", tags=[projeto_tag], responses={"200": ProjetoSchema, "404": ErrorSchema, "400": ErrorSchema})
def editar_projeto(body: ProjetoEditSchema):
    """Edita um projeto existente com base no ID e nos novos dados enviados."""
    session = Session()
    try:
        projeto = session.query(Projeto).filter_by(id=body.id).first()
        if not projeto:
            return {"mensagem": f"Projeto com ID {body.id} não encontrado."}, 404

        for campo, valor in body.dict(exclude_unset=True).items():
            if campo != "id" and hasattr(projeto, campo):
                setattr(projeto, campo, valor)

        projeto.validar_nome()
        projeto.validar_sigla()
        projeto.validar_custo()

        session.commit()
        return jsonify({"mensagem": "Projeto atualizado com sucesso!", "projeto": ProjetoSchema.from_orm(projeto).dict()}), 200

    except IntegrityError as e:
        session.rollback()
        return {"mensagem": f"Erro de integridade: {str(e)}"}, 400

    except ValueError as e:
        session.rollback()
        return {"mensagem": f"Erro de validação: {str(e)}"}, 400

    except Exception as e:
        session.rollback()
        return {"mensagem": f"Erro ao atualizar o projeto: {str(e)}"}, 500

    finally:
        session.close()


# ======================= ROTAS: Histórico =======================
@app.post("/historico", tags=[historico_tag], responses={"201": HistoricoViewSchema, "400": ErrorSchema, "404": ErrorSchema})
def adicionar_historico(body: HistoricoSchema):
    """Adiciona um novo registro histórico a um projeto existente."""
    session = Session()
    projeto_id = request.args.get("id")

    if not projeto_id:
        return {"mensagem": "ID do projeto não fornecido."}, 400

    projeto = session.query(Projeto).filter_by(id=projeto_id).first()
    if not projeto:
        return {"mensagem": f"Projeto com ID {projeto_id} não encontrado."}, 404

    try:
        historico = Historico(descricao=body.descricao, projeto_id=projeto_id)
        session.add(historico)
        session.commit()
        logger.info(f"Histórico adicionado ao projeto ID {projeto_id}.")
        return {
            "mensagem": "Histórico adicionado com sucesso!",
            "projeto": projeto_id,
            "descricao": body.descricao
        }, 200
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao adicionar histórico: {e}")
        return {"mensagem": f"Erro ao adicionar histórico: {str(e)}"}, 500
    

@app.get("/historico", tags=[historico_tag], responses={"200": HistoricoViewSchema, "404": ErrorSchema})
def listar_historico():
    """Lista todos os registros históricos de um projeto com base no ID."""
    session = Session()
    projeto_id = request.args.get("id")

    if not projeto_id:
        return {"mensagem": "ID do projeto não fornecido."}, 400

    projeto = session.query(Projeto).filter_by(id=projeto_id).first()
    if not projeto:
        return {"mensagem": f"Projeto com ID {projeto_id} não encontrado."}, 404

    historicos = session.query(Historico).filter_by(projeto_id=projeto_id).all()

    historico_formatado = [
        {
            "id": h.id,
            "descricao": h.descricao,
            "data_insercao": h.data_insercao.strftime("%d/%m/%Y %H:%M")
        } for h in historicos
    ]

    logger.info(f"{len(historicos)} histórico(s) retornado(s) para projeto ID {projeto_id}.")
    return {"projeto_id": projeto_id, "historico": historico_formatado}, 200


# ======================= ROTAS: Recursos =======================
@app.post("/recurso", tags=[recurso_tag], responses={"201": RecursoViewSchema, "400": ErrorSchema, "404": ErrorSchema})
def adicionar_recurso(body: RecursoSchema):
    """Adiciona um novo recurso, e opcionalmente o vincula a um projeto."""
    session = Session()

    try:
        recurso = session.query(Recurso).filter_by(nome=body.nome, papel=body.papel).first()

        if not recurso:
            recurso = Recurso(nome=body.nome, papel=body.papel, alocacao=body.alocacao)
            session.add(recurso)
            session.commit()

        if body.projeto_id:
            projeto = session.query(Projeto).filter_by(id=body.projeto_id).first()
            if not projeto:
                return {"mensagem": "Projeto não encontrado."}, 404

            if recurso not in projeto.recursos:
                projeto.recursos.append(recurso)
                session.commit()

        return jsonify({"mensagem": "Recurso cadastrado com sucesso!", "id": recurso.id}), 200

    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao adicionar recurso: {e}")
        return {"mensagem": f"Erro ao adicionar recurso: {str(e)}"}, 500


@app.get("/recursos", tags=[recurso_tag], responses={"200": ListagemRecursoSchema})
def listar_recursos():
    """Lista todos os recursos cadastrados."""
    session = Session()
    recursos = session.query(Recurso).all()

    if not recursos:
        return jsonify({"mensagem": "Nenhum recurso encontrado."}), 200

    logger.info(f"{len(recursos)} recurso(s) encontrado(s).")
    return jsonify([RecursoViewSchema.from_orm(r).dict() for r in recursos]), 200


@app.get("/recurso", tags=[recurso_tag], responses={"200": RecursoSchema, "404": ErrorSchema, "500": ErrorSchema})
def buscar_recurso(query: RecursoBuscaIdSchema):
    """Retorna um recurso com base no ID."""
    session = Session()

    try:
        recurso = session.query(Recurso).filter_by(id=query.id).first()

        if not recurso:
            return jsonify({"mensagem": "Recurso não encontrado."}), 404

        return jsonify({
            "id": recurso.id,
            "nome": recurso.nome,
            "papel": recurso.papel,
            "alocacao": recurso.alocacao
        }), 200

    except Exception as e:
        logger.error(f"Erro ao buscar recurso: {e}")
        return jsonify({"mensagem": f"Erro interno: {str(e)}"}), 500


@app.get("/recursos-disponiveis", tags=[recurso_tag])
def listar_recursos_disponiveis(query: ProjetoBuscaIdSchema):
    """Retorna os recursos que ainda não estão vinculados ao projeto."""
    session = Session()

    try:
        vinculados = session.query(projeto_recurso.c.recurso_id).filter(projeto_recurso.c.projeto_id == query.id)
        recursos_disponiveis = session.query(Recurso).filter(~Recurso.id.in_(vinculados)).all()

        recursos = [{
            "id": r.id,
            "nome": r.nome,
            "papel": r.papel,
            "alocacao": r.alocacao
        } for r in recursos_disponiveis]

        return jsonify({"recursos": recursos}), 200
    except Exception as e:
        logger.error(f"Erro ao listar recursos disponíveis: {e}")
        return jsonify({"mensagem": f"Erro ao buscar recursos disponíveis: {str(e)}"}), 500


@app.put("/recurso", tags=[recurso_tag], responses={"200": RecursoMsgSchema, "404": ErrorSchema, "400": ErrorSchema})
def atualizar_recurso(body: RecursoEditSchema):
    """Atualiza os dados de um recurso existente."""
    session = Session()

    recurso = session.query(Recurso).filter_by(id=body.id).first()
    if not recurso:
        return {"mensagem": "Recurso não encontrado."}, 404

    try:
        recurso.nome = body.nome
        recurso.papel = body.papel
        recurso.alocacao = body.alocacao
        session.commit()
        return {"mensagem": "Recurso atualizado com sucesso."}, 200
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao atualizar recurso: {e}")
        return {"mensagem": f"Erro ao atualizar recurso: {str(e)}"}, 500


@app.delete("/recurso", tags=[recurso_tag], responses={"200": RecursoMsgSchema, "404": ErrorSchema, "500": ErrorSchema})
def deletar_recurso(query: RecursoBuscaIdSchema):
    """Remove um recurso, se ele não estiver vinculado a nenhum projeto."""
    session = Session()
    recurso_id = request.args.get("id")

    if not recurso_id:
        return {"mensagem": "ID do recurso é obrigatório."}, 400

    recurso = session.query(Recurso).filter_by(id=recurso_id).first()

    if not recurso:
        return {"mensagem": "Recurso não encontrado."}, 404

    if recurso.projetos:
        return {"mensagem": "Recurso não pode ser removido pois está vinculado a um ou mais projetos."}, 400

    try:
        session.delete(recurso)
        session.commit()
        return {"mensagem": "Recurso removido com sucesso."}, 200
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao remover recurso: {e}")
        return {"mensagem": f"Erro ao remover recurso: {str(e)}"}, 500


# ======================= ROTAS: Projeto_Recurso =======================

@app.post("/projeto/recurso", tags=[projeto_recurso_tag])
def vincular_recurso_projeto():
    """Vincula um recurso existente a um projeto existente."""
    session = Session()
    projeto_id = request.args.get("id_projeto")
    recurso_id = request.args.get("id_recurso")

    if not projeto_id or not recurso_id:
        return {"mensagem": "ID do projeto e do recurso são obrigatórios."}, 400

    projeto = session.query(Projeto).filter_by(id=projeto_id).first()
    recurso = session.query(Recurso).filter_by(id=recurso_id).first()

    if not projeto or not recurso:
        return {"mensagem": "Projeto ou recurso não encontrado."}, 404

    if recurso in projeto.recursos:
        return {"mensagem": "Recurso já está vinculado a este projeto."}, 200

    try:
        projeto.recursos.append(recurso)
        session.commit()
        return {"mensagem": "Recurso vinculado ao projeto com sucesso."}, 200
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao vincular recurso: {e}")
        return {"mensagem": f"Erro ao vincular recurso: {str(e)}"}, 500


@app.delete("/projeto/recurso", tags=[projeto_recurso_tag])
def desvincular_recurso_projeto():
    """Remove o vínculo entre um recurso e um projeto."""
    session = Session()
    projeto_id = request.args.get("id_projeto")
    recurso_id = request.args.get("id_recurso")

    if not projeto_id or not recurso_id:
        return {"mensagem": "ID do projeto e do recurso são obrigatórios."}, 400

    projeto = session.query(Projeto).filter_by(id=projeto_id).first()
    recurso = session.query(Recurso).filter_by(id=recurso_id).first()

    if not projeto or not recurso:
        return {"mensagem": "Projeto ou recurso não encontrado."}, 404

    if recurso not in projeto.recursos:
        return {"mensagem": "Recurso não estava vinculado a este projeto."}, 400

    try:
        projeto.recursos.remove(recurso)
        session.commit()
        return {"mensagem": "Recurso desvinculado do projeto com sucesso."}, 200
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao desvincular recurso: {e}")
        return {"mensagem": f"Erro ao desvincular recurso: {str(e)}"}, 500


@app.get("/projeto/recursos", tags=[projeto_tag])
def listar_recursos_por_projeto():
    """Lista os recursos vinculados a um projeto."""
    session = Session()
    projeto_id = request.args.get("id")

    if not projeto_id:
        return {"mensagem": "ID do projeto não fornecido."}, 400

    projeto = session.query(Projeto).filter_by(id=projeto_id).first()

    if not projeto:
        return {"mensagem": "Projeto não encontrado."}, 404

    recursos = projeto.recursos
    lista_recursos = [
        {
            "id": r.id,
            "nome": r.nome,
            "papel": r.papel,
            "alocacao": r.alocacao
        } for r in recursos
    ]

    logger.info(f"{len(lista_recursos)} recurso(s) retornado(s) para o projeto ID {projeto_id}.")
    return {"projeto_id": projeto_id, "recursos": lista_recursos}, 200


if __name__ == "__main__":
    app.run(debug=True)