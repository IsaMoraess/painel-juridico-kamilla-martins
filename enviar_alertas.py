"""Envia um e-mail com os prazos fatais que vencem nos próximos N dias.

Uso manual:
    python enviar_alertas.py            # usa o padrão de 3 dias
    python enviar_alertas.py 5          # avisa sobre prazos que vencem em até 5 dias

Configuração (arquivo .env, veja .env.example):
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_USE_TLS
    EMAIL_REMETENTE, EMAIL_DESTINATARIOS (separados por vírgula)

Para automatizar o envio diário, agende este script no Agendador de Tarefas do
Windows (Task Scheduler) — peça ajuda se quiser configurar isso.
"""

import os
import smtplib
import sys
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from dotenv import load_dotenv

from db import Manifestacao, get_session
from utils import parse_prazo_fatal

load_dotenv()


def montar_html(prazos_df, dias):
    if prazos_df.empty:
        return None

    linhas = "".join(
        f"<tr>"
        f"<td style='padding:6px 10px;border:1px solid #E6DEC7;'>{row['prazo_fatal']}</td>"
        f"<td style='padding:6px 10px;border:1px solid #E6DEC7;'>{row['processo'] or ''}</td>"
        f"<td style='padding:6px 10px;border:1px solid #E6DEC7;'>{row['partes'] or ''}</td>"
        f"<td style='padding:6px 10px;border:1px solid #E6DEC7;'>{row['finalidade'] or ''}</td>"
        f"<td style='padding:6px 10px;border:1px solid #E6DEC7;'>{row['responsavel'] or '—'}</td>"
        f"</tr>"
        for _, row in prazos_df.iterrows()
    )

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #1B1F2A;">
        <h2 style="color:#1B1F2A;">⚖️ Prazos fatais vencendo em até {dias} dia(s)</h2>
        <table style="border-collapse: collapse; width: 100%;">
            <tr style="background-color:#F1E9D8;">
                <th style="padding:6px 10px;border:1px solid #E6DEC7;text-align:left;">Prazo</th>
                <th style="padding:6px 10px;border:1px solid #E6DEC7;text-align:left;">Processo</th>
                <th style="padding:6px 10px;border:1px solid #E6DEC7;text-align:left;">Partes</th>
                <th style="padding:6px 10px;border:1px solid #E6DEC7;text-align:left;">Finalidade</th>
                <th style="padding:6px 10px;border:1px solid #E6DEC7;text-align:left;">Responsável</th>
            </tr>
            {linhas}
        </table>
        <p style="color:#6B6252; font-size: 0.85rem;">Painel Jurídico — Kamilla Martins Advocacia</p>
    </body>
    </html>
    """


def prazos_vencendo(dias):
    session = get_session()
    hoje = date.today()
    df = pd.read_sql(session.query(Manifestacao).statement, session.bind)
    session.close()

    if df.empty:
        return df

    df = df[df["concluida"] == False]  # noqa: E712
    df["data_fatal"] = df["prazo_fatal"].apply(lambda v: parse_prazo_fatal(v, hoje))
    df = df.dropna(subset=["data_fatal"])
    from datetime import timedelta

    return df[(df["data_fatal"] >= hoje) & (df["data_fatal"] <= hoje + timedelta(days=dias))].sort_values(
        "data_fatal"
    )


def enviar_alertas(dias=3):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    usar_tls = os.getenv("SMTP_USE_TLS", "true").lower() != "false"
    remetente = os.getenv("EMAIL_REMETENTE", smtp_user)
    destinatarios = [d.strip() for d in os.getenv("EMAIL_DESTINATARIOS", "").split(",") if d.strip()]

    if not smtp_host or not smtp_user or not smtp_password or not destinatarios:
        return False, (
            "Configuração de e-mail incompleta. Preencha SMTP_HOST, SMTP_USER, SMTP_PASSWORD "
            "e EMAIL_DESTINATARIOS no arquivo .env (veja .env.example)."
        )

    df = prazos_vencendo(dias)
    if df.empty:
        return True, f"Nenhum prazo fatal vencendo nos próximos {dias} dia(s) — nenhum e-mail enviado."

    corpo_html = montar_html(df, dias)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"⚖️ {len(df)} prazo(s) fatal(is) vencendo em até {dias} dia(s)"
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)
    msg.attach(MIMEText(corpo_html, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as servidor:
            if usar_tls:
                servidor.starttls()
            servidor.login(smtp_user, smtp_password)
            servidor.sendmail(remetente, destinatarios, msg.as_string())
    except Exception as exc:  # noqa: BLE001
        return False, f"Falha ao enviar e-mail: {exc}"

    return True, f"E-mail enviado para {', '.join(destinatarios)} com {len(df)} prazo(s)."


if __name__ == "__main__":
    dias_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    ok, mensagem = enviar_alertas(dias_arg)
    print(mensagem)
    sys.exit(0 if ok else 1)
