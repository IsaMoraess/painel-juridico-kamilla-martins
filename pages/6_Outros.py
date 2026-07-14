import streamlit as st

from auth import eh_admin, exigir_login
from crud import editor_tabela
from db import Alerta, CnpjConsulta, Credencial, TarefaRecorrente, get_session

exigir_login()
session = get_session()

st.title("🗂️ Tarefas, CNPJs, Alertas e Credenciais")

nomes_abas = ["Tarefas recorrentes", "CNPJs para consulta", "Alertas"]
if eh_admin():
    nomes_abas.append("Credenciais")

abas = st.tabs(nomes_abas)

with abas[0]:
    editor_tabela(
        session,
        TarefaRecorrente,
        "Tarefas recorrentes",
        column_config={
            "descricao": st.column_config.TextColumn("Descrição", width="large"),
            "frequencia": st.column_config.TextColumn("Frequência"),
            "referencia": st.column_config.TextColumn("Referência"),
            "concluida": st.column_config.CheckboxColumn("Concluída"),
        },
    )

with abas[1]:
    editor_tabela(
        session,
        CnpjConsulta,
        "CNPJs para consulta",
        column_config={
            "descricao": st.column_config.TextColumn("Descrição", width="large"),
            "cnpj": st.column_config.TextColumn("CNPJ"),
            "frequencia": st.column_config.TextColumn("Frequência"),
        },
    )

with abas[2]:
    editor_tabela(
        session,
        Alerta,
        "Alertas",
        column_config={
            "descricao": st.column_config.TextColumn("Descrição", width="large"),
        },
    )

if eh_admin():
    with abas[3]:
        st.warning(
            "Atenção: estas credenciais ficam salvas em texto simples no banco. "
            "Apenas administradores veem esta aba, mas evite compartilhar acesso de admin sem necessidade."
        )
        editor_tabela(
            session,
            Credencial,
            "Credenciais",
            column_config={
                "sistema": st.column_config.TextColumn("Sistema"),
                "usuario": st.column_config.TextColumn("Usuário"),
                "senha": st.column_config.TextColumn("Senha"),
                "referencia": st.column_config.TextColumn("Referência"),
            },
        )

session.close()
