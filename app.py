import os

import streamlit as st

from auth import eh_admin, logout, usuario_logado
from db import get_session, init_db
from style import apply_style
from utils import contar_prazos_vencendo

st.set_page_config(page_title="Painel Jurídico | Kamilla Martins", page_icon="⚖️", layout="wide")
apply_style()
init_db()

_LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.svg")
st.logo(_LOGO_PATH, size="large")

_usuario = usuario_logado()

if not _usuario:
    # Antes do login, a barra lateral mostra só a página inicial (que exibe a
    # tela de login/criação de admin) — nenhuma outra página é anunciada.
    st.navigation([st.Page("home_content.py", title="Painel", icon="⚖️", default=True)]).run()
    st.stop()

with st.sidebar:
    st.markdown(f"**{_usuario['nome']}**")
    st.caption("Administrador" if eh_admin() else "Usuário padrão")
    if st.button("Sair", use_container_width=True):
        logout()
    st.divider()

_session = get_session()
_qtd_vencendo = contar_prazos_vencendo(_session, dias=7)
_session.close()

_titulo_prazos = "Prazos e Manifestações"
if _qtd_vencendo > 0:
    _titulo_prazos = f"Prazos e Manifestações 🔴{_qtd_vencendo}"

paginas = [
    st.Page("home_content.py", title="Painel", icon="⚖️", default=True),
    st.Page("pages/1_Agenda.py", title="Agenda", icon="📅"),
    st.Page("pages/2_Acordos_Financeiros.py", title="Acordos Financeiros", icon="💰"),
    st.Page("pages/3_Prazos_e_Manifestacoes.py", title=_titulo_prazos, icon="⏳"),
    st.Page("pages/4_Processos.py", title="Processos", icon="📁"),
    st.Page("pages/5_Pendencias_por_Cliente.py", title="Pendências por Cliente", icon="✅"),
    st.Page("pages/7_Busca_Global.py", title="Busca Global", icon="🔎"),
    st.Page("pages/8_Visao_360.py", title="Visão 360º por Cliente", icon="🧭"),
    st.Page("pages/9_Calendario.py", title="Calendário", icon="🗓️"),
    st.Page("pages/10_Anexos.py", title="Anexos", icon="📎"),
    st.Page("pages/6_Outros.py", title="Outros", icon="🗂️"),
]

if eh_admin():
    paginas.append(st.Page("pages/11_Usuarios.py", title="Usuários", icon="👤"))

st.navigation(paginas).run()
