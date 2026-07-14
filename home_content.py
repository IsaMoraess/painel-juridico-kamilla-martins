from datetime import date, datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from auth import exigir_login
from db import Audiencia, AcordoFinanceiro, Manifestacao, PendenciaCliente, Reuniao, get_session

exigir_login()

st.title("Painel Jurídico")
st.caption("Kamilla Martins Advocacia — visão geral de audiências, prazos, acordos e pendências")

session = get_session()

df_audiencias = pd.read_sql(session.query(Audiencia).statement, session.bind)
df_reunioes = pd.read_sql(session.query(Reuniao).statement, session.bind)
df_acordos = pd.read_sql(session.query(AcordoFinanceiro).statement, session.bind)
df_manif = pd.read_sql(session.query(Manifestacao).statement, session.bind)
df_pend = pd.read_sql(session.query(PendenciaCliente).statement, session.bind)

session.close()


def parse_data(valor):
    try:
        return datetime.strptime(str(valor).strip(), "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None


def parse_prazo_fatal(valor, hoje):
    """Aceita 'dd/mm/aaaa' (data completa) ou 'dd/mm' (como no PDF original,
    sem ano — assume o ano corrente, ou o próximo se já tiver passado há mais
    de 6 meses)."""
    texto = str(valor).strip()
    try:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except ValueError:
        pass
    try:
        parcial = datetime.strptime(texto, "%d/%m")
    except ValueError:
        return None
    candidata = date(hoje.year, parcial.month, parcial.day)
    if candidata < hoje - timedelta(days=180):
        candidata = date(hoje.year + 1, parcial.month, parcial.day)
    return candidata


def formatar_brl(valor, decimais=2):
    texto = f"{valor:,.{decimais}f}"
    texto = texto.replace(",", "§").replace(".", ",").replace("§", ".")
    return f"R$ {texto}"


hoje = date.today()

df_manif["data_fatal"] = df_manif["prazo_fatal"].apply(lambda v: parse_prazo_fatal(v, hoje))
prazos_abertos = df_manif[df_manif["concluida"] == False]  # noqa: E712
prazos_com_data = prazos_abertos.dropna(subset=["data_fatal"])
prazos_vencendo = prazos_com_data[
    (prazos_com_data["data_fatal"] >= hoje) & (prazos_com_data["data_fatal"] <= hoje + pd.Timedelta(days=7))
]

col1, col2, col3, col4 = st.columns([1, 1, 1, 1.4])
col1.metric("⚖️ Prazos fatais em aberto", len(prazos_abertos))
col2.metric("⏳ Vencendo em 7 dias", len(prazos_vencendo))
col3.metric("📅 Audiências cadastradas", len(df_audiencias))
col4.metric("💰 Valor total em acordos", formatar_brl(df_acordos["valor_total"].fillna(0).sum(), decimais=0))

st.divider()

col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("Próximos prazos fatais")
    tabela = prazos_com_data.sort_values("data_fatal")[
        ["processo", "partes", "finalidade", "prazo_fatal", "data_fatal"]
    ].copy()

    def cor_urgencia(row):
        dias = (row["data_fatal"] - hoje).days
        if dias < 0:
            cor = "#F6C9C7"
        elif dias <= 3:
            cor = "#F2CE6E"
        elif dias <= 7:
            cor = "#FBEBC5"
        else:
            cor = "#FFFFFF"
        return [f"background-color: {cor}; color: #1B1F2A"] * len(row)

    if not tabela.empty:
        estilo = tabela.style.apply(cor_urgencia, axis=1).hide(axis="columns", subset=["data_fatal"])
        st.dataframe(estilo, use_container_width=True, hide_index=True)
        st.caption("🟥 atrasado · 🟨 até 3 dias · 🟡 até 7 dias · ⬜ mais de 7 dias")
    else:
        st.info("Nenhum prazo fatal em aberto.")

with col_dir:
    st.subheader("Pendências por cliente (abertas)")
    pend_abertas = df_pend[df_pend["concluida"] == False]  # noqa: E712
    contagem = pend_abertas.groupby("cliente").size().reset_index(name="qtd").sort_values("qtd", ascending=True)
    if not contagem.empty:
        fig = px.bar(
            contagem,
            x="qtd",
            y="cliente",
            orientation="h",
            color="qtd",
            color_continuous_scale=["#EAD9A0", "#C9A227", "#8C6D14"],
        )
        fig.update_layout(
            plot_bgcolor="#FBF8F3",
            paper_bgcolor="#FBF8F3",
            font_color="#1B1F2A",
            font_family="Inter, sans-serif",
            xaxis_title="Pendências",
            yaxis_title=None,
            margin=dict(l=10, r=10, t=10, b=10),
            height=max(320, 28 * len(contagem)),
            showlegend=False,
            coloraxis_showscale=False,
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma pendência aberta.")

st.divider()
st.subheader("Agenda — próximas audiências e reuniões")

df_audiencias["data_dt"] = df_audiencias["data"].apply(parse_data)
df_reunioes["data_dt"] = df_reunioes["data"].apply(parse_data)

agenda = pd.concat(
    [
        df_audiencias.rename(columns={"audiencia": "evento"})[["data_dt", "horario", "partes", "evento"]].assign(
            tipo="⚖️ Audiência"
        ),
        df_reunioes.rename(columns={"assunto": "evento", "cliente": "partes"})[
            ["data_dt", "horario", "partes", "evento"]
        ].assign(tipo="🤝 Reunião"),
    ],
    ignore_index=True,
)
agenda = agenda.dropna(subset=["data_dt"]).sort_values("data_dt")
agenda["data_dt"] = agenda["data_dt"].apply(lambda d: d.strftime("%d/%m/%Y"))
agenda = agenda.rename(columns={"data_dt": "data"})[["data", "horario", "tipo", "partes", "evento"]]
st.dataframe(agenda, use_container_width=True, hide_index=True)

st.divider()
st.caption("✉️ contato@martinsemartinsadvogados.com.br  ·  📍 Rua Piauí, Quadra 134, Lote 16, Salas 03 e 04, Planaltina-DF")
