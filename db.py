import os

from dotenv import load_dotenv
from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, Text, create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

_DEFAULT_SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dash_juridico.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_DEFAULT_SQLITE_PATH}")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


class Audiencia(Base):
    __tablename__ = "audiencias"
    id = Column(Integer, primary_key=True)
    data = Column(String(20))
    horario = Column(String(20))
    partes = Column(Text)
    processo = Column(String(60))
    audiencia = Column(Text)
    responsavel = Column(String(120))


class Reuniao(Base):
    __tablename__ = "reunioes"
    id = Column(Integer, primary_key=True)
    data = Column(String(20))
    horario = Column(String(20))
    cliente = Column(Text)
    assunto = Column(Text)


class AcordoFinanceiro(Base):
    __tablename__ = "acordos_financeiros"
    id = Column(Integer, primary_key=True)
    partes = Column(Text)
    valor_total = Column(Numeric(14, 2))
    valor_parcela = Column(Numeric(14, 2))
    qtd_parcelas = Column(Integer)
    data_inicio = Column(String(20))
    data_fim = Column(String(20))
    dia_vencimento = Column(Integer)
    observacao = Column(Text)


class TarefaRecorrente(Base):
    __tablename__ = "tarefas_recorrentes"
    id = Column(Integer, primary_key=True)
    descricao = Column(Text)
    frequencia = Column(String(60))
    referencia = Column(Text)
    concluida = Column(Boolean, default=False)


class Credencial(Base):
    __tablename__ = "credenciais"
    id = Column(Integer, primary_key=True)
    sistema = Column(String(120))
    usuario = Column(String(120))
    senha = Column(String(120))
    referencia = Column(Text)


class Manifestacao(Base):
    __tablename__ = "manifestacoes"
    id = Column(Integer, primary_key=True)
    processo = Column(String(60))
    partes = Column(Text)
    finalidade = Column(Text)
    prazo_juridico = Column(String(20))
    prazo_fatal = Column(String(20))
    concluida = Column(Boolean, default=False)
    responsavel = Column(String(120))


class Acao(Base):
    __tablename__ = "acoes"
    id = Column(Integer, primary_key=True)
    partes = Column(Text)
    finalidade = Column(Text)
    responsavel = Column(String(120))


class ProcessoNaoCitado(Base):
    __tablename__ = "processos_nao_citados"
    id = Column(Integer, primary_key=True)
    tribunal = Column(String(20))
    processo = Column(String(60))
    partes = Column(Text)
    situacao = Column(Text)
    responsavel = Column(String(120))


class PendenciaCliente(Base):
    __tablename__ = "pendencias_cliente"
    id = Column(Integer, primary_key=True)
    cliente = Column(String(120))
    atividade_pendente = Column(Text)
    concluida = Column(Boolean, default=False)


class CnpjConsulta(Base):
    __tablename__ = "cnpjs_consulta"
    id = Column(Integer, primary_key=True)
    descricao = Column(Text)
    cnpj = Column(String(30))
    frequencia = Column(String(60))


class Alerta(Base):
    __tablename__ = "alertas"
    id = Column(Integer, primary_key=True)
    descricao = Column(Text)


class Anexo(Base):
    __tablename__ = "anexos"
    id = Column(Integer, primary_key=True)
    tabela_origem = Column(String(60))
    registro_id = Column(Integer)
    descricao_registro = Column(Text)
    nome_arquivo = Column(String(255))
    caminho_arquivo = Column(Text)
    data_upload = Column(DateTime)


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome = Column(String(120))
    usuario = Column(String(80), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    papel = Column(String(20), default="padrao")  # "admin" ou "padrao"
    ativo = Column(Boolean, default=True)


# Colunas adicionadas depois da criação inicial das tabelas — create_all() não
# altera tabelas já existentes, então aplicamos ALTER TABLE manualmente quando faltar.
_COLUNAS_NOVAS = {
    "audiencias": [("responsavel", "VARCHAR(120)")],
    "manifestacoes": [("responsavel", "VARCHAR(120)")],
    "processos_nao_citados": [("responsavel", "VARCHAR(120)")],
    "acoes": [("responsavel", "VARCHAR(120)")],
}


def _migrar_colunas_novas():
    inspector = inspect(engine)
    tabelas_existentes = set(inspector.get_table_names())
    with engine.begin() as conn:
        for tabela, colunas in _COLUNAS_NOVAS.items():
            if tabela not in tabelas_existentes:
                continue
            existentes = {c["name"] for c in inspector.get_columns(tabela)}
            for nome_coluna, tipo_sql in colunas:
                if nome_coluna not in existentes:
                    conn.execute(text(f"ALTER TABLE {tabela} ADD COLUMN {nome_coluna} {tipo_sql}"))


def init_db():
    Base.metadata.create_all(engine)
    _migrar_colunas_novas()


def get_session():
    return SessionLocal()
