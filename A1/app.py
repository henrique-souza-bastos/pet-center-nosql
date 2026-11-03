"""
Formulário web (Streamlit) do Pet Center.

Segue o modelo aninhado: para cadastrar um PET você escolhe o TUTOR dono; para
cadastrar uma VISITA você escolhe o tutor, depois o pet, depois o prestador.

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
    ["Tutor", "Pet", "Visita", "Prestador"],
)


def buscar(caminho):
    """Faz um GET na API e devolve a lista (vazia se a API estiver fora)."""
    try:
        resposta = requests.get(f"{API_URL}{caminho}", timeout=5)
        if resposta.status_code == 200:
            return resposta.json()
    except requests.exceptions.ConnectionError:
        st.error("API offline. Rode 'python -m uvicorn main:app' em outro terminal.")
    return []


def enviar(caminho, payload):
    """Envia o payload para a API e mostra o resultado."""
    try:
        resposta = requests.post(f"{API_URL}{caminho}", json=payload, timeout=5)
        if resposta.status_code == 200:
            st.success("Cadastrado com sucesso!")
            return True
        st.error(f"Erro ao cadastrar: {resposta.json().get('detail')}")
    except requests.exceptions.ConnectionError:
        st.error("API offline. Rode 'python -m uvicorn main:app' em outro terminal.")
    return False


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
# PET (dentro de um tutor)
# ---------------------------------------------------------------------
elif entidade == "Pet":
    st.subheader("Cadastro de pet (dentro de um tutor)")
    tutores = buscar("/tutores")
    if not tutores:
        st.info("Cadastre um tutor primeiro.")
    else:
        tutor = st.selectbox("Tutor dono do pet", tutores, format_func=lambda t: t["nome"])
        with st.form("form_pet"):
            nome = st.text_input("Nome do pet", placeholder="Ex: Rex")
            especie = st.selectbox("Espécie", ["cao", "gato", "coelho", "outro"])
            raca = st.text_input("Raça (opcional)")
            porte = st.selectbox("Porte (opcional)", ["", "pequeno", "medio", "grande"])
            peso = st.number_input("Peso em kg (opcional)", min_value=0.0, value=0.0, step=0.5)
            alergias = st.text_input("Alergias (separadas por vírgula, opcional)")
            if st.form_submit_button("Cadastrar pet"):
                payload = {"nome": nome, "especie": especie}
                if raca:
                    payload["raca"] = raca
                if porte:
                    payload["porte"] = porte
                if peso:
                    payload["peso_kg"] = peso
                if alergias:
                    payload["alergias"] = [a.strip() for a in alergias.split(",")]
                enviar(f"/tutores/{tutor['_id']}/pets", payload)

# ---------------------------------------------------------------------
# VISITA (dentro de um pet)
# ---------------------------------------------------------------------
elif entidade == "Visita":
    st.subheader("Cadastro de visita (dentro de um pet)")
    tutores = buscar("/tutores")
    prestadores = buscar("/prestadores")
    if not tutores:
        st.info("Cadastre um tutor e um pet primeiro.")
    elif not prestadores:
        st.info("Cadastre um prestador primeiro.")
    else:
        tutor = st.selectbox("Tutor", tutores, format_func=lambda t: t["nome"])
        pets = tutor.get("pets", [])
        if not pets:
            st.info("Esse tutor ainda não tem pet. Cadastre um pet para ele primeiro.")
        else:
            pet = st.selectbox("Pet", pets, format_func=lambda p: p["nome"])
            prestador = st.selectbox("Prestador", prestadores, format_func=lambda p: p["nome"])
            with st.form("form_visita"):
                tipo = st.selectbox("Tipo", ["passeio", "hospedagem"])
                status = st.selectbox(
                    "Status", ["agendada", "em_andamento", "concluida", "cancelada"]
                )
                inicio = st.text_input("Início (AAAA-MM-DD HH:MM)", value="2026-10-10 08:00")
                fim = st.text_input("Fim (AAAA-MM-DD HH:MM, opcional)", value="2026-10-10 08:30")
                valor = st.number_input("Valor", min_value=0.0, value=25.0)
                nota = st.slider("Nota da avaliação", 1, 5, 5)
                comentario = st.text_input("Comentário da avaliação (opcional)")
                if st.form_submit_button("Cadastrar visita"):
                    payload = {
                        "tipo": tipo,
                        "status": status,
                        "prestador_id": prestador["_id"],
                        "prestador_nome": prestador["nome"],
                        "inicio": inicio.strip().replace(" ", "T"),
                        "valor": valor,
                        "avaliacao": {"nota": nota, "comentario": comentario or None},
                    }
                    if fim.strip():
                        payload["fim"] = fim.strip().replace(" ", "T")
                    enviar(f"/tutores/{tutor['_id']}/pets/{pet['_id']}/visitas", payload)

# ---------------------------------------------------------------------
# PRESTADOR (coleção separada)
# ---------------------------------------------------------------------
else:
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
# Lista o que já foi cadastrado, mostrando o aninhamento.
# ---------------------------------------------------------------------
st.divider()
st.subheader("📋 Já cadastrados")

aba_tutores, aba_prestadores = st.tabs(["Tutores (com pets e visitas)", "Prestadores"])

with aba_tutores:
    tutores = buscar("/tutores")
    if not tutores:
        st.caption("Nada cadastrado ainda.")
    for tutor in tutores:
        pets = tutor.get("pets", [])
        with st.expander(f"👤 {tutor['nome']} — {len(pets)} pet(s)"):
            endereco = tutor.get("endereco", {})
            st.write(
                f"✉️ {tutor.get('email', '')}  ·  📞 {tutor.get('telefone', '')}  "
                f"·  📍 {endereco.get('cidade', '')}/{endereco.get('uf', '')}"
            )
            if not pets:
                st.caption("Sem pets ainda.")
            for pet in pets:
                visitas = pet.get("visitas", [])
                st.markdown(
                    f"**🐾 {pet['nome']}** ({pet.get('especie', '')}) — {len(visitas)} visita(s)"
                )
                if visitas:
                    st.table([
                        {
                            "Tipo": v.get("tipo", ""),
                            "Status": v.get("status", ""),
                            "Prestador": v.get("prestador_nome", ""),
                            "Valor (R$)": v.get("valor", "-"),
                            "Nota": (v.get("avaliacao") or {}).get("nota", "-"),
                        }
                        for v in visitas
                    ])

with aba_prestadores:
    prestadores = buscar("/prestadores")
    if not prestadores:
        st.caption("Nada cadastrado ainda.")
    else:
        st.dataframe(
            [
                {
                    "Nome": p.get("nome", ""),
                    "Tipo": p.get("tipo", ""),
                    "Espécies aceitas": ", ".join(p.get("especies_aceitas", [])),
                    "Nº de serviços": len(p.get("servicos", [])),
                }
                for p in prestadores
            ],
            use_container_width=True,
            hide_index=True,
        )
