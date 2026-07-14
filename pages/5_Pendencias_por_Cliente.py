import streamlit as st

from auth import exigir_login
from crud import editor_tabela
from db import PendenciaCliente, get_session

exigir_login()
session = get_session()

st.title("✅ Pendências por Cliente")
st.caption("Marque 'concluida' quando a atividade for finalizada — o gráfico da home só conta as abertas.")

editor_tabela(
    session,
    PendenciaCliente,
    "Pendências por cliente",
    column_config={
        "cliente": st.column_config.TextColumn("Cliente"),
        "atividade_pendente": st.column_config.TextColumn("Atividade pendente", width="large"),
        "concluida": st.column_config.CheckboxColumn("Concluída"),
    },
)

session.close()
