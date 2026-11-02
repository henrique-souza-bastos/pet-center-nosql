"""
A1 - Criação do banco no MongoDB Atlas
Pet Center: app de passeadores e hospedagem pet

Cria o banco "patinhas_carinho", as 4 coleções e insere documentos de exemplo.
Todos os dados são fictícios.

Autores: Henrique Souza e Yuri Cainã

Como rodar:  python criar_banco.py
"""
from datetime import datetime, timezone

from bson import ObjectId

from database import banco

COLECOES = ["tutores", "pets", "prestadores", "visitas"]


def data(texto):
    """Converte '2026-10-02 08:00' em data/hora (UTC) que o MongoDB entende."""
    return datetime.strptime(texto, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)


# IDs criados antes, para um documento poder referenciar o outro.
tutor_ana = ObjectId()
tutor_bruno = ObjectId()
pet_rex = ObjectId()
pet_mia = ObjectId()
pet_pipoca = ObjectId()
passeador_joao = ObjectId()
hospedagem_casa = ObjectId()

# ---------------------------------------------------------------------
# TUTORES - o endereço fica embutido (é sempre lido junto com o tutor).
# ---------------------------------------------------------------------
tutores = [
    {
        "_id": tutor_ana,
        "nome": "Ana Souza",
        "email": "ana@exemplo.com",
        "telefone": "(34) 99999-0001",
        "endereco": {"bairro": "Santa Mônica", "cidade": "Uberlândia", "uf": "MG"},
    },
    {
        "_id": tutor_bruno,
        "nome": "Bruno Lima",
        "email": "bruno@exemplo.com",
        "telefone": "(34) 99999-0002",
        "endereco": {"bairro": "Centro", "cidade": "Uberlândia", "uf": "MG"},
    },
]

# ---------------------------------------------------------------------
# PETS - cada espécie tem campos diferentes (esquema flexível).
# "tutor_id" é uma REFERÊNCIA: um tutor pode ter vários pets.
# ---------------------------------------------------------------------
pets = [
    {
        "_id": pet_rex,
        "tutor_id": tutor_ana,
        "nome": "Rex",
        "especie": "cao",
        "raca": "Labrador",
        "porte": "grande",
        "peso_kg": 28,
        "alergias": ["frango"],
        "medicamentos": [{"nome": "Condroitina", "horarios": ["08:00", "20:00"]}],
        "comportamento": {"agressivo_com_machos": False, "castrado": True},
    },
    {
        "_id": pet_mia,
        "tutor_id": tutor_ana,
        "nome": "Mia",
        "especie": "gato",
        "raca": "SRD",
        "alergias": [],
        "indoor": True,  # campo que só faz sentido para gatos
    },
    {
        "_id": pet_pipoca,
        "tutor_id": tutor_bruno,
        "nome": "Pipoca",
        "especie": "coelho",
        "dieta": {"feno": True, "racao_g_dia": 40},  # sem "raca", sem "porte"
    },
]

# ---------------------------------------------------------------------
# PRESTADORES - passeadores e hospedagens na mesma coleção.
# "localizacao" usa GeoJSON (formato padrão de ponto no mapa),
# sempre na ordem [longitude, latitude].
# ---------------------------------------------------------------------
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
# VISITAS - o "pacote" de dados de um passeio ou de uma estadia.
# O que é lido junto fica EMBUTIDO (trajeto, ocorrências, fotos, avaliação).
# Os nomes do pet e do prestador são copiados de propósito, para mostrar
# o relatório sem consultar outras coleções.
# ---------------------------------------------------------------------
visitas = [
    {
        "tipo": "passeio",
        "status": "concluida",
        "pet_id": pet_rex,
        "pet_nome": "Rex",
        "prestador_id": passeador_joao,
        "prestador_nome": "João Passeios",
        "inicio": data("2026-10-02 08:00"),
        "fim": data("2026-10-02 08:30"),
        "trajeto": {  # linha formada pelos pontos de GPS
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
        "pet_id": pet_rex,
        "pet_nome": "Rex",
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
    {
        "tipo": "hospedagem",  # mesmo modelo, mas com "diario" em vez de "trajeto"
        "status": "concluida",
        "pet_id": pet_mia,
        "pet_nome": "Mia",
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
]


def limpar_banco():
    """Apaga as coleções, para o script poder ser rodado várias vezes."""
    for nome in COLECOES:
        banco.drop_collection(nome)


def criar_colecoes():
    """Cria as coleções (o equivalente às tabelas) de forma explícita."""
    banco.create_collection("tutores")
    banco.create_collection("pets")
    banco.create_collection("prestadores")

    # "visitas" tem uma regra mínima de validação: mesmo sem esquema fixo,
    # o banco exige os campos essenciais e limita os valores de tipo e status.
    banco.create_collection(
        "visitas",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["tipo", "pet_id", "prestador_id", "inicio", "status"],
                "properties": {
                    "tipo": {"enum": ["passeio", "hospedagem"]},
                    "status": {"enum": ["agendada", "em_andamento", "concluida", "cancelada"]},
                },
            }
        },
    )


def inserir_documentos():
    banco["tutores"].insert_many(tutores)
    banco["pets"].insert_many(pets)
    banco["prestadores"].insert_many(prestadores)
    banco["visitas"].insert_many(visitas)


def mostrar_resumo():
    print(f"Banco '{banco.name}' criado com sucesso:")
    for nome in COLECOES:
        print(f"  - {nome}: {banco[nome].count_documents({})} documentos")


if __name__ == "__main__":
    limpar_banco()
    criar_colecoes()
    inserir_documentos()
    mostrar_resumo()
