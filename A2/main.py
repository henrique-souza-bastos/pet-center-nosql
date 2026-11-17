"""
API do Pet Center (FastAPI).

[A2] Rotas novas no fim do arquivo: servicos-compativeis e faturamento.

Autores: Henrique Souza e Yuri Cainã

Como rodar: uvicorn main:app --reload  (docs em http://localhost:8000/docs)
"""
import re
from datetime import timedelta
from typing import Optional

from bson import ObjectId
from fastapi import FastAPI, HTTPException

import consultas  # [A2]
from database import banco
from modelos import (
    STATUS_EVENTO,
    AtualizacaoStatus,
    EventoSolicitacao,
    Pet,
    Prestador,
    ServicoOferecido,
    Tutor,
)

app = FastAPI(title="Pet Center")


def _id_valido(valor):
    try:
        return ObjectId(valor)
    except Exception:
        raise HTTPException(status_code=400, detail=f"id inválido: {valor}")


def _limpar(documento):
    if isinstance(documento, list):
        return [_limpar(item) for item in documento]
    if isinstance(documento, dict):
        return {chave: _limpar(valor) for chave, valor in documento.items()}
    if isinstance(documento, ObjectId):
        return str(documento)
    return documento


# ===== LOGIN =====
def _normalizar_usuario(texto):
    usuario = (texto or "").strip().lower()
    if not re.fullmatch(r"[a-z0-9._-]{3,30}", usuario):
        raise HTTPException(
            status_code=400,
            detail="O usuário deve ter de 3 a 30 caracteres, usando só letras sem "
                   "acento, números, ponto, hífen ou sublinhado (ex.: ana.souza).",
        )
    return usuario


def _conferir_usuario_livre(usuario):
    for colecao in ("tutores", "prestadores"):
        if banco[colecao].find_one({"usuario": usuario}, {"_id": 1}):
            raise HTTPException(
                status_code=409,
                detail=f"O usuário '{usuario}' já está em uso. Escolha outro.",
            )


@app.get("/login/{usuario}")
def entrar(usuario: str):
    usuario = usuario.strip().lower()
    for colecao, perfil in (("tutores", "Tutor"), ("prestadores", "Prestador")):
        conta = banco[colecao].find_one({"usuario": usuario})
        if conta:
            return {"perfil": perfil, "dados": _limpar(conta)}
    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado. Confira o nome digitado ou crie uma conta.",
    )


# ===== TUTORES =====
@app.post("/tutores")
def criar_tutor(tutor: Tutor):
    documento = tutor.model_dump()
    documento["usuario"] = _normalizar_usuario(tutor.usuario)
    _conferir_usuario_livre(documento["usuario"])
    for pet in documento.get("pets", []):
        pet["pet_id"] = ObjectId()
    try:
        resultado = banco["tutores"].insert_one(documento)
        return {"mensagem": "Tutor cadastrado!", "id": str(resultado.inserted_id)}
    except Exception as erro:
        raise HTTPException(status_code=500, detail=str(erro))


@app.get("/tutores")
def listar_tutores():
    return _limpar(list(banco["tutores"].find().limit(100)))


