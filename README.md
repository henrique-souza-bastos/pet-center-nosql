# 🐾 Pet Center

**App de passeadores e hospedagem pet com banco de dados NoSQL (MongoDB)**

Projeto da disciplina de Banco de Dados NoSQL · Gestão da Informação · UFU/FAGEN
Autores: Henrique Souza e Yuri Cainã

---

## 🚀 Visão Geral

O **Pet Center** conecta **tutores** de animais domésticos a **prestadores de serviço**: passeadores e hospedagens pet.

Hoje, quem precisa deixar o pet com alguém depende de indicações, mensagens soltas e pouca informação sobre como foi o serviço. O sistema centraliza esse processo: o tutor encontra prestadores perto de casa, contrata um passeio ou uma estadia e recebe um **relatório completo** de cada atendimento.

---

## ✨ Principais Funcionalidades

🐶 **Cadastro de pets com necessidades individuais**
Cães, gatos e pequenos animais, cada um com suas informações: alergias, medicamentos, dieta e comportamento.

📍 **Busca de prestadores por proximidade**
O tutor encontra passeadores e hospedagens perto de casa, filtrando pela espécie atendida.

🦮 **Relatório de passeio**
Trajeto de GPS, ocorrências (xixi, cocô), fotos e observações do passeador.

🏠 **Diário de hospedagem**
Registro de cada dia da estadia: alimentação, humor e observações.

⭐ **Avaliação dos serviços**
Nota e comentário do tutor ao final de cada atendimento.

---

## 🗂️ Modelo de Dados

**Banco:** `patinhas_carinho`

O sistema usa o **modelo orientado a documentos**: o que pertence a uma coisa e é lido junto com ela fica **aninhado** dentro dela, formando um único documento (um *agregado*).

- Cada **tutor** guarda dentro de si a lista dos seus **pets**.
- Cada **pet** guarda dentro de si a lista das suas **visitas** (passeios e hospedagens).
- Os **prestadores** ficam numa **coleção separada**, porque são compartilhados por vários tutores e visitas — duplicá-los dentro de cada tutor seria repetição desnecessária.

| Coleção | O que guarda |
|---|---|
| `tutores` | O tutor, com o endereço embutido, a **lista de pets**, e dentro de cada pet a **lista de visitas**. É a coleção principal. |
| `prestadores` | Passeadores e hospedagens, com localização (GeoJSON) e serviços. Coleção separada. |

**Como as partes se ligam:**
- **Pet dentro de tutor** e **visita dentro de pet** → *aninhado* (lidos sempre junto com o tutor).
- **Visita → prestador** → *referência*: a visita guarda o `prestador_id` (e uma cópia do `prestador_nome`, para exibir o relatório sem precisar consultar a outra coleção).

### 🧠 Por que aninhar?

O relatório de um tutor (seus pets e as visitas de cada um) é quase sempre lido de uma vez. No MongoDB, isso vira **um único documento**, buscado numa tacada só — sem os vários JOINs que o modelo relacional exigiria para remontar tudo. Além disso, o esquema é flexível: o gato tem `indoor`, o coelho tem `dieta`, o passeio tem `trajeto` e a hospedagem tem `diario`, tudo no mesmo lugar.

> **Nota de evolução futura:** a lista de visitas dentro de um pet cresce a cada atendimento. Para um volume muito grande no futuro, as visitas poderiam virar uma coleção própria referenciando o pet. Para o tamanho deste projeto, mantê-las aninhadas é mais simples e atende bem.

### Exemplo de documento (`tutores`)

```json
{
  "_id": "<ObjectId do tutor>",
  "nome": "Ana Souza",
  "email": "ana@exemplo.com",
  "telefone": "(34) 99999-0001",
  "endereco": { "bairro": "Santa Mônica", "cidade": "Uberlândia", "uf": "MG" },
  "pets": [
    {
      "_id": "<ObjectId do pet>",
      "nome": "Rex",
      "especie": "cao",
      "raca": "Labrador",
      "visitas": [
        {
          "tipo": "passeio",
          "status": "concluida",
          "prestador_id": "<ObjectId do prestador>",
          "prestador_nome": "João Passeios",
          "inicio": "2026-10-02T08:00:00Z",
          "trajeto": { "type": "LineString", "coordinates": [[-48.278, -18.915], [-48.277, -18.916]] },
          "avaliacao": { "nota": 5, "comentario": "Ótimo passeio!" }
        }
      ]
    }
  ]
}
```

---

## 🛠️ Arquitetura e Tecnologias

O sistema tem **três camadas**:

```
Streamlit (formulário)  →  FastAPI (API)  →  MongoDB Atlas (banco)
        app.py                main.py            database.py
```

- **MongoDB Atlas** — banco de dados NoSQL orientado a documentos, hospedado na nuvem.
- **Python + PyMongo** — linguagem e biblioteca que conectam a aplicação ao banco.
- **FastAPI + Pydantic** — a API que recebe os cadastros e valida os dados antes de gravar.
- **Streamlit** — a tela de formulário para cadastrar sem precisar escrever código.

### Rotas da API (seguindo o aninhamento)

| Método | Rota | O que faz |
|---|---|---|
| POST | `/tutores` | Cadastra um tutor |
| POST | `/tutores/{tutor_id}/pets` | Adiciona um pet **dentro** de um tutor |
| POST | `/tutores/{tutor_id}/pets/{pet_id}/visitas` | Adiciona uma visita **dentro** de um pet |
| POST | `/prestadores` | Cadastra um prestador |
| GET | `/tutores` · `/prestadores` | Lista o que está cadastrado |

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
   O script cria o banco `patinhas_carinho` com as coleções `tutores` (com pets e visitas aninhados) e `prestadores`, e insere dados fictícios. A cada execução, as coleções são apagadas e recriadas.
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
| `A1/modelos.py` | Modelos Pydantic (tutor → pets → visitas; prestador) |
| `A1/criar_banco.py` | Criação das coleções e inserção dos documentos de exemplo |
| `A1/main.py` | API FastAPI com as rotas aninhadas e de listagem |
| `A1/app.py` | Formulário web (Streamlit) de cadastro |
| `A1/requirements.txt` | Bibliotecas Python necessárias |
| `A1/.env.exemplo` | Modelo do arquivo de configuração da conexão |
