import streamlit as st

from auth import exigir_login
from crud import editor_tabela
from db import Acao, ProcessoNaoCitado, get_session

exigir_login()
session = get_session()

st.title("📁 Ações e Processos")

tab1, tab2 = st.tabs(["Ações", "Processos não citados"])

with tab1:
    editor_tabela(
        session,
        Acao,
        "Ações",
        column_config={
            "partes": st.column_config.TextColumn("Partes", width="large"),
            "finalidade": st.column_config.TextColumn("Finalidade", width="large"),
            "responsavel": st.column_config.TextColumn("Responsável"),
        },
    )

with tab2:
    editor_tabela(
        session,
        ProcessoNaoCitado,
        "Processos não citados",
        column_config={
            "tribunal": st.column_config.TextColumn("Tribunal"),
            "processo": st.column_config.TextColumn("Processo"),
            "partes": st.column_config.TextColumn("Partes", width="large"),
            "situacao": st.column_config.TextColumn("Situação", width="large"),
            "responsavel": st.column_config.TextColumn("Responsável"),
        },
    )

session.close()
