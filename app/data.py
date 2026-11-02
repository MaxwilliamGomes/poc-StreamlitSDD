"""Cached data layer: the only app module that calls `src.queries`."""

from datetime import date

import pandas as pd
import streamlit as st
from sqlalchemy import Engine

from src import db, queries

KPI_TTL = "5m"
OPTIONS_TTL = "1h"
MAX_ENTRIES = 256
SPINNER = "Consultando o banco..."


@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    return db.create_db_engine()


@st.cache_data(ttl=OPTIONS_TTL, show_spinner=False)
def load_filter_options() -> dict[str, object]:
    return queries.filter_options(get_engine())


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=False)
def load_overview(start: date, end: date, states: tuple[str, ...]) -> dict[str, float | int | None]:
    return queries.overview_kpis(get_engine(), start, end, states)


def load_overview_comparison(
    start: date, end: date, states: tuple[str, ...]
) -> tuple[dict[str, float | int | None], dict[str, float | int | None], dict[str, float | None]]:
    """Current KPIs, previous KPIs and the change between them."""
    current = load_overview(start, end, states)
    previous = load_overview(*queries.previous_period(start, end), states)
    growth = {
        key: queries.safe_growth(current[key], previous[key])
        for key in ("faturamento", "pedidos", "ticket_medio", "taxa_cancelamento")
    }
    return current, previous, growth


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_revenue_over_time(
    start: date, end: date, states: tuple[str, ...], grain: str = "month"
) -> pd.DataFrame:
    frame = queries.revenue_over_time(get_engine(), start, end, states, grain)
    return queries.fill_time_gaps(frame, grain)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_revenue_by_state(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.revenue_by_state(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_orders_by_status(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.orders_by_status(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_orders_by_payment(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.orders_by_payment(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_top_products(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.top_products(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_category_summary(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.category_summary(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_customers_by_segment(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.customers_by_segment(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_customers_by_state(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.customers_by_state(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_review_summary(start: date, end: date, states: tuple[str, ...]) -> dict[str, float | int | None]:
    return queries.review_summary(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_sentiment(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.sentiment_distribution(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_rating_by_category(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.rating_by_category(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_negative_comments(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.negative_comments(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_kpi_series(start: date, end: date, states: tuple[str, ...], grain: str) -> pd.DataFrame:
    return queries.fill_time_gaps(queries.kpi_series(get_engine(), start, end, states, grain), grain)


def load_previous_series(start: date, end: date, states: tuple[str, ...], grain: str) -> pd.DataFrame:
    return load_kpi_series(*queries.previous_period(start, end), states, grain)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_orders_heatmap(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.orders_heatmap(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_state_scorecard(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.state_scorecard(get_engine(), start, end, states)


def load_previous_scorecard(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return load_state_scorecard(*queries.previous_period(start, end), states)


def load_previous_revenue_by_state(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return load_revenue_by_state(*queries.previous_period(start, end), states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_product_performance(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.product_performance(get_engine(), start, end, states)


def load_previous_products(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return load_product_performance(*queries.previous_period(start, end), states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_category_matrix(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.category_state_matrix(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_payment_over_time(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.payment_over_time(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_order_frequency(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.order_frequency(get_engine(), start, end, states)


def load_previous_segments(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return load_customers_by_segment(*queries.previous_period(start, end), states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_rating_distribution(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.rating_distribution(get_engine(), start, end, states)


@st.cache_data(ttl=KPI_TTL, max_entries=MAX_ENTRIES, show_spinner=SPINNER)
def load_sentiment_by_category(start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    return queries.sentiment_by_category(get_engine(), start, end, states)
