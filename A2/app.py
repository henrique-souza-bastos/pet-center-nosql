"""
Formulário web (Streamlit) do Pet Center.

A primeira tela só oferece ENTRAR ou CRIAR CONTA. O login é feito pelo nome
de usuário (sem senha) e é a conta que define o perfil: depois de entrar, a
pessoa só enxerga a área do perfil dela.

- TUTOR: cadastra os próprios pets, vê a vitrine de
  serviços, solicita um serviço escolhendo a data (sem poder mexer no valor,
  que o sistema calcula) e acompanha seus agendamentos.
- PRESTADOR: monta o catálogo de serviços, recebe as
  solicitações e ACEITA ou RECUSA cada uma.

Datas aparecem sempre no formato brasileiro (DD/MM/AAAA). No banco elas são
guardadas no padrão internacional (AAAA-MM-DD), que é o correto para ordenar
e comparar.

[A2] Novidades da A2 (o resto do arquivo é igual ao da A1), sempre dentro de
blocos marcados com "[A2]":
- TUTOR: aba "Para o meu pet (A2)" - mostra só os serviços compatíveis com o
  pet escolhido, dos mais contratados para os menos contratados.
- PRESTADOR: aba "Faturamento (A2)" - quanto faturou por mês e por tipo.
As duas abas só exibem o resultado; a consulta é feita no banco pelos
pipelines de agregação de consultas.py.

Autores: Henrique Souza e Yuri Cainã

Como rodar (a API precisa estar rodando antes):  streamlit run app.py
"""
from datetime import date, datetime, time, timedelta
from urllib.parse import quote

import requests
import streamlit as st

API_URL = "http://localhost:8000"
FORMATO = "DD/MM/YYYY"          # formato mostrado nos seletores de data

ESPECIES = ["Cachorro", "Gato", "Outro"]
PORTES = ["Pequeno", "Médio", "Grande"]

HOJE = date.today()
MIN_ADULTO, MIN_PET = date(1930, 1, 1), date(1995, 1, 1)
MAX_AGENDA = HOJE + timedelta(days=365)

st.set_page_config(page_title="Pet Center", page_icon="🐾", layout="centered")
st.title("🐾 Pet Center")


# ---------------------------------------------------------------------
# Conversa com a API
# ---------------------------------------------------------------------
def buscar(caminho):
    try:
        resposta = requests.get(f"{API_URL}{caminho}", timeout=10)
        if resposta.status_code == 200:
            return resposta.json()
    except requests.exceptions.ConnectionError:
        st.error("API offline. Rode 'python -m uvicorn main:app' em outro terminal.")
    return []


def enviar(caminho, payload, sucesso="Cadastrado com sucesso!"):
    try:
        resposta = requests.post(f"{API_URL}{caminho}", json=payload, timeout=10)
        if resposta.status_code == 200:
            st.success(sucesso)
            return True
        st.error(f"Não deu certo: {resposta.json().get('detail')}")
    except requests.exceptions.ConnectionError:
        st.error("API offline. Rode 'python -m uvicorn main:app' em outro terminal.")
    return False


def mudar_status(evento_id, status):
    try:
        resposta = requests.patch(
            f"{API_URL}/eventos/{evento_id}/status", json={"status": status}, timeout=10
        )
        if resposta.status_code == 200:
            return True
        st.error(f"Não deu certo: {resposta.json().get('detail')}")
    except requests.exceptions.ConnectionError:
        st.error("API offline.")
    return False


