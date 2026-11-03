"""
A1 - Criação do banco no MongoDB Atlas
Pet Center: app de passeadores e hospedagem pet

Estrutura de documento ANINHADA: cada TUTOR guarda seus PETS, e cada pet guarda
suas VISITAS. Os PRESTADORES ficam numa coleção separada.

Cria o banco "patinhas_carinho", as coleções e insere documentos de exemplo.
Todos os dados são fictícios.

Autores: Henrique Souza e Yuri Cainã

Como rodar:  python criar_banco.py
"""
from datetime import datetime, timezone

from bson import ObjectId

from database import banco

COLECOES = ["tutores", "prestadores"]
# coleções do modelo antigo (separado), apagadas numa eventual migração
COLECOES_ANTIGAS = ["pets", "visitas"]


def data(texto):
    """Converte '2026-10-02 08:00' em data/hora (UTC) que o MongoDB entende."""
    return datetime.strptime(texto, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)


# ---------------------------------------------------------------------
# PRESTADORES - coleção separada. Criados antes para as visitas poderem
# referenciá-los pelo id. "localizacao" usa GeoJSON [longitude, latitude].
# ---------------------------------------------------------------------
passeador_joao = ObjectId()
hospedagem_casa = ObjectId()

prestadores = [
    {
        "_id": passeador_joao,
        "tipo": "passeador",
        "nome": "João Passeios",
        "localizacao": {"type": "Point", "coordinates": [-48.278, -18.915]},
        "especies_aceitas": ["cao"],
        "servicos": [
            {"nome": "Passeio 30 min", "preco": 25.0},
            {"nome": "Passeio 60 min", "preco": 40.0},
        ],
    },
    {
        "_id": hospedagem_casa,
        "tipo": "hospedagem",
        "nome": "Casa do Pet Feliz",
        "localizacao": {"type": "Point", "coordinates": [-48.265, -18.925]},
        "especies_aceitas": ["cao", "gato", "coelho"],
        "capacidade": 6,
        "servicos": [
            {"nome": "Diária cão", "preco": 60.0},
            {"nome": "Diária gato", "preco": 45.0},
        ],
    },
]

