import bcrypt
import streamlit as st

from db import Usuario, get_session


def hash_senha(senha):
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha, senha_hash):
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
    except ValueError:
        return False


def criar_usuario(session, nome, usuario, senha, papel="padrao"):
    novo = Usuario(nome=nome, usuario=usuario.strip().lower(), senha_hash=hash_senha(senha), papel=papel, ativo=True)
    session.add(novo)
    session.commit()
    return novo


def autenticar(session, usuario, senha):
    registro = session.query(Usuario).filter(Usuario.usuario == usuario.strip().lower(), Usuario.ativo == True).first()  # noqa: E712
    if registro and verificar_senha(senha, registro.senha_hash):
        return registro
    return None


def usuario_logado():
    return st.session_state.get("usuario_logado")


def eh_admin():
    usuario = usuario_logado()
    return bool(usuario) and usuario.get("papel") == "admin"


def logout():
    st.session_state.pop("usuario_logado", None)
    st.rerun()


def trocar_propria_senha(session, usuario_id, senha_atual, nova_senha):
    registro = session.get(Usuario, usuario_id)
    if not registro or not verificar_senha(senha_atual, registro.senha_hash):
        return False, "Senha atual incorreta."
    if len(nova_senha) < 6:
        return False, "Use uma senha nova com pelo menos 6 caracteres."
    registro.senha_hash = hash_senha(nova_senha)
    session.commit()
    return True, "Senha alterada com sucesso."


@st.dialog("🔑 Trocar senha")
def _dialog_trocar_senha():
    usuario = usuario_logado()
    with st.form("trocar_senha"):
        senha_atual = st.text_input("Senha atual", type="password")
        nova_senha = st.text_input("Nova senha", type="password")
        confirmar = st.text_input("Confirmar nova senha", type="password")
        enviado = st.form_submit_button("Salvar nova senha")

    if enviado:
        if nova_senha != confirmar:
            st.error("As senhas não coincidem.")
        else:
            session = get_session()
            ok, mensagem = trocar_propria_senha(session, usuario["id"], senha_atual, nova_senha)
            session.close()
            if ok:
                st.success(mensagem)
            else:
                st.error(mensagem)


def caixa_trocar_senha():
    if st.button("🔑 Trocar senha", use_container_width=True):
        _dialog_trocar_senha()


def _tela_bootstrap(session):
    st.title("⚖️ Painel Jurídico")
    st.subheader("Primeiro acesso — crie a conta de administrador")
    st.caption("Nenhum usuário cadastrado ainda. A primeira conta criada terá acesso total ao sistema.")

    with st.form("bootstrap_admin"):
        nome = st.text_input("Nome")
        usuario = st.text_input("Usuário (login)")
        senha = st.text_input("Senha", type="password")
        confirmar = st.text_input("Confirmar senha", type="password")
        enviado = st.form_submit_button("Criar conta de administrador")

    if enviado:
        if not nome or not usuario or not senha:
            st.error("Preencha todos os campos.")
        elif senha != confirmar:
            st.error("As senhas não coincidem.")
        elif len(senha) < 6:
            st.error("Use uma senha com pelo menos 6 caracteres.")
        else:
            criar_usuario(session, nome, usuario, senha, papel="admin")
            st.success("Conta criada! Faça login abaixo.")
            st.rerun()


def _tela_login(session):
    st.title("⚖️ Painel Jurídico")
    st.subheader("Entrar")

    with st.form("login"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        enviado = st.form_submit_button("Entrar")

    if enviado:
        registro = autenticar(session, usuario, senha)
        if registro:
            st.session_state["usuario_logado"] = {
                "id": registro.id,
                "nome": registro.nome,
                "usuario": registro.usuario,
                "papel": registro.papel,
            }
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")


def exigir_login():
    """Bloqueia o restante do app até haver um usuário autenticado na sessão."""
    if usuario_logado():
        return

    session = get_session()
    tem_usuarios = session.query(Usuario).count() > 0
    if tem_usuarios:
        _tela_login(session)
    else:
        _tela_bootstrap(session)
    session.close()
    st.stop()
