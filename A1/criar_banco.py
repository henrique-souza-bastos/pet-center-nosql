"""
A1 - Criação do banco no MongoDB Atlas
Pet Center: app de passeadores e hospedagem pet

Modelagem em 3 coleções:
- "tutores": dados do tutor + array "pets" EMBUTIDO.
- "prestadores": dados do prestador + array "servicos_oferecidos" EMBUTIDO.
- "eventos": agendamentos (passeio/hospedagem) numa coleção SEPARADA, que
  REFERENCIA tutor, prestador, serviço e pets, e guarda um SNAPSHOT com os
  nomes do momento do agendamento (para listar histórico sem join).

Cria o banco "patinhas_carinho", as coleções e insere documentos de exemplo.
Todos os dados são fictícios.

Autores: Henrique Souza e Yuri Cainã

Como rodar:  python criar_banco.py
"""
from datetime import datetime, timezone

from bson import ObjectId

from database import banco

COLECOES = ["tutores", "prestadores", "eventos"]
# coleções de modelagens anteriores, apagadas na migração
COLECOES_ANTIGAS = ["pets", "visitas"]


def data(texto):
    """Converte '2026-10-02 08:00' em data/hora (UTC) que o MongoDB entende."""
    return datetime.strptime(texto, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)


# ---------------------------------------------------------------------
# IDs criados antes, para um documento poder referenciar o outro.
# ---------------------------------------------------------------------
joao_id, joao_passeio30, joao_passeio60 = ObjectId(), ObjectId(), ObjectId()
casa_id, casa_diaria = ObjectId(), ObjectId()

ana_id, rex_id, mia_id = ObjectId(), ObjectId(), ObjectId()
bruno_id, thor_id = ObjectId(), ObjectId()


# ---------------------------------------------------------------------
# PRESTADORES - cada um com o seu catálogo de serviços embutido.
# Cada serviço traz as próprias restrições (espécies, portes, alergia).
# ---------------------------------------------------------------------
prestadores = [
    {
        "_id": joao_id,
        "nome": "João Passeios",
        "endereco": "Rua das Acácias, 250 - Santa Mônica, Uberlândia/MG",
        "telefone": "(34) 98888-0001",
        "data_nascimento": "1995-02-14",
        "tipos_servicos_gerais": "Passeio",
        "servicos_oferecidos": [
            {
                "servico_id": joao_passeio30,
                "tipo": "Passeio",
                "tempo_duracao": "30 min",
                "especies_aceitas": ["Cachorro"],
                "portes_aceitos": ["Pequeno", "Médio", "Grande"],
                "valor": 25.0,
                "aceita_animais_com_alergia_doenca": True,
            },
            {
                "servico_id": joao_passeio60,
                "tipo": "Passeio",
                "tempo_duracao": "60 min",
                "especies_aceitas": ["Cachorro"],
                "portes_aceitos": ["Médio", "Grande"],
                "valor": 40.0,
                "aceita_animais_com_alergia_doenca": False,
            },
        ],
    },
    {
        "_id": casa_id,
        "nome": "Casa do Pet Feliz",
        "endereco": "Av. Rondon Pacheco, 1200 - Centro, Uberlândia/MG",
        "telefone": "(34) 98888-0002",
        "data_nascimento": "1988-07-30",
        "tipos_servicos_gerais": "Hospedagem",
        "servicos_oferecidos": [
            {
                "servico_id": casa_diaria,
                "tipo": "Hospedagem",
                "max_diarias": 10,   # disponibilidade: o tutor pode pedir de 1 a 10
                "especies_aceitas": ["Cachorro", "Gato"],
                "portes_aceitos": ["Pequeno", "Médio"],
                "valor": 60.0,       # valor da DIÁRIA (o total é diária x quantidade)
                "aceita_animais_com_alergia_doenca": True,
            },
        ],
    },
]


# ---------------------------------------------------------------------
# TUTORES - cada tutor guarda os seus pets EMBUTIDOS.
# ---------------------------------------------------------------------
tutores = [
    {
        "_id": ana_id,
        "nome": "Ana Souza",
        "endereco": "Rua Goiás, 100 - Santa Mônica, Uberlândia/MG",
        "telefone": "(34) 99999-0001",
        "data_nascimento": "1990-05-20",
        "pets": [
            {
                "pet_id": rex_id,
                "nome": "Rex",
                "especie": "Cachorro",
                "raca": "Labrador",
                "peso_kg": 28.0,
                "porte": "Grande",
                "data_nascimento": {"data": "2019-03-10", "tipo": "Exata"},
                "possui_alergia": True,
                "detalhes_alergia": "Alergia a ração com frango.",
                "qtde_passeios_dia": 2,
                "observacoes": "Puxa bastante a guia no começo do passeio.",
            },
            {
                "pet_id": mia_id,
                "nome": "Mia",
                "especie": "Gato",
                "raca": "SRD",
                "peso_kg": 4.2,
                "porte": "Pequeno",
                "data_nascimento": {"data": "2020-01-01", "tipo": "Aproximada"},
                "possui_alergia": False,
                "detalhes_alergia": None,
                "qtde_passeios_dia": 1,
                "observacoes": "Gata de apartamento, não sai para passeios.",
            },
        ],
    },
    {
        "_id": bruno_id,
        "nome": "Bruno Lima",
        "endereco": "Rua Machado de Assis, 45 - Centro, Uberlândia/MG",
        "telefone": "(34) 99999-0002",
        "data_nascimento": "1985-11-02",
        "pets": [
            {
                "pet_id": thor_id,
                "nome": "Thor",
                "especie": "Cachorro",
                "raca": "SRD",
                "peso_kg": 15.0,
                "porte": "Médio",
                "data_nascimento": {"data": "2021-08-05", "tipo": "Aproximada"},
                "possui_alergia": False,
                "detalhes_alergia": None,
                "qtde_passeios_dia": 3,
                "observacoes": None,
            },
        ],
    },
]


