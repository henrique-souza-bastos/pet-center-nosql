"""
Modelos Pydantic (validação dos dados) do Pet Center.

Estrutura NoSQL em 3 coleções:
- TUTORES: dados do tutor + array "pets" embutido.
- PRESTADORES: dados do prestador + array "servicos_oferecidos" embutido.
- EVENTOS: coleção separada de agendamentos, que referencia tutor, prestador,
  serviço e pets, e guarda um "snapshot" com os nomes.

Regras de negócio importantes:
- O tutor NÃO informa o valor: quem calcula é a API, a partir do serviço.
- Passeio: o valor é o valor do serviço.
- Hospedagem: o prestador informa o valor da DIÁRIA e quantas diárias tem
  disponíveis (1 a 10); o tutor escolhe a quantidade e o total é calculado.
- Todo evento nasce com status "Solicitado"; o prestador aceita ou recusa.

Autores: Henrique Souza e Yuri Cainã
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# Valores aceitos em vários lugares do sistema
TIPOS_SERVICO = ["Passeio", "Hospedagem"]
STATUS_EVENTO = [
    "Solicitado", "Confirmado", "Em Andamento", "Concluído", "Cancelado",
]


# =====================================================================
# TUTORES (com pets embutidos)
# =====================================================================
class DataNascimento(BaseModel):
    """Nascimento do pet: a data e se ela é exata ou aproximada."""
    data: str                 # ex: "2019-03-10"
    tipo: str                 # "Exata" ou "Aproximada"


class Pet(BaseModel):
    model_config = ConfigDict(extra="allow")

    nome: str
    especie: str                       # ex: "Cachorro", "Gato"
    raca: str                          # ex: "SRD", "Labrador"
    peso_kg: float
    porte: str                         # "Pequeno", "Médio", "Grande"
    data_nascimento: DataNascimento
    possui_alergia: bool = False
    detalhes_alergia: Optional[str] = None   # preenchido só se possui_alergia
    qtde_passeios_dia: int = Field(1, ge=1, le=3)
    observacoes: Optional[str] = None


class Tutor(BaseModel):
    nome: str
    endereco: str
    telefone: str
    data_nascimento: str               # ex: "1990-05-20"
    pets: List[Pet] = []


# =====================================================================
# PRESTADORES (com catálogo de serviços embutido)
# =====================================================================
class ServicoOferecido(BaseModel):
    """
    Uma oferta do prestador.

    - Passeio:    usa "tempo_duracao" e "valor" é o preço do passeio.
    - Hospedagem: usa "max_diarias" (1 a 10 disponíveis) e "valor" é o preço
                  da DIÁRIA.
    """
    tipo: str                                 # "Passeio" ou "Hospedagem"
    tempo_duracao: Optional[str] = None       # só passeio: ex. "30 min"
    max_diarias: Optional[int] = Field(None, ge=1, le=10)  # só hospedagem
    especies_aceitas: List[str] = []
    portes_aceitos: List[str] = []
    valor: float                              # passeio: total | hospedagem: diária
    aceita_animais_com_alergia_doenca: bool = False


class Prestador(BaseModel):
    nome: str
    endereco: str
    telefone: str
    data_nascimento: str
    tipos_servicos_gerais: str         # "Passeio", "Hospedagem" ou "Ambos"
    servicos_oferecidos: List[ServicoOferecido] = []


# =====================================================================
# EVENTOS
# =====================================================================
class EventoSolicitacao(BaseModel):
    """
    O que o TUTOR envia ao solicitar um serviço.

    Repare que não existe campo de valor nem de status: quem define os dois é
    a API, para o tutor não conseguir alterar o preço.
    """
    tutor_id: str
    prestador_id: str
    servico_id: str
    pets_envolvidos: List[str] = []
    data_inicio: datetime
    qtde_diarias: Optional[int] = Field(None, ge=1, le=10)  # só hospedagem


class AtualizacaoStatus(BaseModel):
    """O que o PRESTADOR envia para aceitar, recusar ou andar com o evento."""
    status: str
