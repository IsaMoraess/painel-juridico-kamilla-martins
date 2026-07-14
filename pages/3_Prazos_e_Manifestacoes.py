import streamlit as st

from auth import exigir_login
from crud import editor_tabela
from db import Manifestacao, get_session
from enviar_alertas import enviar_alertas

exigir_login()
session = get_session()

st.title("⚖️ Prazos e Manifestações")
st.caption("Marque 'concluida' quando o prazo for cumprido — isso tira o item do painel de prazos abertos.")

with st.expander("📧 Alertas por e-mail"):
    st.caption(
        "Envia um e-mail com os prazos fatais que vencem nos próximos N dias. "
        "Requer configuração de SMTP no arquivo .env (veja .env.example)."
    )
    dias = st.number_input("Avisar sobre prazos vencendo em até quantos dias?", min_value=1, max_value=30, value=3)
    if st.button("Enviar alertas agora"):
        with st.spinner("Enviando..."):
            ok, mensagem = enviar_alertas(int(dias))
        if ok:
            st.success(mensagem)
        else:
            st.error(mensagem)

editor_tabela(
    session,
    Manifestacao,
    "Manifestações",
    column_config={
        "processo": st.column_config.TextColumn("Processo"),
        "partes": st.column_config.TextColumn("Partes", width="large"),
        "finalidade": st.column_config.TextColumn("Finalidade", width="large"),
        "prazo_juridico": st.column_config.TextColumn("Prazo jurídico"),
        "prazo_fatal": st.column_config.TextColumn("Prazo fatal (dd/mm/aaaa)"),
        "responsavel": st.column_config.TextColumn("Responsável"),
        "concluida": st.column_config.CheckboxColumn("Concluída"),
    },
)

session.close()
