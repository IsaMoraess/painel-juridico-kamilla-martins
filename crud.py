import pandas as pd
import streamlit as st


def carregar_df(session, model):
    return pd.read_sql(session.query(model).statement, session.bind)


def salvar_alteracoes(session, model, original, editado):
    orig_ids = set(original["id"].dropna().astype(int)) if "id" in original.columns else set()
    edit_ids = set(editado["id"].dropna().astype(int)) if "id" in editado.columns else set()

    for rid in orig_ids - edit_ids:
        obj = session.get(model, int(rid))
        if obj:
            session.delete(obj)

    for _, row in editado.iterrows():
        data = row.to_dict()
        rid = data.pop("id", None)
        data = {k: (None if pd.isna(v) else v) for k, v in data.items()}

        if rid is None or (isinstance(rid, float) and pd.isna(rid)):
            session.add(model(**data))
        else:
            obj = session.get(model, int(rid))
            if obj:
                for k, v in data.items():
                    setattr(obj, k, v)

    session.commit()


def editor_tabela(session, model, titulo, column_config=None):
    st.subheader(titulo)
    df = carregar_df(session, model)
    editado = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        disabled=("id",),
        column_config=column_config,
        key=f"editor_{model.__tablename__}",
    )
    if st.button(f"Salvar alterações — {titulo}", key=f"salvar_{model.__tablename__}"):
        salvar_alteracoes(session, model, df, editado)
        st.success("Alterações salvas.")
        st.rerun()
