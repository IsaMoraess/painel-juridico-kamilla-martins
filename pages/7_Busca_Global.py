import streamlit as st

from auth import exigir_login
from db import get_session
from utils import buscar

exigir_login()
session = get_session()

st.title("🔎 Busca Global")
st.caption("Procure um cliente, processo ou parte em todas as tabelas do sistema de uma vez.")

termo = st.text_input("Buscar por", placeholder="ex.: Caratinga, Fernando, 0756499-35.2026.8.07.0016...")

if termo:
    resultados = buscar(session, termo)
    if not resultados:
        st.info("Nenhum resultado encontrado.")
    else:
        total = sum(len(df) for _, _, df in resultados)
        st.success(f"{total} resultado(s) encontrado(s) em {len(resultados)} tabela(s).")
        for nome, _modelo, df in resultados:
            with st.expander(f"{nome} — {len(df)} resultado(s)", expanded=True):
                st.dataframe(df.drop(columns=["id"], errors="ignore"), use_container_width=True, hide_index=True)
else:
    st.info("Digite um termo acima para buscar em Audiências, Reuniões, Acordos, Prazos, Ações, Processos e Pendências.")

session.close()
