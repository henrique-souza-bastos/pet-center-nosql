"""
Modelos Pydantic (validação dos dados) das 4 entidades do sistema.

A API (main.py) usa estes modelos para conferir os dados recebidos do
formulário antes de gravar no MongoDB. Cada classe descreve os campos
esperados e o seu tipo.

Autores: Henrique Souza e Yuri Cainã
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------
# TUTOR - o endereço fica embutido (é sempre lido junto com o tutor).
# ---------------------------------------------------------------------
class Endereco(BaseModel):
    bairro: str
    cidade: str
    uf: str


class Tutor(BaseModel):
    nome: str
    email: str
    telefone: str
    endereco: Endereco


# ---------------------------------------------------------------------
# PET - "extra=allow" deixa cada espécie ter campos próprios (o gato tem
# "indoor", o coelho tem "dieta"), sem precisar declarar todos aqui.
# "tutor_id" é uma referência ao tutor dono do pet.
# ---------------------------------------------------------------------
class Medicamento(BaseModel):
    nome: str
    horarios: List[str] = []


class Pet(BaseModel):
    model_config = ConfigDict(extra="allow")

    tutor_id: str
    nome: str
    especie: str
    raca: Optional[str] = None
    porte: Optional[str] = None
    peso_kg: Optional[float] = None
    alergias: List[str] = []
    medicamentos: List[Medicamento] = []
    comportamento: Optional[dict] = None


# ---------------------------------------------------------------------
# PRESTADOR - passeadores e hospedagens. "localizacao" usa GeoJSON, sempre
# na ordem [longitude, latitude]. "extra=allow" cobre campos como
# "capacidade", que só a hospedagem tem.
# ---------------------------------------------------------------------
class Localizacao(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]


class Servico(BaseModel):
    nome: str
    preco: float


class Prestador(BaseModel):
    model_config = ConfigDict(extra="allow")

    tipo: str  # "passeador" ou "hospedagem"
    nome: str
    localizacao: Localizacao
    especies_aceitas: List[str]
    servicos: List[Servico] = []


# ---------------------------------------------------------------------
# VISITA - o relatório de um passeio ou de uma estadia. O passeio tem
# "trajeto"; a hospedagem tem "diario". Os nomes do pet e do prestador são
# copiados de propósito, para exibir o relatório sem consultar outras
# coleções.
# ---------------------------------------------------------------------
class Ocorrencia(BaseModel):
    tipo: str
    hora: str


class Trajeto(BaseModel):
    type: str = "LineString"
    coordinates: List[List[float]]


class DiaHospedagem(BaseModel):
    model_config = ConfigDict(extra="allow")

    data: str
    alimentacao: Optional[str] = None
    humor: Optional[str] = None
    observacoes: Optional[str] = None


class Avaliacao(BaseModel):
    nota: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = None


class Visita(BaseModel):
    model_config = ConfigDict(extra="allow")

    tipo: str  # "passeio" ou "hospedagem"
    status: str  # agendada, em_andamento, concluida, cancelada
    pet_id: str
    pet_nome: str
    prestador_id: str
    prestador_nome: str
    inicio: datetime
    fim: Optional[datetime] = None
    trajeto: Optional[Trajeto] = None
    diario: Optional[List[DiaHospedagem]] = None
    ocorrencias: List[Ocorrencia] = []
    fotos: List[str] = []
    observacoes: Optional[str] = None
    valor: Optional[float] = None
    avaliacao: Optional[Avaliacao] = None
