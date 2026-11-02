"""Dashboard router: run with `python -m streamlit run app/Home.py` from the root."""

import streamlit as st
from psycopg2.errors import UndefinedTable
from sqlalchemy.exc import OperationalError, ProgrammingError

from components.filters import render_filters
from src.db import MissingConfigError
from theme import apply_theme

st.set_page_config(page_title="ShopAgent Dashboard", layout="wide")
apply_theme()

page = st.navigation(
    [
        st.Page("pages/visao_geral.py", title="Visão geral", default=True),
        st.Page("pages/vendas.py", title="Vendas"),
        st.Page("pages/produtos.py", title="Produtos"),
        st.Page("pages/clientes.py", title="Clientes"),
        st.Page("pages/avaliacoes.py", title="Avaliações"),
    ],
    position="top",
)

try:
    render_filters()
    page.run()
except OperationalError:
    st.error("Não foi possível conectar ao banco. Verifique se o Postgres está rodando "
             "e as credenciais do `.env`.")
except ProgrammingError as exc:
    if not isinstance(exc.orig, UndefinedTable):
        raise
    st.error("As tabelas do dashboard não existem. Rode `python -m src.prepare_data`.")
except MissingConfigError as exc:
    st.error(str(exc))
