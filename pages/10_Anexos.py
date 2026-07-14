import os
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st

from auth import exigir_login
from db import Anexo, get_session
from utils import TABELAS_BUSCAVEIS, rotulo_registro

exigir_login()

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")

session = get_session()

st.title("📎 Anexos")
st.caption("Vincule PDFs e outros documentos (petições, contratos, comprovantes) a um registro específico do sistema.")

tab_upload, tab_lista = st.tabs(["Enviar novo anexo", "Anexos existentes"])

with tab_upload:
    nomes_tabelas = [nome for nome, _modelo, _cols in TABELAS_BUSCAVEIS]
    categoria = st.selectbox("Categoria", nomes_tabelas)
    modelo = next(m for nome, m, _cols in TABELAS_BUSCAVEIS if nome == categoria)
    colunas = next(c for nome, _m, c in TABELAS_BUSCAVEIS if nome == categoria)

    df = pd.read_sql(session.query(modelo).statement, session.bind)

    if df.empty:
        st.info(f"Não há registros cadastrados em '{categoria}' ainda.")
    else:
        opcoes = {int(row["id"]): rotulo_registro(row, colunas) for _, row in df.iterrows()}
        registro_id = st.selectbox(
            "Registro",
            options=list(opcoes.keys()),
            format_func=lambda rid: opcoes[rid],
        )

        arquivo = st.file_uploader("Arquivo (PDF, imagem, documento)", type=None)

        if st.button("Salvar anexo", disabled=arquivo is None):
            pasta_destino = os.path.join(UPLOADS_DIR, modelo.__tablename__)
            os.makedirs(pasta_destino, exist_ok=True)

            extensao = os.path.splitext(arquivo.name)[1]
            nome_unico = f"{uuid.uuid4().hex}{extensao}"
            caminho_completo = os.path.join(pasta_destino, nome_unico)

            with open(caminho_completo, "wb") as f:
                f.write(arquivo.getbuffer())

            session.add(
                Anexo(
                    tabela_origem=modelo.__tablename__,
                    registro_id=registro_id,
                    descricao_registro=opcoes[registro_id],
                    nome_arquivo=arquivo.name,
                    caminho_arquivo=caminho_completo,
                    data_upload=datetime.now(),
                )
            )
            session.commit()
            st.success(f"Anexo '{arquivo.name}' salvo em '{categoria}' — {opcoes[registro_id]}")
            st.rerun()

with tab_lista:
    anexos = session.query(Anexo).order_by(Anexo.data_upload.desc()).all()
    if not anexos:
        st.info("Nenhum anexo enviado ainda.")
    else:
        nomes_por_tabela = {m.__tablename__: nome for nome, m, _c in TABELAS_BUSCAVEIS}
        for anexo in anexos:
            categoria_legivel = nomes_por_tabela.get(anexo.tabela_origem, anexo.tabela_origem)
            with st.container(border=True):
                col_info, col_acoes = st.columns([4, 1])
                with col_info:
                    st.markdown(f"**{anexo.nome_arquivo}**")
                    st.caption(f"{categoria_legivel} — {anexo.descricao_registro}")
                    if anexo.data_upload:
                        st.caption(f"Enviado em {anexo.data_upload.strftime('%d/%m/%Y %H:%M')}")
                with col_acoes:
                    if os.path.exists(anexo.caminho_arquivo):
                        with open(anexo.caminho_arquivo, "rb") as f:
                            st.download_button(
                                "⬇️ Baixar",
                                data=f.read(),
                                file_name=anexo.nome_arquivo,
                                key=f"baixar_{anexo.id}",
                            )
                    else:
                        st.caption("⚠️ Arquivo não encontrado no disco")
                    if st.button("🗑️ Excluir", key=f"excluir_{anexo.id}"):
                        if os.path.exists(anexo.caminho_arquivo):
                            os.remove(anexo.caminho_arquivo)
                        session.delete(anexo)
                        session.commit()
                        st.rerun()

session.close()