# ---------------------------------------------------------------------
# EVENTOS - coleção separada. Guarda as REFERÊNCIAS (ids) e um SNAPSHOT
# com os nomes do momento do agendamento, para listar o histórico rápido.
# ---------------------------------------------------------------------
eventos = [
    {
        "evento_id": ObjectId(),
        "tipo_evento": "Passeio",
        "status": "Concluído",
        "data_inicio": data("2026-10-02 08:00"),
        "data_fim": data("2026-10-02 08:30"),
        "valor_total": 25.0,
        "tutor_id": ana_id,
        "prestador_id": joao_id,
        "servico_id": joao_passeio30,
        "pets_envolvidos": [rex_id],
        "snapshot": {
            "tutor_nome": "Ana Souza",
            "prestador_nome": "João Passeios",
            "pets_nomes": ["Rex"],
        },
    },
    {
        "evento_id": ObjectId(),
        "tipo_evento": "Hospedagem",
        "status": "Concluído",
        "data_inicio": data("2026-09-20 12:00"),
        "data_fim": data("2026-09-23 12:00"),
        "qtde_diarias": 3,            # 3 diárias x R$ 60,00 = R$ 180,00
        "valor_total": 180.0,
        "tutor_id": ana_id,
        "prestador_id": casa_id,
        "servico_id": casa_diaria,
        "pets_envolvidos": [mia_id],
        "snapshot": {
            "tutor_nome": "Ana Souza",
            "prestador_nome": "Casa do Pet Feliz",
            "pets_nomes": ["Mia"],
        },
    },
    {
        "evento_id": ObjectId(),
        "tipo_evento": "Passeio",
        "status": "Solicitado",
        "data_inicio": data("2026-11-10 17:00"),
        "data_fim": data("2026-11-10 18:00"),
        "valor_total": 40.0,
        "tutor_id": bruno_id,
        "prestador_id": joao_id,
        "servico_id": joao_passeio60,
        "pets_envolvidos": [thor_id],
        "snapshot": {
            "tutor_nome": "Bruno Lima",
            "prestador_nome": "João Passeios",
            "pets_nomes": ["Thor"],
        },
    },
]


def limpar_banco():
    """Apaga as coleções (inclusive as de modelagens antigas), para rodar de novo."""
    for nome in COLECOES + COLECOES_ANTIGAS:
        banco.drop_collection(nome)


def criar_colecoes():
    """Cria as coleções com uma validação mínima dos campos essenciais."""
    banco.create_collection(
        "tutores",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["nome", "telefone"],
                "properties": {"pets": {"bsonType": "array"}},
            }
        },
    )
    banco.create_collection(
        "prestadores",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["nome", "tipos_servicos_gerais"],
                "properties": {"servicos_oferecidos": {"bsonType": "array"}},
            }
        },
    )
    banco.create_collection(
        "eventos",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["tipo_evento", "status", "tutor_id", "prestador_id"],
                "properties": {
                    "tipo_evento": {"enum": ["Passeio", "Hospedagem"]},
                    "status": {
                        "enum": [
                            "Solicitado", "Confirmado", "Em Andamento",
                            "Concluído", "Cancelado",
                        ]
                    },
                },
            }
        },
    )


def inserir_documentos():
    banco["prestadores"].insert_many(prestadores)
    banco["tutores"].insert_many(tutores)
    banco["eventos"].insert_many(eventos)


def mostrar_resumo():
    print(f"Banco '{banco.name}' criado com sucesso:")
    n_pets = sum(len(t.get("pets", [])) for t in banco["tutores"].find())
    n_servicos = sum(
        len(p.get("servicos_oferecidos", [])) for p in banco["prestadores"].find()
    )
    print(f"  - tutores: {banco['tutores'].count_documents({})}")
    print(f"      pets embutidos: {n_pets}")
    print(f"  - prestadores: {banco['prestadores'].count_documents({})}")
    print(f"      serviços embutidos: {n_servicos}")
    print(f"  - eventos: {banco['eventos'].count_documents({})}")


if __name__ == "__main__":
    limpar_banco()
    criar_colecoes()
    inserir_documentos()
    mostrar_resumo()
