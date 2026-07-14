import streamlit as st

from auth import exigir_login
from db import get_session
from utils import anexos_de, buscar, clientes_conhecidos

exigir_login()
session = get_session()

st.title("🧭 Visão 360º por Cliente")
st.caption("Veja tudo relacionado a um cliente em um só lugar: audiências, acordos, prazos, pendências e anexos.")

conhecidos = clientes_conhecidos(session)

col1, col2 = st.columns([2, 2])
with col1:
    escolhido = st.selectbox("Selecione um cliente conhecido", ["—"] + conhecidos)
with col2:
    digitado = st.text_input("...ou digite qualquer nome/parte", placeholder="ex.: Caratinga, Fernando, JR...")

nome = digitado.strip() if digitado.strip() else (escolhido if escolhido != "—" else "")

if not nome:
    st.info("Escolha um cliente na lista ou digite um nome para ver a visão consolidada.")
else:
    resultados = buscar(session, nome)

    if not resultados:
        st.warning(f"Nada encontrado para **{nome}**.")
    else:
        total_registros = sum(len(df) for _, _, df in resultados)
        total_anexos = 0
        for _nome, modelo, df in resultados:
            for registro_id in df["id"]:
                total_anexos += len(anexos_de(session, modelo.__tablename__, int(registro_id)))

        c1, c2, c3 = st.columns(3)
        c1.metric("Cliente", nome)
        c2.metric("Registros encontrados", total_registros)
        c3.metric("📎 Anexos", total_anexos)

        st.divider()

        for categoria, modelo, df in resultados:
            with st.expander(f"{categoria} — {len(df)} registro(s)", expanded=True):
                st.dataframe(df.drop(columns=["id"], errors="ignore"), use_container_width=True, hide_index=True)

                for _, row in df.iterrows():
                    anexos = anexos_de(session, modelo.__tablename__, int(row["id"]))
                    for anexo in anexos:
                        st.caption(f"📎 {anexo.nome_arquivo} — ligado a este registro")

session.close()
