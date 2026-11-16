"""
[A2] Consultas com PIPELINE DE AGREGAÇÃO do Pet Center.

ARQUIVO 100% NOVO NA A2 - é aqui que estão as duas funcionalidades pedidas.

Um pipeline de agregação é uma "linha de montagem": o MongoDB pega os
documentos de uma coleção e passa por várias etapas em sequência (filtrar,
abrir arrays, juntar com outra coleção, agrupar, ordenar...). A saída de uma
etapa é a entrada da próxima, e todo o trabalho é feito DENTRO do banco.

As duas funcionalidades usam pipelines bem diferentes:

1) servicos_compativeis  (para o TUTOR)
   Parte da coleção "prestadores". ABRE o array embutido de serviços, FILTRA
   pelos que aceitam o pet escolhido e JUNTA com a coleção "eventos" para
   saber quantas vezes cada serviço já foi contratado.
   Etapas: $unwind -> $match -> $lookup -> $addFields -> $sort -> $project

2) faturamento_prestador  (para o PRESTADOR)
   Parte da coleção "eventos". FILTRA os serviços concluídos do prestador e
   AGRUPA por mês e por tipo, somando o faturamento.
   Etapas: $match -> $group -> $sort -> $project

Autores: Henrique Souza e Yuri Cainã

Como é usado: este arquivo não roda sozinho. As rotas [A2] do main.py chamam
as funções daqui.
"""
from database import banco


# =====================================================================
# [A2] FUNCIONALIDADE 1 - Serviços compatíveis com o pet (perfil TUTOR)
# =====================================================================
def servicos_compativeis(pet):
    """
    Devolve só os serviços que aceitam esse pet, dos mais contratados para os
    menos contratados.

    Na A1 o tutor via a vitrine inteira e só descobria que o pet não era
    aceito quando a API recusava o pedido. Aqui o próprio banco já entrega a
    lista filtrada.
    """
    # As regras são as mesmas da função _conferir_compatibilidade (main.py):
    # lista vazia de espécies/portes significa "aceita todos".
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
    # Só restringe por alergia/doença se o pet realmente tiver.
    if pet.get("possui_alergia"):
        condicoes.append(
            {"servicos_oferecidos.aceita_animais_com_alergia_doenca": True}
        )

    pipeline = [
        # 1) $unwind: "abre" o array embutido. Um prestador com 3 serviços
        #    vira 3 documentos, cada um com 1 serviço. Sem isso o filtro
        #    devolveria o prestador inteiro, e não o serviço que serve.
        {"$unwind": "$servicos_oferecidos"},

        # 2) $match: fica só com os serviços que aceitam o pet.
        {"$match": {"$and": condicoes}},

        # 3) $lookup: junta com a coleção "eventos" (é o "join" do MongoDB).
        #    Para cada serviço, traz os eventos CONCLUÍDOS daquele serviço.
        #    Só os concluídos contam como contratação de verdade.
        {"$lookup": {
            "from": "eventos",
            "localField": "servicos_oferecidos.servico_id",
            "foreignField": "servico_id",
            "pipeline": [{"$match": {"status": "Concluído"}}],
            "as": "contratacoes",
        }},

        # 4) $addFields: cria um campo novo com a quantidade de contratações.
        {"$addFields": {"vezes_contratado": {"$size": "$contratacoes"}}},

        # 5) $sort: mais contratados primeiro; no empate, o mais barato.
        {"$sort": {"vezes_contratado": -1, "servicos_oferecidos.valor": 1}},

        # 6) $project: escolhe o formato da resposta - o mesmo da vitrine
        #    (/servicos), para a tela reaproveitar o que já existia.
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


# =====================================================================
# [A2] FUNCIONALIDADE 2 - Painel de faturamento (perfil PRESTADOR)
# =====================================================================
def faturamento_prestador(prestador_id):
    """
    Resume quanto o prestador faturou, mês a mês e por tipo de serviço:
    quantidade de serviços, total faturado e ticket médio (valor médio por
    serviço).

    prestador_id precisa chegar como ObjectId (a rota do main.py converte).
    """
    pipeline = [
        # 1) $match: só os eventos desse prestador que foram CONCLUÍDOS.
        #    Solicitado/Confirmado ainda não aconteceram e Cancelado não
        #    gera receita, então não entram no faturamento.
        {"$match": {"prestador_id": prestador_id, "status": "Concluído"}},

        # 2) $group: junta os eventos em "caixinhas" de mês + tipo e calcula
        #    os totais de cada caixinha. $dateToString transforma a data
        #    completa em "2026-10" para todos os dias do mês caírem juntos.
        {"$group": {
            "_id": {
                "mes": {"$dateToString": {"format": "%Y-%m", "date": "$data_inicio"}},
                "tipo": "$tipo_evento",
            },
            "quantidade": {"$sum": 1},
            "faturamento": {"$sum": "$valor_total"},
            "ticket_medio": {"$avg": "$valor_total"},
        }},

        # 3) $sort: ordem cronológica e, dentro do mês, por tipo.
        {"$sort": {"_id.mes": 1, "_id.tipo": 1}},

        # 4) $project: tira os campos de dentro do "_id" do grupo e arredonda
        #    o ticket médio para 2 casas (centavos).
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
