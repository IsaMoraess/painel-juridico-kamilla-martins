import pandas as pd
import streamlit as st

from auth import eh_admin, exigir_login
from db import (
    Acao,
    AcordoFinanceiro,
    Alerta,
    Audiencia,
    CnpjConsulta,
    Credencial,
    Manifestacao,
    PendenciaCliente,
    ProcessoNaoCitado,
    Reuniao,
    TarefaRecorrente,
    get_session,
)

exigir_login()

if not eh_admin():
    st.error("Apenas administradores podem acessar esta página.")
    st.stop()

session = get_session()

st.title("⬆️ Importar Dados (CSV)")
st.caption(
    "Envie os arquivos CSV gerados a partir do PDF original para popular este ambiente. "
    "Os arquivos ficam só na memória desta sessão — nunca vão para o repositório do GitHub."
)


def to_float(v):
    if pd.isna(v) or v in (None, "", "nan"):
        return None
    return float(v)


def to_int(v):
    if pd.isna(v) or v in (None, "", "nan"):
        return None
    return int(float(v))


def ler_csv(arquivo):
    return pd.read_csv(arquivo, dtype=str, keep_default_na=False)


def importar_generico(arquivo, titulo, inserir_linha):
    if arquivo is None:
        return
    df = ler_csv(arquivo)
    qtd = 0
    for _, r in df.iterrows():
        obj = inserir_linha(r)
        if obj is not None:
            session.add(obj)
            qtd += 1
    session.commit()
    st.success(f"{titulo}: {qtd} registro(s) importado(s).")


st.divider()
col1, col2 = st.columns(2)

with col1:
    f_audiencias = st.file_uploader("audiencias.csv", type="csv", key="up_audiencias")
    if st.button("Importar Audiências", disabled=f_audiencias is None):
        importar_generico(
            f_audiencias,
            "Audiências",
            lambda r: Audiencia(data=r["data"], horario=r["horario"], partes=r["partes"], processo=r["processo"], audiencia=r["audiencia"]),
        )

    f_reunioes = st.file_uploader("reunioes.csv", type="csv", key="up_reunioes")
    if st.button("Importar Reuniões", disabled=f_reunioes is None):
        importar_generico(
            f_reunioes,
            "Reuniões",
            lambda r: Reuniao(data=r["data"], horario=r["horario"], cliente=r["cliente"], assunto=r["assunto"]),
        )

    f_acordos = st.file_uploader("acordos_financeiros.csv", type="csv", key="up_acordos")
    if st.button("Importar Acordos Financeiros", disabled=f_acordos is None):
        importar_generico(
            f_acordos,
            "Acordos Financeiros",
            lambda r: AcordoFinanceiro(
                partes=r["partes"],
                valor_total=to_float(r["valor_total"]),
                valor_parcela=to_float(r["valor_parcela"]),
                qtd_parcelas=to_int(r["qtd_parcelas"]),
                data_inicio=r["data_inicio"],
                data_fim=r["data_fim"],
                dia_vencimento=to_int(r["dia_vencimento"]),
                observacao=r["observacao"],
            ),
        )

    f_manifestacoes = st.file_uploader("manifestacoes.csv", type="csv", key="up_manifestacoes")
    if st.button("Importar Prazos e Manifestações", disabled=f_manifestacoes is None):
        importar_generico(
            f_manifestacoes,
            "Manifestações",
            lambda r: Manifestacao(
                processo=r["processo"],
                partes=r["partes"],
                finalidade=r["finalidade"],
                prazo_juridico=r["prazo_juridico"],
                prazo_fatal=r["prazo_fatal"],
            ),
        )

    f_acoes = st.file_uploader("acoes.csv", type="csv", key="up_acoes")
    if st.button("Importar Ações", disabled=f_acoes is None):
        importar_generico(f_acoes, "Ações", lambda r: Acao(partes=r["partes"], finalidade=r["finalidade"]))

with col2:
    f_processos = st.file_uploader("processos_nao_citados.csv", type="csv", key="up_processos")
    if st.button("Importar Processos não citados", disabled=f_processos is None):
        importar_generico(
            f_processos,
            "Processos não citados",
            lambda r: ProcessoNaoCitado(tribunal=r["tribunal"], processo=r["processo"], partes=r["partes"], situacao=r["situacao"]),
        )

    f_pendencias = st.file_uploader("pendencias_cliente.csv", type="csv", key="up_pendencias")
    if st.button("Importar Pendências por Cliente", disabled=f_pendencias is None):
        importar_generico(
            f_pendencias,
            "Pendências por Cliente",
            lambda r: None
            if r["atividade_pendente"].strip().lower() == "nada"
            else PendenciaCliente(cliente=r["cliente"], atividade_pendente=r["atividade_pendente"]),
        )

    f_tarefas = st.file_uploader("tarefas_recorrentes.csv", type="csv", key="up_tarefas")
    if st.button("Importar Tarefas Recorrentes", disabled=f_tarefas is None):
        importar_generico(
            f_tarefas,
            "Tarefas Recorrentes",
            lambda r: TarefaRecorrente(descricao=r["descricao"], frequencia=r["frequencia"], referencia=r["referencia"]),
        )

    f_cnpjs = st.file_uploader("cnpjs_consulta.csv", type="csv", key="up_cnpjs")
    if st.button("Importar CNPJs para Consulta", disabled=f_cnpjs is None):
        importar_generico(
            f_cnpjs, "CNPJs para Consulta", lambda r: CnpjConsulta(descricao=r["descricao"], cnpj=r["cnpj"], frequencia=r["frequencia"])
        )

    f_alertas = st.file_uploader("alertas.csv", type="csv", key="up_alertas")
    if st.button("Importar Alertas", disabled=f_alertas is None):
        importar_generico(f_alertas, "Alertas", lambda r: Alerta(descricao=r["descricao"]))

    f_credenciais = st.file_uploader("credenciais.csv", type="csv", key="up_credenciais")
    if st.button("Importar Credenciais", disabled=f_credenciais is None):
        importar_generico(
            f_credenciais,
            "Credenciais",
            lambda r: Credencial(sistema=r["sistema"], usuario=r["usuario"], senha=r["senha"], referencia=r["referencia"]),
        )

session.close()
