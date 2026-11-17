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

**Entrada no sistema:** a primeira tela oferece apenas **Entrar** ou **Criar conta**. Cada conta tem um nome de `usuario` único (ex.: `ana.souza`) e o login é feito só com ele, sem senha — é um login simplificado para fins didáticos. Ao criar a conta a pessoa escolhe se é tutor ou prestador, e depois de entrar só vê a área do seu perfil. Usuários de exemplo: `ana.souza`, `bruno.lima`, `carla.mendes` (tutores) e `joao.passeios`, `casa.petfeliz`, `patas.cia` (prestadores).

| Perfil | O que pode fazer |
|---|---|
| **Tutor** | Criar sua conta, cadastrar **seus** pets, ver a vitrine de serviços, **solicitar** um serviço escolhendo a data (e, na hospedagem, quantas diárias) e acompanhar seus agendamentos |
| **Prestador** | Criar sua conta, montar seu **catálogo de serviços** e **aceitar ou recusar** as solicitações que recebe |

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

**Tutor:** `usuario` (nome de login, único), `nome`, `endereco`, `telefone`, `data_nascimento`
**Cada pet do array `pets`:** `pet_id`, `nome`, `especie`, `raca`, `peso_kg`, `porte`, `data_nascimento` (objeto com `data` e `tipo`: "Exata" ou "Aproximada"), `possui_alergia`, `detalhes_alergia`, `qtde_passeios_dia` (1, 2 ou 3), `observacoes`

