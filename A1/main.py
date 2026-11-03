"""
API (FastAPI) do Pet Center.

Segue o modelo aninhado:
- um PET é criado DENTRO de um tutor;
- uma VISITA é criada DENTRO de um pet.
Os PRESTADORES ficam numa coleção separada.

Autores: Henrique Souza e Yuri Cainã

Como rodar:  uvicorn main:app --reload
Documentação automática (teste pelo navegador):  http://localhost:8000/docs
"""
from bson import ObjectId
from fastapi import FastAPI, HTTPException

from database import banco
from modelos import Pet, Prestador, Tutor, Visita

app = FastAPI(title="Pet Center")


def _id_valido(valor):
    """Converte texto em ObjectId; devolve erro 400 se o id for inválido."""
    try:
        return ObjectId(valor)
    except Exception:
        raise HTTPException(status_code=400, detail="id inválido")


def _limpar(documento):
    """Converte ObjectId em texto (recursivo) para poder devolver em JSON."""
    if isinstance(documento, list):
        return [_limpar(item) for item in documento]
    if isinstance(documento, dict):
        return {chave: _limpar(valor) for chave, valor in documento.items()}
    if isinstance(documento, ObjectId):
        return str(documento)
    return documento


# ---------------------------------------------------------------------
# TUTORES (coleção principal)
# ---------------------------------------------------------------------
@app.post("/tutores")
def criar_tutor(tutor: Tutor):
    try:
        resultado = banco["tutores"].insert_one(tutor.model_dump())
        return {"mensagem": "Tutor cadastrado!", "id": str(resultado.inserted_id)}
    except Exception as erro:
        raise HTTPException(status_code=500, detail=str(erro))


@app.get("/tutores")
def listar_tutores():
    return _limpar(list(banco["tutores"].find().limit(50)))


# ---------------------------------------------------------------------
# PETS (ficam dentro de um tutor)
# ---------------------------------------------------------------------
@app.post("/tutores/{tutor_id}/pets")
def adicionar_pet(tutor_id: str, pet: Pet):
    documento = pet.model_dump()
    documento["_id"] = ObjectId()  # id próprio do pet, para localizá-lo depois
    resultado = banco["tutores"].update_one(
        {"_id": _id_valido(tutor_id)},
        {"$push": {"pets": documento}},
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    return {"mensagem": "Pet adicionado ao tutor!", "pet_id": str(documento["_id"])}


# ---------------------------------------------------------------------
# VISITAS (ficam dentro de um pet)
# ---------------------------------------------------------------------
@app.post("/tutores/{tutor_id}/pets/{pet_id}/visitas")
def adicionar_visita(tutor_id: str, pet_id: str, visita: Visita):
    documento = visita.model_dump()
    documento["prestador_id"] = _id_valido(documento["prestador_id"])
    documento = {chave: valor for chave, valor in documento.items() if valor is not None}
    resultado = banco["tutores"].update_one(
        {"_id": _id_valido(tutor_id)},
        {"$push": {"pets.$[p].visitas": documento}},
        array_filters=[{"p._id": _id_valido(pet_id)}],
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    if resultado.modified_count == 0:
        raise HTTPException(status_code=404, detail="Pet não encontrado nesse tutor")
    return {"mensagem": "Visita adicionada ao pet!"}


# ---------------------------------------------------------------------
# PRESTADORES (coleção separada)
# ---------------------------------------------------------------------
@app.post("/prestadores")
def criar_prestador(prestador: Prestador):
    try:
        resultado = banco["prestadores"].insert_one(prestador.model_dump())
        return {"mensagem": "Prestador cadastrado!", "id": str(resultado.inserted_id)}
    except Exception as erro:
        raise HTTPException(status_code=500, detail=str(erro))


@app.get("/prestadores")
def listar_prestadores():
    return _limpar(list(banco["prestadores"].find().limit(50)))
