# 🐾 Patinhas & Carinho

**App de passeadores e hospedagem pet com banco de dados NoSQL (MongoDB)**

Projeto da disciplina de Banco de Dados NoSQL · Gestão da Informação · UFU/FAGEN
Autores: Henrique Souza e Yuri Cainã

---

## 🚀 Visão Geral

O **Patinhas & Carinho** conecta **tutores** de animais domésticos a **prestadores de serviço**: passeadores e hospedagens pet.

Hoje, quem precisa deixar o pet com alguém depende de indicações, mensagens soltas e pouca informação sobre como foi o serviço. O sistema centraliza esse processo: o tutor encontra prestadores perto de casa, contrata um passeio ou uma estadia e recebe um **relatório completo** de cada atendimento.

---

## ✨ Principais Funcionalidades

🐶 **Cadastro de pets com necessidades individuais**
Cães, gatos e pequenos animais, cada um com suas informações: alergias, medicamentos, dieta e comportamento.

📍 **Busca de prestadores por proximidade**
O tutor encontra passeadores e hospedagens a até X km de casa, filtrando pela espécie atendida.

🦮 **Relatório de passeio**
Trajeto de GPS, ocorrências (xixi, cocô), fotos e observações do passeador.

🏠 **Diário de hospedagem**
Registro de cada dia da estadia: alimentação, humor e observações.

⭐ **Avaliação dos serviços**
Nota e comentário do tutor ao final de cada atendimento.

---

## 🧠 Por que um banco NoSQL (orientado a documentos)?

1. **O relatório da visita é um agregado.** Trajeto, ocorrências, fotos e avaliação são sempre lidos juntos. No MongoDB, a visita inteira é um único documento, lido de uma vez. No modelo relacional, seriam várias tabelas e JOINs para remontar o relatório. (Conceito de *aggregate*, *NoSQL Distilled*, cap. 2.)
2. **Esquema flexível.** Cada espécie tem campos diferentes: o gato tem `indoor`, o coelho tem `dieta` e não tem `raca`. Passeio tem `trajeto`; hospedagem tem `diario`. No modelo relacional, isso geraria colunas cheias de nulos ou tabelas extras.
3. **Dados geográficos nativos.** O MongoDB armazena localizações no formato GeoJSON e oferece busca por proximidade.
4. **Muitas escritas pequenas.** Durante o passeio, o app grava pontos de GPS com frequência.

**Onde o relacional ainda seria melhor:** pagamentos, agenda sem conflito de horário e relatórios financeiros exigem consistência rígida e consultas tabulares. Em um sistema real, essas partes poderiam ficar em um banco relacional ao lado do MongoDB, o que caracteriza a **persistência poliglota** (*polyglot persistence*, *NoSQL Distilled*, cap. 13). Este projeto modela a parte em MongoDB.

---

## 🗂️ Modelo de Dados

**Banco:** `patinhas_carinho`

| Coleção | O que guarda | Relacionamentos |
|---|---|---|
| `tutores` | Dados do tutor, com endereço **embutido** | — |
| `pets` | Dados do pet, com campos variáveis por espécie | `tutor_id` → `tutores` (**referência**) |
| `prestadores` | Passeadores e hospedagens, com localização e serviços **embutidos** | — |
| `visitas` | Passeio ou estadia, com trajeto ou diário, ocorrências, fotos e avaliação **embutidos** | `pet_id` → `pets`, `prestador_id` → `prestadores` (**referências**) |

**Critério para embutir ou referenciar:**
- **Embutir** o que é lido junto e cresce pouco (endereço, ocorrências do passeio, avaliação).
- **Referenciar** o que é compartilhado ou cresce sem limite (um tutor tem vários pets; um pet tem muitas visitas).

**Duplicação proposital:** `visitas` guarda uma cópia de `pet_nome` e `prestador_nome`, para exibir o relatório sem consultar outras coleções. Em troca, se um nome mudar, as cópias antigas ficam desatualizadas.

**Validação:** a coleção `visitas` exige os campos `tipo`, `pet_id`, `prestador_id`, `inicio` e `status`, e aceita apenas valores definidos para `tipo` e `status`.

### Exemplo de documento (`visitas`, tipo passeio)

```json
{
  "tipo": "passeio",
  "status": "concluida",
  "pet_id": "<ObjectId do pet>",
  "pet_nome": "Rex",
  "prestador_id": "<ObjectId do prestador>",
  "prestador_nome": "João Passeios",
  "inicio": "2026-10-02T08:00:00Z",
  "fim": "2026-10-02T08:30:00Z",
  "trajeto": { "type": "LineString", "coordinates": [[-48.278, -18.915], [-48.277, -18.916]] },
  "ocorrencias": [ { "tipo": "xixi", "hora": "08:12" } ],
  "fotos": ["https://exemplo.com/fotos/rex1.jpg"],
  "valor": 25.0,
  "avaliacao": { "nota": 5, "comentario": "Ótimo passeio!" }
}
```

---

## 🛠️ Arquitetura e Tecnologias

O sistema tem **três camadas**, no mesmo padrão do exemplo da disciplina:

```
Streamlit (formulário)  →  FastAPI (API)  →  MongoDB Atlas (banco)
        app.py                main.py            database.py
```

- **MongoDB Atlas** — banco de dados NoSQL orientado a documentos, hospedado na nuvem.
- **Python + PyMongo** — linguagem e biblioteca que conectam a aplicação ao banco.
- **FastAPI + Pydantic** — a API que recebe os cadastros e valida os dados antes de gravar.
- **Streamlit** — a tela de formulário para cadastrar sem precisar escrever código.

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
   O script cria o banco `patinhas_carinho` com as 4 coleções e insere dados fictícios: 2 tutores, 3 pets (cão, gato e coelho), 2 prestadores e 3 visitas. A cada execução, as coleções são apagadas e recriadas.
5. **Suba a API** (deixe este terminal aberto):
   ```bash
   uvicorn main:app --reload
   ```
   Teste pelo navegador em `http://localhost:8000/docs`.
6. **Abra o formulário** (em outro terminal, com a API no ar):
   ```bash
   streamlit run app.py
   ```

| Arquivo | Conteúdo |
|---|---|
| `A1/database.py` | Conexão com o MongoDB Atlas (lê a `MONGO_URI` do `.env`) |
| `A1/modelos.py` | Modelos Pydantic que validam os dados das 4 entidades |
| `A1/criar_banco.py` | Criação das coleções e inserção dos documentos de exemplo |
| `A1/main.py` | API FastAPI com os endpoints de cadastro e listagem |
| `A1/app.py` | Formulário web (Streamlit) de cadastro |
| `A1/requirements.txt` | Bibliotecas Python necessárias |
| `A1/.env.exemplo` | Modelo do arquivo de configuração da conexão |
