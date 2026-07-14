import streamlit as st

from auth import exigir_login
from crud import editor_tabela
from db import Audiencia, Reuniao, get_session

exigir_login()
session = get_session()

st.title("📅 Agenda — Audiências e Reuniões")
st.caption("Adicione uma linha no final da tabela para cadastrar. Edite células direto. Para excluir, selecione a linha e aperte a lixeira.")

tab1, tab2 = st.tabs(["Audiências", "Reuniões / Perícias"])

with tab1:
    editor_tabela(
        session,
        Audiencia,
        "Audiências",
        column_config={
            "data": st.column_config.TextColumn("Data (dd/mm/aaaa)"),
            "horario": st.column_config.TextColumn("Horário"),
            "partes": st.column_config.TextColumn("Partes", width="large"),
            "processo": st.column_config.TextColumn("Processo"),
            "audiencia": st.column_config.TextColumn("Audiência", width="large"),
            "responsavel": st.column_config.TextColumn("Responsável"),
        },
    )

with tab2:
    editor_tabela(
        session,
        Reuniao,
        "Reuniões / Perícias",
        column_config={
            "data": st.column_config.TextColumn("Data (dd/mm/aaaa)"),
            "horario": st.column_config.TextColumn("Horário"),
            "cliente": st.column_config.TextColumn("Cliente"),
            "assunto": st.column_config.TextColumn("Assunto", width="large"),
        },
    )

session.close()
