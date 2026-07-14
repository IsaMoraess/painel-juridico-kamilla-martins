from datetime import date, datetime, timedelta

import pandas as pd

from db import (
    Acao,
    AcordoFinanceiro,
    Anexo,
    Audiencia,
    Manifestacao,
    PendenciaCliente,
    ProcessoNaoCitado,
    Reuniao,
)


def parse_data(valor):
    try:
        return datetime.strptime(str(valor).strip(), "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None


def parse_prazo_fatal(valor, hoje=None):
    """Aceita 'dd/mm/aaaa' (data completa) ou 'dd/mm' (como no PDF original,
    sem ano — assume o ano corrente, ou o próximo se já tiver passado há mais
    de 6 meses)."""
    hoje = hoje or date.today()
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


def contar_prazos_vencendo(session, dias=7):
    """Quantos prazos fatais (não concluídos) vencem entre hoje e N dias a partir de hoje."""
    hoje = date.today()
    df = pd.read_sql(session.query(Manifestacao).statement, session.bind)
    if df.empty:
        return 0
    df = df[df["concluida"] == False]  # noqa: E712
    df["data_fatal"] = df["prazo_fatal"].apply(lambda v: parse_prazo_fatal(v, hoje))
    df = df.dropna(subset=["data_fatal"])
    vencendo = df[(df["data_fatal"] >= hoje) & (df["data_fatal"] <= hoje + timedelta(days=dias))]
    return len(vencendo)


# Tabelas e colunas de texto onde um termo de busca pode aparecer.
TABELAS_BUSCAVEIS = [
    ("Audiências", Audiencia, ["partes", "processo", "audiencia"]),
    ("Reuniões", Reuniao, ["cliente", "assunto"]),
    ("Acordos Financeiros", AcordoFinanceiro, ["partes", "observacao"]),
    ("Prazos e Manifestações", Manifestacao, ["partes", "processo", "finalidade"]),
    ("Ações", Acao, ["partes", "finalidade"]),
    ("Processos não citados", ProcessoNaoCitado, ["partes", "processo", "situacao"]),
    ("Pendências por Cliente", PendenciaCliente, ["cliente", "atividade_pendente"]),
]


def buscar(session, termo):
    """Procura `termo` (case-insensitive, substring) nas colunas de texto de
    todas as tabelas relevantes. Retorna lista de (nome_tabela, dataframe_filtrado)."""
    termo = (termo or "").strip().lower()
    if not termo:
        return []

    resultados = []
    for nome, modelo, colunas in TABELAS_BUSCAVEIS:
        df = pd.read_sql(session.query(modelo).statement, session.bind)
        if df.empty:
            continue
        mascara = False
        for coluna in colunas:
            mascara = mascara | df[coluna].fillna("").astype(str).str.lower().str.contains(termo, regex=False)
        encontrados = df[mascara]
        if not encontrados.empty:
            resultados.append((nome, modelo, encontrados))
    return resultados


def clientes_conhecidos(session):
    """Lista de nomes de cliente conhecidos, a partir da tabela mais limpa (Pendências por Cliente)."""
    df = pd.read_sql(session.query(PendenciaCliente.cliente).distinct().statement, session.bind)
    return sorted(df["cliente"].dropna().unique().tolist())


def rotulo_registro(row, colunas):
    """Monta um rótulo legível para um registro a partir das colunas de texto mais relevantes."""
    partes = [str(row[c]) for c in colunas if row.get(c) not in (None, "")]
    texto = " — ".join(partes)
    return texto[:120] if texto else f"registro #{row.get('id')}"


def anexos_de(session, tabela, registro_id):
    return (
        session.query(Anexo)
        .filter(Anexo.tabela_origem == tabela, Anexo.registro_id == registro_id)
        .order_by(Anexo.data_upload.desc())
        .all()
    )
