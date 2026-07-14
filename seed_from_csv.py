import os

import pandas as pd

from db import (
    Acao,
    AcordoFinanceiro,
    Audiencia,
    Alerta,
    CnpjConsulta,
    Credencial,
    Manifestacao,
    PendenciaCliente,
    ProcessoNaoCitado,
    Reuniao,
    TarefaRecorrente,
    get_session,
    init_db,
)

CSV_DIR = os.path.join(os.path.dirname(__file__), "..", "csv")


def carregar(nome):
    caminho = os.path.join(CSV_DIR, nome)
    return pd.read_csv(caminho, dtype=str, keep_default_na=False)


def to_float(v):
    if v in (None, "", "nan"):
        return None
    return float(v)


def to_int(v):
    if v in (None, "", "nan"):
        return None
    return int(float(v))


def seed():
    init_db()
    session = get_session()

    if session.query(Audiencia).count() > 0:
        print("Banco já populado — abortando seed para não duplicar dados.")
        session.close()
        return

    df = carregar("audiencias.csv")
    for _, r in df.iterrows():
        session.add(
            Audiencia(data=r["data"], horario=r["horario"], partes=r["partes"], processo=r["processo"], audiencia=r["audiencia"])
        )

    df = carregar("reunioes.csv")
    for _, r in df.iterrows():
        session.add(Reuniao(data=r["data"], horario=r["horario"], cliente=r["cliente"], assunto=r["assunto"]))

    df = carregar("acordos_financeiros.csv")
    for _, r in df.iterrows():
        session.add(
            AcordoFinanceiro(
                partes=r["partes"],
                valor_total=to_float(r["valor_total"]),
                valor_parcela=to_float(r["valor_parcela"]),
                qtd_parcelas=to_int(r["qtd_parcelas"]),
                data_inicio=r["data_inicio"],
                data_fim=r["data_fim"],
                dia_vencimento=to_int(r["dia_vencimento"]),
                observacao=r["observacao"],
            )
        )

    df = carregar("tarefas_recorrentes.csv")
    for _, r in df.iterrows():
        session.add(TarefaRecorrente(descricao=r["descricao"], frequencia=r["frequencia"], referencia=r["referencia"]))

    df = carregar("credenciais.csv")
    for _, r in df.iterrows():
        session.add(Credencial(sistema=r["sistema"], usuario=r["usuario"], senha=r["senha"], referencia=r["referencia"]))

    df = carregar("manifestacoes.csv")
    for _, r in df.iterrows():
        session.add(
            Manifestacao(
                processo=r["processo"],
                partes=r["partes"],
                finalidade=r["finalidade"],
                prazo_juridico=r["prazo_juridico"],
                prazo_fatal=r["prazo_fatal"],
            )
        )

    df = carregar("acoes.csv")
    for _, r in df.iterrows():
        session.add(Acao(partes=r["partes"], finalidade=r["finalidade"]))

    df = carregar("processos_nao_citados.csv")
    for _, r in df.iterrows():
        session.add(
            ProcessoNaoCitado(tribunal=r["tribunal"], processo=r["processo"], partes=r["partes"], situacao=r["situacao"])
        )

    df = carregar("pendencias_cliente.csv")
    for _, r in df.iterrows():
        if r["atividade_pendente"].strip().lower() == "nada":
            continue
        session.add(PendenciaCliente(cliente=r["cliente"], atividade_pendente=r["atividade_pendente"]))

    df = carregar("cnpjs_consulta.csv")
    for _, r in df.iterrows():
        session.add(CnpjConsulta(descricao=r["descricao"], cnpj=r["cnpj"], frequencia=r["frequencia"]))

    df = carregar("alertas.csv")
    for _, r in df.iterrows():
        session.add(Alerta(descricao=r["descricao"]))

    session.commit()
    session.close()
    print("Seed concluído.")


if __name__ == "__main__":
    seed()
