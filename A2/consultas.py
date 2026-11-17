"""
[A2] Pipelines de agregação do Pet Center.

Autores: Henrique Souza e Yuri Cainã
"""
from database import banco


# ===== [A2] Serviços compatíveis com o pet =====
def servicos_compativeis(pet):
    condicoes = [
        {"$or": [
            {"servicos_oferecidos.especies_aceitas": pet.get("especie")},
            {"servicos_oferecidos.especies_aceitas": {"$size": 0}},
        ]},
        {"$or": [
            {"servicos_oferecidos.portes_aceitos": pet.get("porte")},
            {"servicos_oferecidos.portes_aceitos": {"$size": 0}},
        ]},
    ]
    if pet.get("possui_alergia"):
        condicoes.append({"servicos_oferecidos.aceita_animais_com_alergia_doenca": True})

    pipeline = [
        {"$unwind": "$servicos_oferecidos"},
        {"$match": {"$and": condicoes}},
        {"$lookup": {
            "from": "eventos",
            "localField": "servicos_oferecidos.servico_id",
            "foreignField": "servico_id",
            "pipeline": [{"$match": {"status": "Concluído"}}],
            "as": "contratacoes",
        }},
        {"$addFields": {"vezes_contratado": {"$size": "$contratacoes"}}},
        {"$sort": {"vezes_contratado": -1, "servicos_oferecidos.valor": 1}},
        {"$project": {
            "_id": 0,
            "prestador_id": "$_id",
            "prestador_nome": "$nome",
            "servico_id": "$servicos_oferecidos.servico_id",
            "tipo": "$servicos_oferecidos.tipo",
            "tempo_duracao": "$servicos_oferecidos.tempo_duracao",
            "max_diarias": "$servicos_oferecidos.max_diarias",
            "especies_aceitas": "$servicos_oferecidos.especies_aceitas",
            "portes_aceitos": "$servicos_oferecidos.portes_aceitos",
            "valor": "$servicos_oferecidos.valor",
            "aceita_animais_com_alergia_doenca":
                "$servicos_oferecidos.aceita_animais_com_alergia_doenca",
            "vezes_contratado": 1,
        }},
    ]
    return list(banco["prestadores"].aggregate(pipeline))


# ===== [A2] Faturamento do prestador =====
def faturamento_prestador(prestador_id):
    pipeline = [
        {"$match": {"prestador_id": prestador_id, "status": "Concluído"}},
        {"$group": {
            "_id": {
                "mes": {"$dateToString": {"format": "%Y-%m", "date": "$data_inicio"}},
                "tipo": "$tipo_evento",
            },
            "quantidade": {"$sum": 1},
            "faturamento": {"$sum": "$valor_total"},
            "ticket_medio": {"$avg": "$valor_total"},
        }},
        {"$sort": {"_id.mes": 1, "_id.tipo": 1}},
        {"$project": {
            "_id": 0,
            "mes": "$_id.mes",
            "tipo": "$_id.tipo",
            "quantidade": 1,
            "faturamento": 1,
            "ticket_medio": {"$round": ["$ticket_medio", 2]},
        }},
    ]
    return list(banco["eventos"].aggregate(pipeline))
