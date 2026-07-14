import streamlit as st


def apply_style():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        h1, h2, h3 {
            font-family: 'Playfair Display', serif;
            color: #1B1F2A;
            letter-spacing: 0.3px;
        }

        /* Marca d'água sutil no conteúdo principal, ecoando o papel timbrado */
        [data-testid="stAppViewContainer"] > .main {
            background-color: #FBF8F3;
            background-image: radial-gradient(circle at 88% 4%, rgba(201, 162, 39, 0.10) 0%, rgba(201, 162, 39, 0) 45%);
        }

        .stApp {
            background-color: #FBF8F3;
        }

        h1:first-of-type::after {
            content: "";
            display: block;
            width: 64px;
            height: 3px;
            background: #C9A227;
            margin-top: 6px;
            border-radius: 2px;
        }

        /* Cabeçalhos de seção com friso dourado à esquerda */
        h2, h3 {
            border-left: 3px solid #C9A227;
            padding-left: 10px !important;
            margin-top: 1.6rem !important;
        }

        /* --- Sidebar --- */
        section[data-testid="stSidebar"] {
            background-color: #1B1F2A;
            background-image: linear-gradient(180deg, #1B1F2A 0%, #20263A 100%);
        }
        section[data-testid="stSidebar"] * {
            color: #F5EFE0 !important;
        }
        section[data-testid="stSidebar"] img {
            padding: 18px 4px 10px 4px;
        }
        section[data-testid="stSidebar"] hr {
            border-top: 1px solid rgba(201, 162, 39, 0.35);
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
            border-radius: 6px;
            margin: 2px 6px;
            transition: background-color 0.15s ease;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
            background-color: rgba(201, 162, 39, 0.18);
        }
        section[data-testid="stSidebar"] [aria-current="page"] {
            background-color: rgba(201, 162, 39, 0.28) !important;
            border-radius: 6px;
        }

        /* --- Cards de métrica --- */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E6DEC7;
            border-top: 4px solid #C9A227;
            border-radius: 10px;
            padding: 14px 16px;
            box-shadow: 0 2px 6px rgba(27, 31, 42, 0.06);
            transition: box-shadow 0.15s ease, transform 0.15s ease;
        }
        div[data-testid="stMetric"]:hover {
            box-shadow: 0 6px 14px rgba(27, 31, 42, 0.10);
            transform: translateY(-1px);
        }

        div[data-testid="stMetricLabel"] {
            color: #6B6252;
            text-transform: uppercase;
            font-size: 0.72rem !important;
            letter-spacing: 0.6px;
            font-weight: 600;
        }

        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: clip !important;
            max-width: none !important;
            word-break: break-word !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.4rem !important;
            line-height: 1.3 !important;
            color: #1B1F2A;
        }

        /* --- Botões --- */
        .stButton>button {
            background-color: #1B1F2A;
            color: #F5EFE0;
            border-radius: 5px;
            border: 1px solid #C9A227;
            transition: background-color 0.15s ease, color 0.15s ease;
        }
        .stButton>button:hover {
            background-color: #C9A227;
            color: #1B1F2A;
            border: 1px solid #1B1F2A;
        }

        /* --- Tabelas / editores --- */
        [data-testid="stDataFrame"], [data-testid="stElementContainer"] [data-testid="stTable"] {
            border: 1px solid #E6DEC7;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 6px rgba(27, 31, 42, 0.05);
        }

        [data-testid="stTabs"] button[role="tab"] {
            font-weight: 600;
            color: #6B6252;
        }
        [data-testid="stTabs"] button[aria-selected="true"] {
            color: #1B1F2A;
            border-bottom-color: #C9A227 !important;
        }

        div[data-testid="stAlertContainer"] {
            border-radius: 8px;
        }

        hr {
            border-top: 1px solid #E6DEC7;
        }

        [data-testid="stCaptionContainer"] {
            color: #8A8072;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
