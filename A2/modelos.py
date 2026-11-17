from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

TIPOS_SERVICO = ["Passeio", "Hospedagem"]
STATUS_EVENTO = [
    "Solicitado", "Confirmado", "Em Andamento", "Concluído", "Cancelado",
]


class DataNascimento(BaseModel):
    data: str
    tipo: str


class Pet(BaseModel):
    model_config = ConfigDict(extra="allow")

    nome: str
    especie: str
    raca: str
    peso_kg: float
    porte: str
    data_nascimento: DataNascimento
    possui_alergia: bool = False
    detalhes_alergia: Optional[str] = None
    qtde_passeios_dia: int = Field(1, ge=1, le=3)
    observacoes: Optional[str] = None


class Tutor(BaseModel):
    usuario: str
    nome: str
    endereco: str
    telefone: str
    data_nascimento: str
    pets: List[Pet] = []


class ServicoOferecido(BaseModel):
    tipo: str
    tempo_duracao: Optional[str] = None
    max_diarias: Optional[int] = Field(None, ge=1, le=10)
    especies_aceitas: List[str] = []
    portes_aceitos: List[str] = []
    valor: float
    aceita_animais_com_alergia_doenca: bool = False


class Prestador(BaseModel):
    usuario: str
    nome: str
    endereco: str
    telefone: str
    data_nascimento: str
    tipos_servicos_gerais: str
    servicos_oferecidos: List[ServicoOferecido] = []


class EventoSolicitacao(BaseModel):
    tutor_id: str
    prestador_id: str
    servico_id: str
    pets_envolvidos: List[str] = []
    data_inicio: datetime
    qtde_diarias: Optional[int] = Field(None, ge=1, le=10)


class AtualizacaoStatus(BaseModel):
    status: str