```json
{
  "_id": "<ObjectId do tutor>",
  "usuario": "ana.souza",
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

**Prestador:** `usuario` (nome de login, único), `nome`, `endereco`, `telefone`, `data_nascimento`, `tipos_servicos_gerais` ("Passeio", "Hospedagem" ou "Ambos")
**Cada serviço do array `servicos_oferecidos`:** `servico_id`, `tipo`, `especies_aceitas`, `portes_aceitos`, `valor`, `aceita_animais_com_alergia_doenca`, mais `tempo_duracao` (quando é **Passeio**) ou `max_diarias`, de 1 a 10 (quando é **Hospedagem**).

> No **passeio**, `valor` é o preço do passeio. Na **hospedagem**, `valor` é o preço da **diária** e `max_diarias` é quantas diárias o prestador tem disponíveis — o tutor escolhe quantas quer e o total é calculado pelo sistema.

```json
{
  "_id": "<ObjectId do prestador>",
  "usuario": "joao.passeios",
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
| GET | `/login/{usuario}` | Localiza a conta pelo usuário e devolve o perfil (Tutor ou Prestador) |
| POST | `/tutores` | Cadastra um tutor (recusa `usuario` repetido) |
| POST | `/tutores/{tutor_id}/pets` | Adiciona um pet **dentro** do tutor |
| POST | `/prestadores` | Cadastra um prestador |
| POST | `/prestadores/{prestador_id}/servicos` | Adiciona um serviço **dentro** do prestador |
| GET | `/servicos` | Vitrine: todos os serviços de todos os prestadores |
| POST | `/eventos` | Tutor solicita um serviço (a API calcula o valor e monta o snapshot) |
| PATCH | `/eventos/{evento_id}/status` | Prestador aceita (Confirmado) ou recusa (Cancelado) |
| GET | `/tutores` · `/prestadores` · `/eventos` | Lista o que está cadastrado (eventos aceita filtros `tutor_id`, `prestador_id` e `status`) |
| GET | `/tutores/{tutor_id}/pets/{pet_id}/servicos-compativeis` | **[A2]** Só os serviços que aceitam o pet, dos mais contratados para os menos |
| GET | `/prestadores/{prestador_id}/faturamento` | **[A2]** Faturamento do prestador por mês e por tipo de serviço |

---

## 📦 Entregas

| Atividade | Descrição | Onde está |
|---|---|---|
| A0 | Descrição do sistema | Este README |
| A1 | Criação do banco, das coleções e de documentos de exemplo no MongoDB Atlas, mais a API e o formulário de cadastro | Pasta [`A1`](A1) |
| A2 | Duas funcionalidades novas com **pipelines de agregação** bem diferentes: serviços compatíveis com o pet e painel de faturamento | Pasta [`A2`](A2) · [detalhes](#-a2--pipelines-de-agregação) |

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

---

## 🧮 A2 — Pipelines de agregação

**Enunciado:** implementar 2 funcionalidades úteis para o sistema, com pipelines bem diferentes.

Um **pipeline de agregação** é uma "linha de montagem" dentro do MongoDB: os documentos de uma coleção passam por etapas em sequência (filtrar, abrir arrays, juntar com outra coleção, agrupar, ordenar) e a saída de uma etapa é a entrada da próxima. O trabalho é feito pelo banco, não pelo Python.

Os dois pipelines estão no arquivo [`A2/consultas.py`](A2/consultas.py).

| | Funcionalidade 1 | Funcionalidade 2 |
|---|---|---|
| **O que é** | Serviços compatíveis com o meu pet | Painel de faturamento |
| **Para quem** | Tutor | Prestador |
| **Coleção de partida** | `prestadores` | `eventos` |
| **Ideia central** | Abrir um array embutido e **juntar** com outra coleção | **Agrupar** e calcular totais por período |
| **Etapas** | `$unwind` → `$match` → `$lookup` → `$addFields` → `$sort` → `$project` | `$match` → `$group` → `$sort` → `$project` |

### Funcionalidade 1 — Serviços compatíveis com o meu pet

**Problema que resolve:** na A1 o tutor via a vitrine inteira e só descobria que o pet não era aceito quando a API recusava o pedido. Agora ele escolhe o pet e vê **apenas** os serviços que o aceitam, começando pelos mais contratados.

| Etapa | O que faz |
|---|---|
| `$unwind` | "Abre" o array `servicos_oferecidos`: um prestador com 3 serviços vira 3 documentos, um por serviço |
| `$match` | Mantém só os serviços que aceitam a espécie e o porte do pet e, se o pet tem alergia/doença, só os que aceitam essa condição |
| `$lookup` | Junta com a coleção `eventos`, trazendo os eventos **concluídos** de cada serviço (o "join" do MongoDB) |
| `$addFields` | Cria o campo `vezes_contratado` com o tamanho da lista trazida pelo `$lookup` |
| `$sort` | Mais contratados primeiro; no empate, o mais barato |
| `$project` | Monta a resposta no mesmo formato da vitrine `/servicos` |

### Funcionalidade 2 — Painel de faturamento

**Problema que resolve:** o prestador só enxergava a lista de eventos, sem nenhum resumo. Agora vê quanto faturou em cada mês, separado por tipo de serviço, com quantidade e ticket médio (valor médio por serviço).

| Etapa | O que faz |
|---|---|
| `$match` | Mantém só os eventos do prestador com status **Concluído** (pendente, confirmado e cancelado não são receita) |
| `$group` | Agrupa por mês (`$dateToString` transforma a data em `"2026-10"`) e por tipo; calcula `$sum` (faturamento e quantidade) e `$avg` (ticket médio) |
| `$sort` | Ordem cronológica e, dentro do mês, por tipo |
| `$project` | Organiza os campos da resposta e arredonda o ticket médio |

### O que é novo na A2

A pasta `A2` é uma cópia da `A1` com as novidades listadas abaixo.

| Arquivo | O que mudou |
|---|---|
| `A2/consultas.py` | **Arquivo novo.** Os dois pipelines de agregação, comentados etapa por etapa |
| `A2/main.py` | As duas rotas novas, no fim do arquivo |
| `A2/app.py` | Abas novas **"Para o meu pet"** (tutor) e **"Faturamento"** (prestador) |
| `A2/criar_banco.py` | Dados extras: mais 1 prestador, 1 tutor e 17 eventos em vários meses, para as agregações terem o que mostrar |
| `A2/database.py`, `A2/modelos.py`, `A2/requirements.txt`, `A2/.env.exemplo` | Iguais aos da A1 |

### Como executar a A2

Os passos são os mesmos da A1, trocando a pasta:

1. Copie `A2/.env.exemplo` para `A2/.env` e preencha `MONGO_URI` (pode ser a mesma da A1).
2. Entre na pasta:
   ```bash
   cd A2
   ```
3. Recrie o banco com os dados extras:
   ```bash
   python criar_banco.py
   ```
4. Suba a API (deixe este terminal aberto):
   ```bash
   python -m uvicorn main:app --reload
   ```
5. Em outro terminal, abra a tela:
   ```bash
   python -m streamlit run app.py
   ```

**Onde ver na tela:** entre com um usuário de tutor (ex.: `ana.souza`) → aba *Para o meu pet*; entre com um usuário de prestador (ex.: `patas.cia`) → aba *Faturamento*. As rotas também podem ser testadas em `http://localhost:8000/docs`.
