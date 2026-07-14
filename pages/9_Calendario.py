import re
from datetime import date

import pandas as pd
import streamlit as st
from streamlit_calendar import calendar

from auth import exigir_login
from db import Audiencia, Manifestacao, Reuniao, get_session
from utils import parse_data, parse_prazo_fatal

exigir_login()
session = get_session()

st.title("🗓️ Calendário")
st.caption("Audiências, reuniões e prazos fatais em um só calendário. Clique em um evento para ver os detalhes.")


def _hora_para_iso(horario):
    if not horario:
        return None
    m = re.match(r"(\d{1,2})h(\d{2})?", str(horario).strip())
    if not m:
        return None
    hora = int(m.group(1))
    minuto = int(m.group(2) or 0)
    return f"{hora:02d}:{minuto:02d}:00"


eventos = []

df_audiencias = pd.read_sql(session.query(Audiencia).statement, session.bind)
for _, row in df_audiencias.iterrows():
    dt = parse_data(row["data"])
    if not dt:
        continue
    hora_iso = _hora_para_iso(row["horario"])
    inicio = f"{dt.isoformat()}T{hora_iso}" if hora_iso else dt.isoformat()
    eventos.append(
        {
            "title": f"⚖️ {row['partes'] or ''}",
            "start": inicio,
            "allDay": hora_iso is None,
            "color": "#C9A227",
        }
    )

df_reunioes = pd.read_sql(session.query(Reuniao).statement, session.bind)
for _, row in df_reunioes.iterrows():
    dt = parse_data(row["data"])
    if not dt:
        continue
    hora_iso = _hora_para_iso(row["horario"])
    inicio = f"{dt.isoformat()}T{hora_iso}" if hora_iso else dt.isoformat()
    eventos.append(
        {
            "title": f"🤝 {row['cliente'] or ''}",
            "start": inicio,
            "allDay": hora_iso is None,
            "color": "#6B7A99",
        }
    )

hoje = date.today()
df_manif = pd.read_sql(session.query(Manifestacao).statement, session.bind)
df_manif = df_manif[df_manif["concluida"] == False]  # noqa: E712
for _, row in df_manif.iterrows():
    dt = parse_prazo_fatal(row["prazo_fatal"], hoje)
    if not dt:
        continue
    eventos.append(
        {
            "title": f"⏳ {row['partes'] or row['processo'] or row['finalidade']}",
            "start": dt.isoformat(),
            "allDay": True,
            "color": "#C0392B" if dt < hoje else "#E0A72E",
        }
    )

session.close()

st.markdown(
    "🟡 audiência · 🔵 reunião · 🟠 prazo fatal (próximo) · 🔴 prazo fatal (atrasado)"
)

opcoes = {
    "initialView": "dayGridMonth",
    "locale": "pt-br",
    "firstDay": 0,
    "height": 720,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,dayGridWeek,listMonth",
    },
}

calendar(events=eventos, options=opcoes, key="calendario_juridico")
