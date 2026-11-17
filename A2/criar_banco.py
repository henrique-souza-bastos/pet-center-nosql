from datetime import datetime, timedelta, timezone

from bson import ObjectId

from database import banco

COLECOES = ["tutores", "prestadores", "eventos"]
COLECOES_ANTIGAS = ["pets", "visitas"]


def data(texto):
    return datetime.strptime(texto, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)


joao_id, joao_passeio30, joao_passeio60 = ObjectId(), ObjectId(), ObjectId()
casa_id, casa_diaria = ObjectId(), ObjectId()

ana_id, rex_id, mia_id = ObjectId(), ObjectId(), ObjectId()
bruno_id, thor_id = ObjectId(), ObjectId()


prestadores = [
    {
        "_id": joao_id,
        "usuario": "joao.passeios",
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
        "usuario": "casa.petfeliz",
        "nome": "Casa do Pet Feliz",
        "endereco": "Av. Rondon Pacheco, 1200 - Centro, Uberlândia/MG",
        "telefone": "(34) 98888-0002",
        "data_nascimento": "1988-07-30",
        "tipos_servicos_gerais": "Hospedagem",
        "servicos_oferecidos": [
            {
                "servico_id": casa_diaria,
                "tipo": "Hospedagem",
                "max_diarias": 10,
                "especies_aceitas": ["Cachorro", "Gato"],
                "portes_aceitos": ["Pequeno", "Médio"],
                "valor": 60.0,
                "aceita_animais_com_alergia_doenca": True,
            },
        ],
    },
]