# ---------------------------------------------------------------------
# Datas no formato brasileiro
# ---------------------------------------------------------------------
def br(valor, com_hora=False):
    """Mostra uma data vinda do banco no formato DD/MM/AAAA."""
    if not valor:
        return "—"
    texto = str(valor)
    try:
        momento = datetime.fromisoformat(texto.replace("Z", "+00:00"))
        return momento.strftime("%d/%m/%Y %H:%M" if com_hora else "%d/%m/%Y")
    except ValueError:
        try:
            return datetime.strptime(texto[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return texto


def rotulo_servico(s):
    if s.get("tipo") == "Hospedagem":
        return (
            f"{s.get('prestador_nome')} · Hospedagem · R$ {s.get('valor', 0):.2f} a diária"
            f" (até {s.get('max_diarias') or 10} diárias)"
        )
    return (
        f"{s.get('prestador_nome')} · Passeio {s.get('tempo_duracao') or ''}"
        f" · R$ {s.get('valor', 0):.2f}"
    )


# =====================================================================
# ENTRADA NO SISTEMA (login por usuário, sem senha, e criação de conta)
# O Streamlit roda o arquivo inteiro a cada clique; o st.session_state é a
# "memória" que guarda quem está conectado entre um clique e outro.
# =====================================================================
st.session_state.setdefault("usuario", None)   # quem está conectado
st.session_state.setdefault("tela", "inicio")  # inicio | login | cadastro


def ir_para(tela):
    st.session_state["tela"] = tela
    st.rerun()


def carregar_conta(usuario, avisar=True):
    """Pergunta à API de quem é esse usuário. Devolve None se não achar."""
    try:
        resposta = requests.get(f"{API_URL}/login/{quote(usuario, safe='')}", timeout=10)
        if resposta.status_code == 200:
            return resposta.json()
        if avisar:
            st.error(resposta.json().get("detail"))
    except requests.exceptions.ConnectionError:
        st.error("API offline. Rode 'python -m uvicorn main:app' em outro terminal.")
    return None


if not st.session_state["usuario"]:
    tela = st.session_state["tela"]

    # ---------------- primeira tela: só duas opções ----------------
    if tela == "inicio":
        st.subheader("Boas-vindas!")
        st.write("Passeios e hospedagem para o seu pet, com quem entende do assunto.")
        with st.container(border=True):
            if st.button("Entrar", type="primary", use_container_width=True):
                ir_para("login")
            if st.button("Criar conta", use_container_width=True):
                ir_para("cadastro")

    # ---------------- entrar ----------------
    elif tela == "login":
        st.subheader("Entrar")
        with st.form("form_login"):
            usuario = st.text_input("Usuário", placeholder="Ex: ana.souza")
            entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)
        if entrar:
            usuario = usuario.strip().lower()
            if not usuario:
                st.warning("Digite o seu usuário.")
            elif carregar_conta(usuario):
                st.session_state["usuario"] = usuario
                ir_para("inicio")
        st.caption("Ainda não tem conta?")
        if st.button("Criar conta"):
            ir_para("cadastro")
        if st.button("← Voltar"):
            ir_para("inicio")

    # ---------------- criar conta ----------------
    else:
        st.subheader("Criar conta")
        # Fica fora do formulário para a tela se ajustar na hora ao tipo escolhido.
        tipo_conta = st.radio(
            "Quero me cadastrar como", ["Tutor", "Prestador"], horizontal=True,
            captions=["Tenho pet e procuro serviços", "Ofereço passeio ou hospedagem"],
        )
        with st.form("form_cadastro"):
            usuario = st.text_input(
                "Usuário (é com ele que você vai entrar)", placeholder="Ex: ana.souza",
                help="De 3 a 30 caracteres: letras sem acento, números, ponto, hífen ou sublinhado.",
            )
            nome = st.text_input(
                "Nome completo" if tipo_conta == "Tutor" else "Nome (seu ou do estabelecimento)",
                placeholder="Ex: Ana Souza" if tipo_conta == "Tutor" else "Ex: João Passeios",
            )
            endereco = st.text_input(
                "Endereço", placeholder="Ex: Rua Goiás, 100 - Santa Mônica, Uberlândia/MG"
            )
            telefone = st.text_input("Telefone", placeholder="Ex: (34) 99999-0001")
            nascimento = st.date_input(
                "Data de nascimento", value=date(1995, 1, 1),
                min_value=MIN_ADULTO, max_value=HOJE, format=FORMATO,
            )
            if tipo_conta == "Prestador":
                tipos = st.selectbox("O que você oferece?", ["Passeio", "Hospedagem", "Ambos"])
            criar = st.form_submit_button("Criar conta", type="primary", use_container_width=True)

        if criar:
            usuario = usuario.strip().lower()
            if not (usuario and nome.strip() and telefone.strip()):
                st.warning("Preencha pelo menos usuário, nome e telefone.")
            else:
                corpo = {
                    "usuario": usuario, "nome": nome.strip(), "endereco": endereco.strip(),
                    "telefone": telefone.strip(), "data_nascimento": nascimento.isoformat(),
                }
                if tipo_conta == "Prestador":
                    corpo["tipos_servicos_gerais"] = tipos
                rota = "/tutores" if tipo_conta == "Tutor" else "/prestadores"
                # Conta criada: já entra direto, como nos sites de verdade.
                if enviar(rota, corpo, "Conta criada!"):
                    st.session_state["usuario"] = usuario
                    ir_para("inicio")
        st.caption("Já tem conta?")
        if st.button("Entrar"):
            ir_para("login")
        if st.button("← Voltar"):
            ir_para("inicio")

    st.stop()   # sem login, nada abaixo desta linha é mostrado


# ---------------- a partir daqui: usuário conectado ----------------
# A conta é buscada de novo a cada clique para a tela refletir o que mudou
# (um pet ou serviço recém-cadastrado, por exemplo).
conta = carregar_conta(st.session_state["usuario"], avisar=False)
if st.sidebar.button("Sair", use_container_width=True):
    st.session_state["usuario"] = None
    ir_para("inicio")
if not conta:
    st.warning("Não foi possível carregar a sua conta. Tente de novo ou saia e entre outra vez.")
    st.stop()

# O perfil vem do banco, não de uma escolha na tela: quem entra como tutor só
# enxerga a área de tutor, e quem entra como prestador só a de prestador.
perfil, eu = conta["perfil"], conta["dados"]
st.sidebar.markdown(f"**{eu['nome']}**")
st.sidebar.caption(f"@{eu.get('usuario', '')} · {perfil}")


# =====================================================================
# PERFIL TUTOR
# =====================================================================
if perfil == "Tutor":
    st.caption(f"Conectado como tutor: **{eu['nome']}**")
    meus_pets = eu.get("pets", [])
    # [A2] a quarta aba (aba_para_pet) é nova
    aba_pets, aba_servicos, aba_agenda, aba_para_pet = st.tabs(
        ["🐾 Meus pets", "🔎 Serviços disponíveis", "📅 Meus agendamentos",
         "✨ Para o meu pet (A2)"]
    )

    # --- meus pets ---
    with aba_pets:
        if meus_pets:
            st.table([
                {
                    "Nome": p.get("nome", ""),
                    "Espécie": p.get("especie", ""),
                    "Raça": p.get("raca", ""),
                    "Porte": p.get("porte", ""),
                    "Peso (kg)": p.get("peso_kg", ""),
                    "Nascimento": f"{br((p.get('data_nascimento') or {}).get('data'))}"
                                  f" ({(p.get('data_nascimento') or {}).get('tipo', '')})",
                    "Alergia": "Sim" if p.get("possui_alergia") else "Não",
                    "Passeios/dia": p.get("qtde_passeios_dia", ""),
                }
                for p in meus_pets
            ])
        else:
            st.info("Você ainda não cadastrou nenhum pet.")

        with st.expander("➕ Cadastrar um pet", expanded=not meus_pets):
            with st.form("form_pet"):
                nome = st.text_input("Nome do pet", placeholder="Ex: Rex")
                especie = st.selectbox("Espécie", ESPECIES)
                raca = st.text_input("Raça", value="SRD")
                peso = st.number_input("Peso (kg)", min_value=0.1, value=10.0, step=0.5)
                porte = st.selectbox("Porte", PORTES)
                nasc = st.date_input(
                    "Data de nascimento do pet", value=date(2021, 1, 1),
                    min_value=MIN_PET, max_value=HOJE, format=FORMATO,
                )
                nasc_tipo = st.selectbox("Essa data é", ["Exata", "Aproximada"])
                tem_alergia = st.checkbox("Possui alergia ou doença")
                detalhes = st.text_input("Detalhes da alergia/doença (se houver)")
                qtde = st.selectbox("Passeios por dia", [1, 2, 3])
                obs = st.text_area("Observações (opcional)")
                if st.form_submit_button("Cadastrar pet"):
                    if enviar(f"/tutores/{eu['_id']}/pets", {
                        "nome": nome, "especie": especie, "raca": raca,
                        "peso_kg": peso, "porte": porte,
                        "data_nascimento": {"data": nasc.isoformat(), "tipo": nasc_tipo},
                        "possui_alergia": tem_alergia,
                        "detalhes_alergia": detalhes if tem_alergia else None,
                        "qtde_passeios_dia": qtde,
                        "observacoes": obs or None,
                    }, "Pet cadastrado!"):
                        st.rerun()

    # --- vitrine de serviços + solicitação ---
    with aba_servicos:
        catalogo = buscar("/servicos")
        if not catalogo:
            st.info("Ainda não há serviços cadastrados pelos prestadores.")
        else:
            st.dataframe(
                [
                    {
                        "Prestador": s.get("prestador_nome", ""),
                        "Tipo": s.get("tipo", ""),
                        "Duração / diárias": (
                            f"até {s.get('max_diarias')} diárias"
                            if s.get("tipo") == "Hospedagem"
                            else s.get("tempo_duracao", "")
                        ),
                        "Valor (R$)": s.get("valor", ""),
                        "Espécies": ", ".join(s.get("especies_aceitas", [])),
                        "Portes": ", ".join(s.get("portes_aceitos", [])),
                        "Aceita alergia": "Sim" if s.get("aceita_animais_com_alergia_doenca") else "Não",
                    }
                    for s in catalogo
                ],
                use_container_width=True, hide_index=True,
            )

            st.divider()
            st.markdown("### Solicitar um serviço")
            if not meus_pets:
                st.warning("Cadastre um pet antes de solicitar um serviço.")
            else:
                servico = st.selectbox(
                    "Escolha o serviço", catalogo, format_func=rotulo_servico
                )
                pets_escolhidos = st.multiselect(
                    "Para qual(is) pet(s)?", meus_pets,
                    format_func=lambda p: p["nome"], default=[meus_pets[0]],
                )
                coluna_data, coluna_hora = st.columns(2)
                with coluna_data:
                    dia = st.date_input(
                        "Data desejada", value=HOJE,
                        min_value=HOJE, max_value=MAX_AGENDA, format=FORMATO,
                    )
                with coluna_hora:
                    hora = st.time_input("Horário", value=time(8, 0))

                if servico.get("tipo") == "Hospedagem":
                    diarias = st.number_input(
                        "Quantas diárias?", min_value=1,
                        max_value=int(servico.get("max_diarias") or 10), value=1, step=1,
                    )
                    total = float(servico.get("valor", 0)) * diarias
                else:
                    diarias = None
                    total = float(servico.get("valor", 0))

                st.metric("Valor total (calculado pelo sistema)", f"R$ {total:.2f}")
                st.caption("O valor é definido pelo serviço: você não precisa preenchê-lo.")

                if st.button("Solicitar serviço", type="primary"):
                    if not pets_escolhidos:
                        st.warning("Escolha pelo menos um pet.")
                    else:
                        corpo = {
                            "tutor_id": eu["_id"],
                            "prestador_id": servico["prestador_id"],
                            "servico_id": servico["servico_id"],
                            "pets_envolvidos": [p["pet_id"] for p in pets_escolhidos],
                            "data_inicio": datetime.combine(dia, hora).isoformat(),
                        }
                        if diarias:
                            corpo["qtde_diarias"] = int(diarias)
                        enviar("/eventos", corpo,
                               "Solicitação enviada! Aguarde o prestador aceitar.")

    # --- meus agendamentos ---
    with aba_agenda:
        meus_eventos = buscar(f"/eventos?tutor_id={eu['_id']}")
        if not meus_eventos:
            st.info("Você ainda não solicitou nenhum serviço.")
        else:
            st.dataframe(
                [
                    {
                        "Situação": e.get("status", ""),
                        "Tipo": e.get("tipo_evento", ""),
                        "Prestador": (e.get("snapshot") or {}).get("prestador_nome", ""),
                        "Pets": ", ".join((e.get("snapshot") or {}).get("pets_nomes", [])),
                        "Início": br(e.get("data_inicio"), com_hora=True),
                        "Fim": br(e.get("data_fim"), com_hora=True),
                        "Diárias": e.get("qtde_diarias") or "—",
                        "Total (R$)": e.get("valor_total", ""),
                    }
                    for e in meus_eventos
                ],
                use_container_width=True, hide_index=True,
            )

    # =============================================================
    # [A2] ABA NOVA - serviços compatíveis com o pet escolhido
    # Pipeline: $unwind -> $match -> $lookup -> $addFields -> $sort
    # (função servicos_compativeis, em consultas.py)
    # =============================================================
    with aba_para_pet:
        st.caption(
            "Escolha um pet: o sistema mostra só os serviços que aceitam a "
            "espécie, o porte e a condição de saúde dele, começando pelos "
            "mais contratados."
        )
        if not meus_pets:
            st.info("Cadastre um pet para ver os serviços compatíveis com ele.")
        else:
            pet = st.selectbox(
                "Para qual pet?", meus_pets,
                format_func=lambda p: (
                    f"{p['nome']} · {p.get('especie', '')} · porte {p.get('porte', '')}"
                    + (" · com alergia/doença" if p.get("possui_alergia") else "")
                ),
                key="a2_pet",
            )
            compativeis = buscar(
                f"/tutores/{eu['_id']}/pets/{pet['pet_id']}/servicos-compativeis"
            )
            if not compativeis:
                st.warning(f"Nenhum serviço cadastrado aceita {pet['nome']} no momento.")
            else:
                st.success(
                    f"{len(compativeis)} serviço(s) compatível(is) com {pet['nome']}."
                )
                st.dataframe(
                    [
                        {
                            "Prestador": s.get("prestador_nome", ""),
                            "Tipo": s.get("tipo", ""),
                            "Duração / diárias": (
                                f"até {s.get('max_diarias')} diárias"
                                if s.get("tipo") == "Hospedagem"
                                else s.get("tempo_duracao", "")
                            ),
                            "Valor (R$)": s.get("valor", ""),
                            "Vezes contratado": s.get("vezes_contratado", 0),
                        }
                        for s in compativeis
                    ],
                    use_container_width=True, hide_index=True,
                )
                st.caption(
                    "Para contratar, use a aba “Serviços disponíveis”. "
                    "“Vezes contratado” conta os serviços já concluídos."
                )
    # ===== fim [A2] =====


# =====================================================================
# PERFIL PRESTADOR
# =====================================================================
else:
    st.caption(f"Conectado como prestador: **{eu['nome']}**")
    meus_servicos = eu.get("servicos_oferecidos", [])
    # [A2] a quarta aba (aba_faturamento) é nova
    aba_servicos, aba_pedidos, aba_agenda, aba_faturamento = st.tabs(
        ["🧾 Meus serviços", "📬 Solicitações", "📅 Minha agenda",
         "💰 Faturamento (A2)"]
    )

    # --- catálogo do prestador ---
    with aba_servicos:
        if meus_servicos:
            st.table([
                {
                    "Tipo": s.get("tipo", ""),
                    "Duração / diárias": (
                        f"até {s.get('max_diarias')} diárias"
                        if s.get("tipo") == "Hospedagem" else s.get("tempo_duracao", "")
                    ),
                    "Valor (R$)": s.get("valor", ""),
                    "Espécies": ", ".join(s.get("especies_aceitas", [])),
                    "Portes": ", ".join(s.get("portes_aceitos", [])),
                    "Aceita alergia": "Sim" if s.get("aceita_animais_com_alergia_doenca") else "Não",
                }
                for s in meus_servicos
            ])
        else:
            st.info("Você ainda não cadastrou nenhum serviço.")

        with st.expander("➕ Cadastrar um serviço", expanded=not meus_servicos):
            tipo = st.selectbox("Tipo de serviço", ["Passeio", "Hospedagem"])
            if tipo == "Hospedagem":
                duracao = None
                max_diarias = st.number_input(
                    "Diárias disponíveis (de 1 a 10)",
                    min_value=1, max_value=10, value=5, step=1,
                )
                valor = st.number_input(
                    "Valor da DIÁRIA (R$)", min_value=0.0, value=60.0, step=5.0
                )
            else:
                max_diarias = None
                duracao = st.text_input("Tempo de duração", value="30 min")
                valor = st.number_input(
                    "Valor do passeio (R$)", min_value=0.0, value=25.0, step=5.0
                )
            especies = st.multiselect("Espécies aceitas", ESPECIES, default=["Cachorro"])
            portes = st.multiselect("Portes aceitos", PORTES, default=PORTES)
            aceita = st.checkbox("Aceito animais com alergia/doença")

            if st.button("Cadastrar serviço", type="primary"):
                corpo = {
                    "tipo": tipo,
                    "tempo_duracao": duracao,
                    "max_diarias": int(max_diarias) if max_diarias else None,
                    "especies_aceitas": especies,
                    "portes_aceitos": portes,
                    "valor": valor,
                    "aceita_animais_com_alergia_doenca": aceita,
                }
                if enviar(f"/prestadores/{eu['_id']}/servicos", corpo, "Serviço cadastrado!"):
                    st.rerun()

    # --- solicitações para aceitar ou recusar ---
    with aba_pedidos:
        pedidos = buscar(f"/eventos?prestador_id={eu['_id']}&status=Solicitado")
        if not pedidos:
            st.info("Nenhuma solicitação pendente.")
        for pedido in pedidos:
            snap = pedido.get("snapshot") or {}
            with st.container(border=True):
                st.markdown(
                    f"**{pedido.get('tipo_evento')}** para "
                    f"**{', '.join(snap.get('pets_nomes', []))}** "
                    f"— tutor {snap.get('tutor_nome', '')}"
                )
                detalhe = f"🗓️ {br(pedido.get('data_inicio'), com_hora=True)}"
                if pedido.get("qtde_diarias"):
                    detalhe += f"  ·  {pedido['qtde_diarias']} diária(s)"
                detalhe += f"  ·  💰 R$ {pedido.get('valor_total', 0):.2f}"
                st.write(detalhe)

                botao_sim, botao_nao = st.columns(2)
                with botao_sim:
                    if st.button("✅ Aceitar", key=f"ok_{pedido['_id']}",
                                 type="primary", use_container_width=True):
                        if mudar_status(pedido["_id"], "Confirmado"):
                            st.rerun()
                with botao_nao:
                    if st.button("❌ Recusar", key=f"no_{pedido['_id']}",
                                 use_container_width=True):
                        if mudar_status(pedido["_id"], "Cancelado"):
                            st.rerun()

    # --- agenda do prestador ---
    with aba_agenda:
        agenda = [
            e for e in buscar(f"/eventos?prestador_id={eu['_id']}")
            if e.get("status") != "Solicitado"
        ]
        if not agenda:
            st.info("Nada agendado ainda.")
        else:
            st.dataframe(
                [
                    {
                        "Situação": e.get("status", ""),
                        "Tipo": e.get("tipo_evento", ""),
                        "Tutor": (e.get("snapshot") or {}).get("tutor_nome", ""),
                        "Pets": ", ".join((e.get("snapshot") or {}).get("pets_nomes", [])),
                        "Início": br(e.get("data_inicio"), com_hora=True),
                        "Fim": br(e.get("data_fim"), com_hora=True),
                        "Diárias": e.get("qtde_diarias") or "—",
                        "Total (R$)": e.get("valor_total", ""),
                    }
                    for e in agenda
                ],
                use_container_width=True, hide_index=True,
            )

    # =============================================================
    # [A2] ABA NOVA - painel de faturamento do prestador
    # Pipeline: $match -> $group -> $sort -> $project
    # (função faturamento_prestador, em consultas.py)
    # =============================================================
    with aba_faturamento:
        st.caption(
            "Considera apenas os serviços com situação “Concluído”: pedidos "
            "pendentes, confirmados ou cancelados não entram na conta."
        )
        resumo = buscar(f"/prestadores/{eu['_id']}/faturamento")
        if not resumo:
            st.info("Você ainda não tem serviços concluídos.")
        else:
            total = sum(linha.get("faturamento", 0) for linha in resumo)
            quantidade = sum(linha.get("quantidade", 0) for linha in resumo)
            coluna_total, coluna_qtde, coluna_media = st.columns(3)
            coluna_total.metric("Total faturado", f"R$ {total:.2f}")
            coluna_qtde.metric("Serviços concluídos", quantidade)
            coluna_media.metric("Ticket médio", f"R$ {total / quantidade:.2f}")

            st.dataframe(
                [
                    {
                        # o banco devolve "2026-10"; na tela vira "10/2026"
                        "Mês": f"{linha['mes'][5:]}/{linha['mes'][:4]}",
                        "Tipo": linha.get("tipo", ""),
                        "Serviços": linha.get("quantidade", 0),
                        "Faturamento (R$)": linha.get("faturamento", 0),
                        "Ticket médio (R$)": linha.get("ticket_medio", 0),
                    }
                    for linha in resumo
                ],
                use_container_width=True, hide_index=True,
            )

            # No gráfico o mês fica como "2026-10" de propósito: nesse
            # formato a ordem alfabética é também a ordem cronológica.
            st.bar_chart(
                [
                    {
                        "Mês": linha["mes"],
                        "Faturamento (R$)": linha.get("faturamento", 0),
                        "Tipo": linha.get("tipo", ""),
                    }
                    for linha in resumo
                ],
                x="Mês", y="Faturamento (R$)", color="Tipo",
            )
    # ===== fim [A2] =====
