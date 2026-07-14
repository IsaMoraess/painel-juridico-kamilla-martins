import streamlit as st

from auth import exigir_login
from crud import editor_tabela
from db import AcordoFinanceiro, get_session

exigir_login()
session = get_session()

st.title("💰 Acordos Financeiros")
st.caption("Parcelas, valores e vencimentos dos acordos em andamento.")

editor_tabela(
    session,
    AcordoFinanceiro,
    "Acordos financeiros",
    column_config={
        "partes": st.column_config.TextColumn("Partes", width="large"),
        "valor_total": st.column_config.NumberColumn("Valor total (R$)", format="localized", step=0.01),
        "valor_parcela": st.column_config.NumberColumn("Valor da parcela (R$)", format="localized", step=0.01),
        "qtd_parcelas": st.column_config.NumberColumn("Qtd. parcelas"),
        "data_inicio": st.column_config.TextColumn("Início"),
        "data_fim": st.column_config.TextColumn("Fim"),
        "dia_vencimento": st.column_config.NumberColumn("Dia de vencimento"),
        "observacao": st.column_config.TextColumn("Observação", width="large"),
    },
)

session.close()