# ---------------------------------------------------------------------
# TUTORES - cada tutor guarda seus pets, e cada pet guarda suas visitas.
# Tudo em um único documento (modelo aninhado / agregado).
# ---------------------------------------------------------------------
tutores = [
    {
        "_id": ObjectId(),
        "nome": "Ana Souza",
        "email": "ana@exemplo.com",
        "telefone": "(34) 99999-0001",
        "endereco": {"bairro": "Santa Mônica", "cidade": "Uberlândia", "uf": "MG"},
        "pets": [
            {
                "_id": ObjectId(),
                "nome": "Rex",
                "especie": "cao",
                "raca": "Labrador",
                "porte": "grande",
                "peso_kg": 28,
                "alergias": ["frango"],
                "medicamentos": [{"nome": "Condroitina", "horarios": ["08:00", "20:00"]}],
                "comportamento": {"agressivo_com_machos": False, "castrado": True},
                "visitas": [
                    {
                        "tipo": "passeio",
                        "status": "concluida",
                        "prestador_id": passeador_joao,
                        "prestador_nome": "João Passeios",
                        "inicio": data("2026-10-02 08:00"),
                        "fim": data("2026-10-02 08:30"),
                        "trajeto": {
                            "type": "LineString",
                            "coordinates": [[-48.278, -18.915], [-48.277, -18.916], [-48.276, -18.917]],
                        },
                        "ocorrencias": [
                            {"tipo": "xixi", "hora": "08:12"},
                            {"tipo": "coco", "hora": "08:20"},
                        ],
                        "fotos": ["https://exemplo.com/fotos/rex1.jpg"],
                        "observacoes": "Brincou bem com outros cães.",
                        "valor": 25.0,
                        "avaliacao": {"nota": 5, "comentario": "Ótimo passeio!"},
                    },
                    {
                        "tipo": "passeio",
                        "status": "concluida",
                        "prestador_id": passeador_joao,
                        "prestador_nome": "João Passeios",
                        "inicio": data("2026-10-05 17:00"),
                        "fim": data("2026-10-05 18:00"),
                        "trajeto": {
                            "type": "LineString",
                            "coordinates": [[-48.278, -18.915], [-48.279, -18.914]],
                        },
                        "ocorrencias": [{"tipo": "xixi", "hora": "17:10"}],
                        "fotos": [],
                        "valor": 40.0,
                        "avaliacao": {"nota": 4},
                    },
                ],
            },
            {
                "_id": ObjectId(),
                "nome": "Mia",
                "especie": "gato",
                "raca": "SRD",
                "alergias": [],
                "indoor": True,  # campo que só faz sentido para gatos
                "visitas": [
                    {
                        "tipo": "hospedagem",  # tem "diario" em vez de "trajeto"
                        "status": "concluida",
                        "prestador_id": hospedagem_casa,
                        "prestador_nome": "Casa do Pet Feliz",
                        "inicio": data("2026-09-20 12:00"),
                        "fim": data("2026-09-23 12:00"),
                        "diario": [
                            {"data": "2026-09-20", "alimentacao": "ração 2x", "humor": "arisca",
                             "observacoes": "Se escondeu no primeiro dia."},
                            {"data": "2026-09-21", "alimentacao": "ração 2x", "humor": "calma"},
                            {"data": "2026-09-22", "alimentacao": "ração 2x", "humor": "brincalhona"},
                        ],
                        "fotos": ["https://exemplo.com/fotos/mia1.jpg", "https://exemplo.com/fotos/mia2.jpg"],
                        "valor": 135.0,
                        "avaliacao": {"nota": 5, "comentario": "A Mia voltou tranquila."},
                    },
                ],
            },
        ],
    },
    {
        "_id": ObjectId(),
        "nome": "Bruno Lima",
        "email": "bruno@exemplo.com",
        "telefone": "(34) 99999-0002",
        "endereco": {"bairro": "Centro", "cidade": "Uberlândia", "uf": "MG"},
        "pets": [
            {
                "_id": ObjectId(),
                "nome": "Pipoca",
                "especie": "coelho",
                "dieta": {"feno": True, "racao_g_dia": 40},  # sem "raca", sem "porte"
                "visitas": [],  # ainda sem visitas
            },
        ],
    },
]


def limpar_banco():
    """Apaga as coleções (inclusive as do modelo antigo), para poder rodar de novo."""
    for nome in COLECOES + COLECOES_ANTIGAS:
        banco.drop_collection(nome)


def criar_colecoes():
    """Cria as coleções com uma validação mínima (campos essenciais)."""
    banco.create_collection(
        "tutores",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["nome", "email"],
                "properties": {"pets": {"bsonType": "array"}},
            }
        },
    )
    banco.create_collection(
        "prestadores",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["tipo", "nome"],
                "properties": {"tipo": {"enum": ["passeador", "hospedagem"]}},
            }
        },
    )


def inserir_documentos():
    banco["prestadores"].insert_many(prestadores)
    banco["tutores"].insert_many(tutores)


def mostrar_resumo():
    print(f"Banco '{banco.name}' criado com sucesso:")
    n_tutores = banco["tutores"].count_documents({})
    n_prestadores = banco["prestadores"].count_documents({})
    n_pets = n_visitas = 0
    for tutor in banco["tutores"].find():
        pets = tutor.get("pets", [])
        n_pets += len(pets)
        for pet in pets:
            n_visitas += len(pet.get("visitas", []))
    print(f"  - tutores: {n_tutores}")
    print(f"  - prestadores: {n_prestadores}")
    print(f"  - pets (dentro dos tutores): {n_pets}")
    print(f"  - visitas (dentro dos pets): {n_visitas}")


if __name__ == "__main__":
    limpar_banco()
    criar_colecoes()
    inserir_documentos()
    mostrar_resumo()