tutores = [
    {
        "_id": ana_id,
        "usuario": "ana.souza",
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
        "usuario": "bruno.lima",
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
        "qtde_diarias": 3,
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


patas_id, patas_passeio45, patas_diaria = ObjectId(), ObjectId(), ObjectId()
carla_id, luna_id, bolt_id = ObjectId(), ObjectId(), ObjectId()

prestadores.append({
    "_id": patas_id,
    "usuario": "patas.cia",
    "nome": "Patas & Cia",
    "endereco": "Rua Tapuirama, 780 - Osvaldo Rezende, Uberlândia/MG",
    "telefone": "(34) 98888-0003",
    "data_nascimento": "1992-09-18",
    "tipos_servicos_gerais": "Ambos",
    "servicos_oferecidos": [
        {
            "servico_id": patas_passeio45,
            "tipo": "Passeio",
            "tempo_duracao": "45 min",
            "especies_aceitas": ["Cachorro"],
            "portes_aceitos": ["Pequeno", "Médio"],
            "valor": 30.0,
            "aceita_animais_com_alergia_doenca": False,
        },
        {
            "servico_id": patas_diaria,
            "tipo": "Hospedagem",
            "max_diarias": 5,
            "especies_aceitas": ["Cachorro", "Gato"],
            "portes_aceitos": ["Pequeno", "Médio", "Grande"],
            "valor": 80.0,
            "aceita_animais_com_alergia_doenca": True,
        },
    ],
})

tutores.append({
    "_id": carla_id,
    "usuario": "carla.mendes",
    "nome": "Carla Mendes",
    "endereco": "Av. Segismundo Pereira, 310 - Santa Mônica, Uberlândia/MG",
    "telefone": "(34) 99999-0003",
    "data_nascimento": "1998-03-27",
    "pets": [
        {
            "pet_id": luna_id,
            "nome": "Luna",
            "especie": "Gato",
            "raca": "Siamês",
            "peso_kg": 3.8,
            "porte": "Pequeno",
            "data_nascimento": {"data": "2022-06-15", "tipo": "Exata"},
            "possui_alergia": True,
            "detalhes_alergia": "Dermatite: usa shampoo medicinal.",
            "qtde_passeios_dia": 1,
            "observacoes": "Assusta com barulho alto.",
        },
        {
            "pet_id": bolt_id,
            "nome": "Bolt",
            "especie": "Cachorro",
            "raca": "Shih-tzu",
            "peso_kg": 6.5,
            "porte": "Pequeno",
            "data_nascimento": {"data": "2023-02-01", "tipo": "Aproximada"},
            "possui_alergia": False,
            "detalhes_alergia": None,
            "qtde_passeios_dia": 2,
            "observacoes": None,
        },
    ],
})

NOMES = {
    joao_id: "João Passeios", casa_id: "Casa do Pet Feliz", patas_id: "Patas & Cia",
    ana_id: "Ana Souza", bruno_id: "Bruno Lima", carla_id: "Carla Mendes",
    rex_id: "Rex", mia_id: "Mia", thor_id: "Thor", luna_id: "Luna", bolt_id: "Bolt",
}


def evento_extra(status, inicio, tutor, prestador, servico, pet, valor,
                 minutos=None, diarias=None):
    comeco = data(inicio)
    documento = {
        "evento_id": ObjectId(),
        "tipo_evento": "Hospedagem" if diarias else "Passeio",
        "status": status,
        "data_inicio": comeco,
        "data_fim": comeco + (timedelta(days=diarias) if diarias
                              else timedelta(minutes=minutos)),
        "valor_total": valor * diarias if diarias else valor,
        "tutor_id": tutor,
        "prestador_id": prestador,
        "servico_id": servico,
        "pets_envolvidos": [pet],
        "snapshot": {
            "tutor_nome": NOMES[tutor],
            "prestador_nome": NOMES[prestador],
            "pets_nomes": [NOMES[pet]],
        },
    }
    if diarias:
        documento["qtde_diarias"] = diarias
    return documento


eventos += [
    evento_extra("Concluído", "2026-08-05 08:00", ana_id, joao_id, joao_passeio30, rex_id, 25.0, minutos=30),
    evento_extra("Concluído", "2026-08-19 17:00", bruno_id, joao_id, joao_passeio60, thor_id, 40.0, minutos=60),
    evento_extra("Concluído", "2026-09-03 17:00", bruno_id, joao_id, joao_passeio60, thor_id, 40.0, minutos=60),
    evento_extra("Concluído", "2026-09-17 09:00", carla_id, joao_id, joao_passeio30, bolt_id, 25.0, minutos=30),
    evento_extra("Concluído", "2026-10-15 17:30", bruno_id, joao_id, joao_passeio30, thor_id, 25.0, minutos=30),
    evento_extra("Cancelado", "2026-10-22 08:00", ana_id, joao_id, joao_passeio30, rex_id, 25.0, minutos=30),
    evento_extra("Confirmado", "2026-11-25 09:00", carla_id, joao_id, joao_passeio30, bolt_id, 25.0, minutos=30),
    evento_extra("Concluído", "2026-08-10 12:00", carla_id, casa_id, casa_diaria, luna_id, 60.0, diarias=2),
    evento_extra("Concluído", "2026-10-05 12:00", bruno_id, casa_id, casa_diaria, thor_id, 60.0, diarias=4),
    evento_extra("Concluído", "2026-10-20 12:00", carla_id, casa_id, casa_diaria, bolt_id, 60.0, diarias=1),
    evento_extra("Confirmado", "2026-12-20 12:00", ana_id, casa_id, casa_diaria, mia_id, 60.0, diarias=5),
    evento_extra("Concluído", "2026-09-12 10:00", carla_id, patas_id, patas_passeio45, bolt_id, 30.0, minutos=45),
    evento_extra("Concluído", "2026-10-08 18:00", bruno_id, patas_id, patas_passeio45, thor_id, 30.0, minutos=45),
    evento_extra("Concluído", "2026-10-10 12:00", ana_id, patas_id, patas_diaria, rex_id, 80.0, diarias=3),
    evento_extra("Concluído", "2026-11-02 12:00", carla_id, patas_id, patas_diaria, luna_id, 80.0, diarias=2),
    evento_extra("Cancelado", "2026-11-05 10:00", carla_id, patas_id, patas_passeio45, bolt_id, 30.0, minutos=45),
    evento_extra("Solicitado", "2026-11-28 18:00", bruno_id, patas_id, patas_passeio45, thor_id, 30.0, minutos=45),
]


def limpar_banco():
    for nome in COLECOES + COLECOES_ANTIGAS:
        banco.drop_collection(nome)


def criar_colecoes():
    banco.create_collection(
        "tutores",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["usuario", "nome", "telefone"],
                "properties": {"pets": {"bsonType": "array"}},
            }
        },
    )
    banco.create_collection(
        "prestadores",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["usuario", "nome", "tipos_servicos_gerais"],
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


def criar_indices():
    banco["tutores"].create_index("usuario", unique=True)
    banco["prestadores"].create_index("usuario", unique=True)


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
    criar_indices()
    inserir_documentos()
    mostrar_resumo()
