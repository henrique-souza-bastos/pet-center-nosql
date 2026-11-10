# 🐾 Pet Center

**App de passeadores e hospedagem pet com banco de dados NoSQL (MongoDB)**

Projeto da disciplina de Banco de Dados NoSQL · Gestão da Informação · UFU/FAGEN
Autores: Henrique Souza e Yuri Cainã

---

## 🚀 Visão Geral

O **Pet Center** conecta **tutores** de animais domésticos a **prestadores de serviço**: passeadores e hospedagens pet.

Hoje, quem precisa deixar o pet com alguém depende de indicações, mensagens soltas e pouca informação sobre o serviço. O sistema centraliza esse processo: o tutor cadastra seus pets, encontra prestadores com serviços compatíveis (espécie, porte, alergias) e contrata um passeio ou uma hospedagem, que fica registrado como um **evento**.

---

## ✨ Principais Funcionalidades

🐶 **Cadastro de pets com necessidades individuais**
Espécie, raça, porte, peso, data de nascimento (exata ou aproximada), alergias e quantidade de passeios por dia.

🧾 **Catálogo de serviços por prestador**
Cada prestador monta suas próprias ofertas, com duração, valor e restrições (espécies e portes aceitos, se aceita animal com alergia/doença).

📅 **Agendamento de passeios e hospedagens**
Cada contratação vira um evento com status (Solicitado → Confirmado → Em Andamento → Concluído / Cancelado).

📜 **Histórico rápido**
Cada evento guarda um *snapshot* com os nomes do tutor, do prestador e dos pets, para listar o histórico sem consultar as outras coleções.

---

## 👥 Como o sistema funciona (perfis)

O app não deixa qualquer pessoa cadastrar qualquer coisa: cada perfil só enxerga o que lhe cabe.

| Perfil | O que pode fazer |
|---|---|
| **Tutor** | Criar seu cadastro, cadastrar **seus** pets, ver a vitrine de serviços, **solicitar** um serviço escolhendo a data (e, na hospedagem, quantas diárias) e acompanhar seus agendamentos |
| **Prestador** | Criar seu cadastro, montar seu **catálogo de serviços** e **aceitar ou recusar** as solicitações que recebe |

**Fluxo de um agendamento:**

```
Tutor escolhe um serviço e a data  →  evento criado como "Solicitado"
                                        ↓
                    Prestador aceita  →  "Confirmado" (agendado)
                    Prestador recusa  →  "Cancelado"
```

Duas regras que a **API** garante, para o formulário não conseguir burlar:

1. **O tutor nunca define o valor.** O sistema calcula: passeio = valor do serviço; hospedagem = valor da diária × quantidade de diárias.
2. **O pet precisa ser compatível com o serviço.** A API confere espécie, porte e se o serviço aceita animal com alergia/doença antes de aceitar a solicitação.

---

## 🗂️ Modelo de Dados

**Banco:** `patinhas_carinho` · **Coleções:** `tutores`, `prestadores`, `eventos`

A modelagem segue o princípio do banco de documentos: o que **pertence** a uma entidade e é lido junto com ela fica **embutido**; o que é **compartilhado** ou representa uma **transação** fica em coleção separada, com **referências**.

| Coleção | O que guarda | Decisão de modelagem |
|---|---|---|
| `tutores` | Dados do tutor + array **`pets`** embutido | O pet pertence a um único tutor e é sempre lido junto dele → **embutido** |
| `prestadores` | Dados do prestador + array **`servicos_oferecidos`** embutido | A oferta só existe dentro do prestador e carrega as restrições dela → **embutido** |
| `eventos` | Cada contratação (passeio/hospedagem) | É uma transação que cresce sem limite e liga duas entidades → **coleção separada com referências** |

### 1. `tutores` (com pets embutidos)

