"""Shared page elements."""

from contextlib import contextmanager
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from charts import PLOTLY_CONFIG
from components.filters import Filters, filter_by_state
from src.formatting import format_date

MIN_REVIEWS = 30


def page_header(title: str, filters: Filters) -> None:
    scope = ", ".join(filters.states) or "todos os estados"
    st.html(
        f'<div class="dash-brand"><b>{escape(title)}</b>'
        f"<span>{format_date(filters.start)} a {format_date(filters.end)} · {escape(scope)}</span></div>"
    )


def stop_if_empty(is_empty: bool) -> None:
    if is_empty:
        st.info("Nenhum dado para os filtros selecionados.")
        st.stop()


@contextmanager
def card(key: str, title: str, subtitle: str = ""):
    with st.container(key=f"card_{key}"):
        sub = f'<p class="card-sub">{escape(subtitle)}</p>' if subtitle else ""
        st.html(f'<p class="card-title">{escape(title)}</p>{sub}')
        yield


def _state_clicked(chart_key: str) -> None:
    points = st.session_state[chart_key].selection.points
    if points:
        filter_by_state(points[0]["y"])


def chart(fig: go.Figure, key: str, table: pd.DataFrame | None = None) -> None:
    """Chart with an optional table twin, so no value depends on hovering."""
    if table is None:
        st.plotly_chart(fig, key=key, config=PLOTLY_CONFIG)
        return
    chart_tab, table_tab = st.tabs(["Gráfico", "Tabela"])
    with chart_tab:
        st.plotly_chart(fig, key=key, config=PLOTLY_CONFIG)
    with table_tab:
        st.dataframe(table, hide_index=True, height=300)


def clickable_state_chart(fig: go.Figure, key: str) -> None:
    st.plotly_chart(fig, key=key, config=PLOTLY_CONFIG, on_select=lambda: _state_clicked(key),
                    selection_mode="points")


def html_block(markup: str) -> None:
    st.html(markup)

