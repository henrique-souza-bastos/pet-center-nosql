"""
API (FastAPI) do Pet Center.

Recebe os dados do formulário (app.py) e grava os documentos no MongoDB.
Cada coleção tem um endpoint POST (cadastrar) e um GET (listar, para conferir).

Autores: Henrique Souza e Yuri Cainã

Como rodar:  uvicorn main:app --reload
Documentação automática (teste pelo navegador):  http://localhost:8000/docs
"""
from bson import ObjectId
from fastapi import FastAPI, HTTPException

from database import banco
from modelos import Pet, Prestador, Tutor, Visita

app = FastAPI(title="Pet Center")


def _para_object_id(valor):
    """Converte um id em texto para ObjectId (formato das referências)."""
    try:
        return ObjectId(valor)
    except Exception:
        return valor


def _inserir(colecao, documento):
    """Grava um documento e devolve o id gerado, tratando erros do banco."""
    try:
        resultado = banco[colecao].insert_one(documento)
        return {"mensagem": "Documento cadastrado!", "id": str(resultado.inserted_id)}
    except Exception as erro:
        raise HTTPException(status_code=500, detail=str(erro))


def _listar(colecao, limite=20):
    """Lista documentos, convertendo os ObjectId em texto para o JSON."""
    documentos = []
    for doc in banco[colecao].find().limit(limite):
        doc["_id"] = str(doc["_id"])
        for campo in ("tutor_id", "pet_id", "prestador_id"):
            if campo in doc:
                doc[campo] = str(doc[campo])
        documentos.append(doc)
    return documentos


# --- Cadastro (POST) -------------------------------------------------
@app.post("/tutores")
def criar_tutor(tutor: Tutor):
    return _inserir("tutores", tutor.model_dump())


@app.post("/pets")
def criar_pet(pet: Pet):
    documento = pet.model_dump()
    documento["tutor_id"] = _para_object_id(documento["tutor_id"])
    return _inserir("pets", documento)


@app.post("/prestadores")
def criar_prestador(prestador: Prestador):
    return _inserir("prestadores", prestador.model_dump())


@app.post("/visitas")
def criar_visita(visita: Visita):
    documento = visita.model_dump()
    documento["pet_id"] = _para_object_id(documento["pet_id"])
    documento["prestador_id"] = _para_object_id(documento["prestador_id"])
    # remove campos opcionais vazios, para não gravar nulos à toa
    documento = {chave: valor for chave, valor in documento.items() if valor is not None}
    return _inserir("visitas", documento)


# --- Listagem (GET) --------------------------------------------------
@app.get("/tutores")
def listar_tutores():
    return _listar("tutores")


@app.get("/pets")
def listar_pets():
    return _listar("pets")


@app.get("/prestadores")
def listar_prestadores():
    return _listar("prestadores")


@app.get("/visitas")
def listar_visitas():
    return _listar("visitas")