**Tutor:** `nome`, `endereco`, `telefone`, `data_nascimento`
**Cada pet do array `pets`:** `pet_id`, `nome`, `especie`, `raca`, `peso_kg`, `porte`, `data_nascimento` (objeto com `data` e `tipo`: "Exata" ou "Aproximada"), `possui_alergia`, `detalhes_alergia`, `qtde_passeios_dia` (1, 2 ou 3), `observacoes`

```json
{
  "_id": "<ObjectId do tutor>",
  "nome": "Ana Souza",
  "endereco": "Rua Goiás, 100 - Santa Mônica, Uberlândia/MG",
  "telefone": "(34) 99999-0001",
  "data_nascimento": "1990-05-20",
  "pets": [
    {
      "pet_id": "<ObjectId do pet>",
      "nome": "Rex",
      "especie": "Cachorro",
      "raca": "Labrador",
      "peso_kg": 28.0,
      "porte": "Grande",
      "data_nascimento": { "data": "2019-03-10", "tipo": "Exata" },
      "possui_alergia": true,
      "detalhes_alergia": "Alergia a ração com frango.",
      "qtde_passeios_dia": 2,
      "observacoes": "Puxa bastante a guia no começo do passeio."
    }
  ]
}
```

### 2. `prestadores` (com catálogo de serviços embutido)

**Prestador:** `nome`, `endereco`, `telefone`, `data_nascimento`, `tipos_servicos_gerais` ("Passeio", "Hospedagem" ou "Ambos")
**Cada serviço do array `servicos_oferecidos`:** `servico_id`, `tipo`, `especies_aceitas`, `portes_aceitos`, `valor`, `aceita_animais_com_alergia_doenca`, mais `tempo_duracao` (quando é **Passeio**) ou `max_diarias`, de 1 a 10 (quando é **Hospedagem**).

> No **passeio**, `valor` é o preço do passeio. Na **hospedagem**, `valor` é o preço da **diária** e `max_diarias` é quantas diárias o prestador tem disponíveis — o tutor escolhe quantas quer e o total é calculado pelo sistema.

```json
{
  "_id": "<ObjectId do prestador>",
  "nome": "João Passeios",
  "endereco": "Rua das Acácias, 250 - Uberlândia/MG",
  "telefone": "(34) 98888-0001",
  "data_nascimento": "1995-02-14",
  "tipos_servicos_gerais": "Passeio",
  "servicos_oferecidos": [
    {
      "servico_id": "<ObjectId do serviço>",
      "tipo": "Passeio",
      "tempo_duracao": "30 min",
      "especies_aceitas": ["Cachorro"],
      "portes_aceitos": ["Pequeno", "Médio", "Grande"],
      "valor": 25.0,
      "aceita_animais_com_alergia_doenca": true
    },
    {
      "servico_id": "<ObjectId do serviço>",
      "tipo": "Hospedagem",
      "max_diarias": 10,
      "especies_aceitas": ["Cachorro", "Gato"],
      "portes_aceitos": ["Pequeno", "Médio"],
      "valor": 60.0,
      "aceita_animais_com_alergia_doenca": true
    }
  ]
}
```

### 3. `eventos` (agendamentos, com referências + snapshot)

**Campos:** `evento_id`, `tipo_evento`, `status`, `data_inicio`, `data_fim`, `qtde_diarias` (só hospedagem), `valor_total`

> `status`, `valor_total`, `data_fim` e `qtde_diarias` são definidos pela **API**, nunca pelo tutor.
**Referências:** `tutor_id`, `prestador_id`, `servico_id`, `pets_envolvidos` (array de `pet_id`)
**Snapshot:** cópia dos nomes no momento do agendamento

```json
{
  "evento_id": "<ObjectId do evento>",
  "tipo_evento": "Passeio",
  "status": "Concluído",
  "data_inicio": "2026-10-02T08:00:00Z",
  "data_fim": "2026-10-02T08:30:00Z",
  "valor_total": 25.0,
  "tutor_id": "<ObjectId do tutor>",
  "prestador_id": "<ObjectId do prestador>",
  "servico_id": "<ObjectId do serviço>",
  "pets_envolvidos": ["<ObjectId do pet>"],
  "snapshot": {
    "tutor_nome": "Ana Souza",
    "prestador_nome": "João Passeios",
    "pets_nomes": ["Rex"]
  }
}
```

