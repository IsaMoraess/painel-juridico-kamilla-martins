import streamlit as st

from auth import criar_usuario, eh_admin, exigir_login, hash_senha, usuario_logado
from db import Usuario, get_session

exigir_login()

if not eh_admin():
    st.error("Apenas administradores podem acessar esta página.")
    st.stop()

session = get_session()
eu = usuario_logado()

st.title("👤 Usuários")
st.caption("Gerencie quem tem acesso ao sistema e o nível de acesso de cada pessoa.")

tab_lista, tab_novo = st.tabs(["Usuários cadastrados", "Adicionar usuário"])

with tab_novo:
    with st.form("novo_usuario", clear_on_submit=True):
        nome = st.text_input("Nome")
        usuario = st.text_input("Usuário (login)")
        papel = st.selectbox("Papel", ["padrao", "admin"], format_func=lambda p: "Administrador" if p == "admin" else "Padrão")
        senha = st.text_input("Senha", type="password")
        confirmar = st.text_input("Confirmar senha", type="password")
        enviado = st.form_submit_button("Criar usuário")

    if enviado:
        existente = session.query(Usuario).filter(Usuario.usuario == usuario.strip().lower()).first()
        if not nome or not usuario or not senha:
            st.error("Preencha todos os campos.")
        elif existente:
            st.error("Já existe um usuário com esse login.")
        elif senha != confirmar:
            st.error("As senhas não coincidem.")
        elif len(senha) < 6:
            st.error("Use uma senha com pelo menos 6 caracteres.")
        else:
            criar_usuario(session, nome, usuario, senha, papel=papel)
            st.success(f"Usuário '{usuario}' criado.")
            st.rerun()

with tab_lista:
    usuarios = session.query(Usuario).order_by(Usuario.nome).all()
    for u in usuarios:
        with st.container(border=True):
            col_info, col_papel, col_acoes = st.columns([3, 2, 2])
            with col_info:
                st.markdown(f"**{u.nome}**")
                st.caption(f"login: {u.usuario}" + ("" if u.ativo else " — inativo"))
            with col_papel:
                novo_papel = st.selectbox(
                    "Papel",
                    ["padrao", "admin"],
                    index=0 if u.papel != "admin" else 1,
                    format_func=lambda p: "Administrador" if p == "admin" else "Padrão",
                    key=f"papel_{u.id}",
                    label_visibility="collapsed",
                    disabled=(u.id == eu["id"]),
                )
                if novo_papel != u.papel:
                    u.papel = novo_papel
                    session.commit()
                    st.rerun()
            with col_acoes:
                nova_senha = st.text_input("Nova senha", key=f"senha_{u.id}", placeholder="Redefinir senha", label_visibility="collapsed")
                if nova_senha:
                    if len(nova_senha) < 6:
                        st.caption("⚠️ mínimo 6 caracteres")
                    elif st.button("Salvar nova senha", key=f"salvar_senha_{u.id}"):
                        u.senha_hash = hash_senha(nova_senha)
                        session.commit()
                        st.success("Senha atualizada.")

                if u.id != eu["id"]:
                    rotulo = "Reativar" if not u.ativo else "Desativar"
                    if st.button(rotulo, key=f"toggle_{u.id}"):
                        u.ativo = not u.ativo
                        session.commit()
                        st.rerun()
                else:
                    st.caption("Você")

session.close()
