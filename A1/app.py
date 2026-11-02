"""
Formulário web (Streamlit) do Pet Center.

Permite cadastrar tutores, pets, prestadores e visitas, enviando os dados
para a API (main.py). Escolha a entidade no menu lateral.

Autores: Henrique Souza e Yuri Cainã

Como rodar (a API precisa estar rodando antes):  streamlit run app.py
"""
import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Pet Center", page_icon="🐾")
st.title("🐾 Pet Center — Cadastro")

entidade = st.sidebar.selectbox(
    "O que você quer cadastrar?",
    ["Tutor", "Pet", "Prestador", "Visita"],
)


def enviar(caminho, payload):
    """Envia o payload para a API e mostra o resultado na tela."""
    try:
        resposta = requests.post(f"{API_URL}{caminho}", json=payload)
        if resposta.status_code == 200:
            st.success(f"Cadastrado com sucesso! id: {resposta.json().get('id')}")
        else:
            st.error(f"Erro ao cadastrar: {resposta.json().get('detail')}")
    except requests.exceptions.ConnectionError:
        st.error(
            "Não foi possível conectar à API. Rode 'uvicorn main:app --reload'"
            " em outro terminal antes de usar o formulário."
        )


# ---------------------------------------------------------------------
# TUTOR
# ---------------------------------------------------------------------
if entidade == "Tutor":
    st.subheader("Cadastro de tutor")
    with st.form("form_tutor"):
        nome = st.text_input("Nome", placeholder="Ex: Ana Souza")
        email = st.text_input("E-mail", placeholder="Ex: ana@exemplo.com")
        telefone = st.text_input("Telefone", placeholder="Ex: (34) 99999-0001")
        bairro = st.text_input("Bairro", placeholder="Ex: Santa Mônica")
        cidade = st.text_input("Cidade", value="Uberlândia")
        uf = st.text_input("UF", value="MG", max_chars=2)
        if st.form_submit_button("Cadastrar tutor"):
            enviar("/tutores", {
                "nome": nome,
                "email": email,
                "telefone": telefone,
                "endereco": {"bairro": bairro, "cidade": cidade, "uf": uf},
            })

# ---------------------------------------------------------------------
# PET
# ---------------------------------------------------------------------
elif entidade == "Pet":
    st.subheader("Cadastro de pet")
    st.caption("Cole o id de um tutor já cadastrado (veja em 'Ver já cadastrados').")
    with st.form("form_pet"):
        tutor_id = st.text_input("ID do tutor")
        nome = st.text_input("Nome do pet", placeholder="Ex: Rex")
        especie = st.selectbox("Espécie", ["cao", "gato", "coelho", "outro"])
        raca = st.text_input("Raça (opcional)")
        porte = st.selectbox("Porte (opcional)", ["", "pequeno", "medio", "grande"])
        peso = st.number_input("Peso em kg (opcional)", min_value=0.0, value=0.0, step=0.5)
        alergias = st.text_input("Alergias (separadas por vírgula, opcional)")
        if st.form_submit_button("Cadastrar pet"):
            payload = {"tutor_id": tutor_id, "nome": nome, "especie": especie}
            if raca:
                payload["raca"] = raca
            if porte:
                payload["porte"] = porte
            if peso:
                payload["peso_kg"] = peso
            if alergias:
                payload["alergias"] = [a.strip() for a in alergias.split(",")]
            enviar("/pets", payload)

# ---------------------------------------------------------------------
# PRESTADOR
# ---------------------------------------------------------------------
elif entidade == "Prestador":
    st.subheader("Cadastro de prestador")
    with st.form("form_prestador"):
        tipo = st.selectbox("Tipo", ["passeador", "hospedagem"])
        nome = st.text_input("Nome", placeholder="Ex: João Passeios")
        longitude = st.number_input("Longitude", value=-48.278, format="%.6f")
        latitude = st.number_input("Latitude", value=-18.915, format="%.6f")
        especies = st.multiselect(
            "Espécies aceitas", ["cao", "gato", "coelho"], default=["cao"]
        )
        serv_nome = st.text_input("Serviço — nome", value="Passeio 30 min")
        serv_preco = st.number_input("Serviço — preço", min_value=0.0, value=25.0)
        if st.form_submit_button("Cadastrar prestador"):
            enviar("/prestadores", {
                "tipo": tipo,
                "nome": nome,
                "localizacao": {"type": "Point", "coordinates": [longitude, latitude]},
                "especies_aceitas": especies,
                "servicos": [{"nome": serv_nome, "preco": serv_preco}],
            })

