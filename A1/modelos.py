"""
Modelos Pydantic (validação dos dados) do Pet Center.

Estrutura de documento ANINHADA, como pede o modelo orientado a documentos:
- cada TUTOR guarda a lista dos seus PETS;
- cada PET guarda a lista das suas VISITAS.
Os PRESTADORES ficam numa coleção separada, porque são compartilhados por
vários tutores e visitas (não faz sentido duplicá-los dentro de cada tutor).

Autores: Henrique Souza e Yuri Cainã
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------
# Pedaços reaproveitados
# ---------------------------------------------------------------------
class Endereco(BaseModel):
    bairro: str
    cidade: str
    uf: str


class Medicamento(BaseModel):
    nome: str
    horarios: List[str] = []


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


# ---------------------------------------------------------------------
# VISITA - fica DENTRO de um pet. Referencia o prestador (que é de outra
# coleção) e guarda uma cópia do nome dele, para exibir sem consultar nada.
# ---------------------------------------------------------------------
class Visita(BaseModel):
    model_config = ConfigDict(extra="allow")

    tipo: str            # "passeio" ou "hospedagem"
    status: str          # agendada, em_andamento, concluida, cancelada
    prestador_id: str    # referência ao prestador
    prestador_nome: str  # cópia, para mostrar sem consultar outra coleção
    inicio: datetime
    fim: Optional[datetime] = None
    trajeto: Optional[Trajeto] = None            # passeio
    diario: Optional[List[DiaHospedagem]] = None  # hospedagem
    ocorrencias: List[Ocorrencia] = []
    fotos: List[str] = []
    observacoes: Optional[str] = None
    valor: Optional[float] = None
    avaliacao: Optional[Avaliacao] = None


# ---------------------------------------------------------------------
# PET - fica DENTRO de um tutor e carrega a lista das suas visitas.
# "extra=allow" deixa cada espécie ter campos próprios (gato: indoor;
# coelho: dieta).
# ---------------------------------------------------------------------
class Pet(BaseModel):
    model_config = ConfigDict(extra="allow")

    nome: str
    especie: str
    raca: Optional[str] = None
    porte: Optional[str] = None
    peso_kg: Optional[float] = None
    alergias: List[str] = []
    medicamentos: List[Medicamento] = []
    comportamento: Optional[dict] = None
    visitas: List[Visita] = []


# ---------------------------------------------------------------------
# TUTOR - coleção principal. Guarda o endereço embutido e a lista de pets.
# ---------------------------------------------------------------------
class Tutor(BaseModel):
    nome: str
    email: str
    telefone: str
    endereco: Endereco
    pets: List[Pet] = []


# ---------------------------------------------------------------------
# PRESTADOR - coleção separada (passeadores e hospedagens).
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