@app.post("/tutores/{tutor_id}/pets")
def adicionar_pet(tutor_id: str, pet: Pet):
    documento = pet.model_dump()
    documento["pet_id"] = ObjectId()
    resultado = banco["tutores"].update_one(
        {"_id": _id_valido(tutor_id)},
        {"$push": {"pets": documento}},
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    return {"mensagem": "Pet adicionado ao tutor!", "pet_id": str(documento["pet_id"])}


# ===== PRESTADORES =====
@app.post("/prestadores")
def criar_prestador(prestador: Prestador):
    documento = prestador.model_dump()
    documento["usuario"] = _normalizar_usuario(prestador.usuario)
    _conferir_usuario_livre(documento["usuario"])
    for servico in documento.get("servicos_oferecidos", []):
        servico["servico_id"] = ObjectId()
    try:
        resultado = banco["prestadores"].insert_one(documento)
        return {"mensagem": "Prestador cadastrado!", "id": str(resultado.inserted_id)}
    except Exception as erro:
        raise HTTPException(status_code=500, detail=str(erro))


@app.get("/prestadores")
def listar_prestadores():
    return _limpar(list(banco["prestadores"].find().limit(100)))


@app.post("/prestadores/{prestador_id}/servicos")
def adicionar_servico(prestador_id: str, servico: ServicoOferecido):
    if servico.tipo not in ("Passeio", "Hospedagem"):
        raise HTTPException(status_code=400, detail="Tipo deve ser Passeio ou Hospedagem")
    if servico.tipo == "Hospedagem" and not servico.max_diarias:
        raise HTTPException(
            status_code=400,
            detail="Na hospedagem, informe quantas diárias estão disponíveis (1 a 10).",
        )
    documento = servico.model_dump()
    documento["servico_id"] = ObjectId()
    resultado = banco["prestadores"].update_one(
        {"_id": _id_valido(prestador_id)},
        {"$push": {"servicos_oferecidos": documento}},
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Prestador não encontrado")
    return {
        "mensagem": "Serviço adicionado ao prestador!",
        "servico_id": str(documento["servico_id"]),
    }


@app.get("/servicos")
def listar_servicos():
    catalogo = []
    for prestador in banco["prestadores"].find():
        for servico in prestador.get("servicos_oferecidos", []):
            item = _limpar(dict(servico))
            item["prestador_id"] = str(prestador["_id"])
            item["prestador_nome"] = prestador.get("nome")
            catalogo.append(item)
    return catalogo


# ===== EVENTOS =====
def _conferir_compatibilidade(pet, servico):
    nome = pet.get("nome", "pet")
    especies = servico.get("especies_aceitas") or []
    portes = servico.get("portes_aceitos") or []
    if especies and pet.get("especie") not in especies:
        return f"{nome} é {pet.get('especie')} e o serviço aceita: {', '.join(especies)}."
    if portes and pet.get("porte") not in portes:
        return f"{nome} é de porte {pet.get('porte')} e o serviço aceita: {', '.join(portes)}."
    if pet.get("possui_alergia") and not servico.get("aceita_animais_com_alergia_doenca"):
        return f"{nome} tem alergia/doença e esse serviço não aceita."
    return None


@app.post("/eventos")
def solicitar_evento(pedido: EventoSolicitacao):
    tutor = banco["tutores"].find_one({"_id": _id_valido(pedido.tutor_id)})
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")

    prestador = banco["prestadores"].find_one({"_id": _id_valido(pedido.prestador_id)})
    if not prestador:
        raise HTTPException(status_code=404, detail="Prestador não encontrado")

    servico = next(
        (
            s for s in prestador.get("servicos_oferecidos", [])
            if str(s.get("servico_id")) == pedido.servico_id
        ),
        None,
    )
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado nesse prestador")

    ids_pets = set(pedido.pets_envolvidos)
    pets = [p for p in tutor.get("pets", []) if str(p.get("pet_id")) in ids_pets]
    if not pets:
        raise HTTPException(status_code=400, detail="Escolha pelo menos um pet seu.")

    for pet in pets:
        problema = _conferir_compatibilidade(pet, servico)
        if problema:
            raise HTTPException(status_code=400, detail=problema)

    if servico.get("tipo") == "Hospedagem":
        diarias = pedido.qtde_diarias or 1
        disponiveis = servico.get("max_diarias") or 10
        if diarias > disponiveis:
            raise HTTPException(
                status_code=400,
                detail=f"Esse serviço tem no máximo {disponiveis} diárias disponíveis.",
            )
        valor_total = float(servico.get("valor", 0)) * diarias
        data_fim = pedido.data_inicio + timedelta(days=diarias)
    else:
        diarias = None
        valor_total = float(servico.get("valor", 0))
        data_fim = pedido.data_inicio

    documento = {
        "evento_id": ObjectId(),
        "tipo_evento": servico.get("tipo"),
        "status": "Solicitado",
        "data_inicio": pedido.data_inicio,
        "data_fim": data_fim,
        "qtde_diarias": diarias,
        "valor_total": valor_total,
        "tutor_id": tutor["_id"],
        "prestador_id": prestador["_id"],
        "servico_id": servico.get("servico_id"),
        "pets_envolvidos": [p["pet_id"] for p in pets],
        "snapshot": {
            "tutor_nome": tutor.get("nome"),
            "prestador_nome": prestador.get("nome"),
            "pets_nomes": [p.get("nome") for p in pets],
        },
    }
    try:
        resultado = banco["eventos"].insert_one(documento)
        return {
            "mensagem": "Solicitação enviada! Aguarde o prestador aceitar.",
            "id": str(resultado.inserted_id),
            "valor_total": valor_total,
        }
    except Exception as erro:
        raise HTTPException(status_code=500, detail=str(erro))


@app.get("/eventos")
def listar_eventos(
    tutor_id: Optional[str] = None,
    prestador_id: Optional[str] = None,
    status: Optional[str] = None,
):
    filtro = {}
    if tutor_id:
        filtro["tutor_id"] = _id_valido(tutor_id)
    if prestador_id:
        filtro["prestador_id"] = _id_valido(prestador_id)
    if status:
        filtro["status"] = status
    return _limpar(list(banco["eventos"].find(filtro).sort("data_inicio", 1).limit(100)))


@app.patch("/eventos/{evento_id}/status")
def atualizar_status(evento_id: str, atualizacao: AtualizacaoStatus):
    if atualizacao.status not in STATUS_EVENTO:
        raise HTTPException(
            status_code=400,
            detail=f"Status inválido. Use um destes: {', '.join(STATUS_EVENTO)}",
        )
    resultado = banco["eventos"].update_one(
        {"_id": _id_valido(evento_id)},
        {"$set": {"status": atualizacao.status}},
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return {"mensagem": f"Evento agora está como '{atualizacao.status}'."}


# ===== [A2] ROTAS NOVAS =====
@app.get("/tutores/{tutor_id}/pets/{pet_id}/servicos-compativeis")
def listar_servicos_compativeis(tutor_id: str, pet_id: str):
    tutor = banco["tutores"].find_one({"_id": _id_valido(tutor_id)})
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")

    pet = next(
        (p for p in tutor.get("pets", []) if str(p.get("pet_id")) == pet_id),
        None,
    )
    if not pet:
        raise HTTPException(
            status_code=404,
            detail="Pet não encontrado: ele precisa estar cadastrado nesse tutor.",
        )
    return _limpar(consultas.servicos_compativeis(pet))


@app.get("/prestadores/{prestador_id}/faturamento")
def consultar_faturamento(prestador_id: str):
    id_prestador = _id_valido(prestador_id)
    if not banco["prestadores"].find_one({"_id": id_prestador}, {"_id": 1}):
        raise HTTPException(status_code=404, detail="Prestador não encontrado")
    return consultas.faturamento_prestador(id_prestador)
# ===== fim [A2] =====