**Por que o snapshot?** Para listar o histórico (“quais passeios o Rex já fez?”) sem precisar buscar em `tutores` e `prestadores` a cada linha. Em troca, se um nome mudar depois, o snapshot guarda o nome antigo — o que é justamente o desejado num registro histórico.

---

## 🛠️ Arquitetura e Tecnologias

```
Streamlit (formulário)  →  FastAPI (API)  →  MongoDB Atlas (banco)
        app.py                main.py            database.py
```

- **MongoDB Atlas** — banco NoSQL orientado a documentos, hospedado na nuvem.
- **Python + PyMongo** — linguagem e biblioteca que conectam a aplicação ao banco.
- **FastAPI + Pydantic** — a API que recebe os cadastros e valida os dados antes de gravar.
- **Streamlit** — a tela de formulário para cadastrar sem precisar escrever código.

### Rotas da API

| Método | Rota | O que faz |
|---|---|---|
| POST | `/tutores` | Cadastra um tutor |
| POST | `/tutores/{tutor_id}/pets` | Adiciona um pet **dentro** do tutor |
| POST | `/prestadores` | Cadastra um prestador |
| POST | `/prestadores/{prestador_id}/servicos` | Adiciona um serviço **dentro** do prestador |
| GET | `/servicos` | Vitrine: todos os serviços de todos os prestadores |
| POST | `/eventos` | Tutor solicita um serviço (a API calcula o valor e monta o snapshot) |
| PATCH | `/eventos/{evento_id}/status` | Prestador aceita (Confirmado) ou recusa (Cancelado) |
| GET | `/tutores` · `/prestadores` · `/eventos` | Lista o que está cadastrado (eventos aceita filtros `tutor_id`, `prestador_id` e `status`) |

---

## 📦 Entregas

| Atividade | Descrição | Onde está |
|---|---|---|
| A0 | Descrição do sistema | Este README |
| A1 | Criação do banco, das coleções e de documentos de exemplo no MongoDB Atlas, mais a API e o formulário de cadastro | Pasta [`A1`](A1) |

### Como executar a A1

1. Instale as dependências:
   ```bash
   pip install -r A1/requirements.txt
   ```
2. Copie `A1/.env.exemplo` para `A1/.env` e preencha `MONGO_URI` com a connection string do cluster no MongoDB Atlas.
3. Entre na pasta da entrega:
   ```bash
   cd A1
   ```
4. **Crie o banco, as coleções e os documentos de exemplo:**
   ```bash
   python criar_banco.py
   ```
   Cria `tutores`, `prestadores` e `eventos` com dados fictícios. A cada execução, as coleções são apagadas e recriadas.
5. **Suba a API** (deixe este terminal aberto):
   ```bash
   uvicorn main:app --reload
   ```
   Teste pelo navegador em `http://localhost:8000/docs`.
6. **Abra o formulário** (em outro terminal, com a API no ar):
   ```bash
   streamlit run app.py
   ```

> Para o professor avaliar: basta ler o código e o modelo de dados acima. Para rodar, use uma conta própria do MongoDB Atlas (preenchendo o `.env` conforme o `.env.exemplo`) e siga os passos acima.

| Arquivo | Conteúdo |
|---|---|
| `A1/database.py` | Conexão com o MongoDB Atlas (lê a `MONGO_URI` do `.env`) |
| `A1/modelos.py` | Modelos Pydantic das 3 coleções |
| `A1/criar_banco.py` | Criação das coleções e inserção dos documentos de exemplo |
| `A1/main.py` | API FastAPI com as rotas e a montagem do snapshot |
| `A1/app.py` | Formulário web (Streamlit) de cadastro |
| `A1/requirements.txt` | Bibliotecas Python necessárias |
| `A1/.env.exemplo` | Modelo do arquivo de configuração da conexão |