# ---------------------------------------------------------------------
# VISITA
# ---------------------------------------------------------------------
else:
    st.subheader("Cadastro de visita (passeio ou hospedagem)")
    st.caption("Cole os ids de um pet e de um prestador já cadastrados.")
    with st.form("form_visita"):
        tipo = st.selectbox("Tipo", ["passeio", "hospedagem"])
        status = st.selectbox(
            "Status", ["agendada", "em_andamento", "concluida", "cancelada"]
        )
        pet_id = st.text_input("ID do pet")
        pet_nome = st.text_input("Nome do pet (cópia para o relatório)")
        prestador_id = st.text_input("ID do prestador")
        prestador_nome = st.text_input("Nome do prestador (cópia para o relatório)")
        inicio = st.text_input("Início (AAAA-MM-DD HH:MM)", value="2026-10-02 08:00")
        fim = st.text_input("Fim (AAAA-MM-DD HH:MM, opcional)", value="2026-10-02 08:30")
        valor = st.number_input("Valor", min_value=0.0, value=25.0)
        nota = st.slider("Nota da avaliação", 1, 5, 5)
        comentario = st.text_input("Comentário da avaliação (opcional)")
        if st.form_submit_button("Cadastrar visita"):
            payload = {
                "tipo": tipo,
                "status": status,
                "pet_id": pet_id,
                "pet_nome": pet_nome,
                "prestador_id": prestador_id,
                "prestador_nome": prestador_nome,
                "inicio": inicio.strip().replace(" ", "T"),
                "valor": valor,
                "avaliacao": {"nota": nota, "comentario": comentario or None},
            }
            if fim.strip():
                payload["fim"] = fim.strip().replace(" ", "T")
            enviar("/visitas", payload)


# ---------------------------------------------------------------------
# Lista o que já foi cadastrado na entidade escolhida.
# ---------------------------------------------------------------------
caminhos = {
    "Tutor": "/tutores",
    "Pet": "/pets",
    "Prestador": "/prestadores",
    "Visita": "/visitas",
}


def resumir(entidade, registros):
    """Monta uma tabela simples, só com os campos principais de cada categoria."""
    linhas = []
    for r in registros:
        if entidade == "Tutor":
            endereco = r.get("endereco", {})
            linhas.append({
                "Nome": r.get("nome", ""),
                "E-mail": r.get("email", ""),
                "Telefone": r.get("telefone", ""),
                "Cidade": endereco.get("cidade", ""),
            })
        elif entidade == "Pet":
            linhas.append({
                "Nome": r.get("nome", ""),
                "Espécie": r.get("especie", ""),
                "Raça": r.get("raca", "-"),
                "Porte": r.get("porte", "-"),
            })
        elif entidade == "Prestador":
            linhas.append({
                "Nome": r.get("nome", ""),
                "Tipo": r.get("tipo", ""),
                "Espécies aceitas": ", ".join(r.get("especies_aceitas", [])),
                "Nº de serviços": len(r.get("servicos", [])),
            })
        else:  # Visita
            avaliacao = r.get("avaliacao") or {}
            linhas.append({
                "Tipo": r.get("tipo", ""),
                "Status": r.get("status", ""),
                "Pet": r.get("pet_nome", ""),
                "Prestador": r.get("prestador_nome", ""),
                "Valor (R$)": r.get("valor", "-"),
                "Nota": avaliacao.get("nota", "-"),
            })
    return linhas


with st.expander("Ver já cadastrados", expanded=True):
    try:
        resposta = requests.get(f"{API_URL}{caminhos[entidade]}")
        if resposta.status_code == 200:
            registros = resposta.json()
            if registros:
                st.dataframe(
                    resumir(entidade, registros),
                    use_container_width=True,
                    hide_index=True,
                )
                if st.checkbox("Ver dados completos (formato técnico)"):
                    st.json(registros)
            else:
                st.info("Ainda não há nada cadastrado nesta categoria.")
        else:
            st.write("Não foi possível listar.")
    except requests.exceptions.ConnectionError:
        st.info("API offline. Rode 'python -m uvicorn main:app' para ver a lista.")
