"""Dashboard read queries. Revenue always excludes cancelled orders."""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
from sqlalchemy import Engine, text

from src.metrics import growth

TIMEZONE = "America/Sao_Paulo"
GRAINS = ("day", "week", "month")
_GRAIN_FREQUENCIES = {"day": "D", "week": "W-MON", "month": "MS"}

_FILTERS = """
    o.created_at >= :start_at AND o.created_at < :end_at
    AND (CAST(:states AS text[]) IS NULL OR c.state = ANY(CAST(:states AS text[])))
"""
_ORDERS = """
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
"""
_ORDERS_PRODUCTS = _ORDERS + "JOIN products p ON p.product_id = o.product_id\n"
_REVIEWS = """
    FROM reviews r
    JOIN orders o ON o.order_id = r.order_id
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN products p ON p.product_id = o.product_id
"""
_REVENUE = "COALESCE(SUM(o.total) FILTER (WHERE o.status <> 'cancelled'), 0)"
_ORDER_COUNT = "COUNT(*) FILTER (WHERE o.status <> 'cancelled')"
_CANCELLED = "COUNT(*) FILTER (WHERE o.status = 'cancelled')"
_TICKET = f"{_REVENUE} / NULLIF({_ORDER_COUNT}, 0)"
_CANCEL_RATE = f"{_CANCELLED}::numeric / NULLIF(COUNT(*), 0)"


def _params(start: date, end: date, states: tuple[str, ...]) -> dict[str, object]:
    """Inclusive local dates become half-open timestamp bounds."""
    zone = ZoneInfo(TIMEZONE)
    return {
        "start_at": datetime.combine(start, time.min, tzinfo=zone),
        "end_at": datetime.combine(end + timedelta(days=1), time.min, tzinfo=zone),
        "states": list(states) or None,
    }


def _read(engine: Engine, sql: str, params: dict[str, object], numeric: tuple[str, ...]) -> pd.DataFrame:
    frame = pd.read_sql(text(sql), engine, params=params)
    return frame.astype({column: "float64" for column in numeric})


def previous_period(start: date, end: date) -> tuple[date, date]:
    """Interval of the same length that ends right before `start`."""
    days = (end - start).days + 1
    return start - timedelta(days=days), start - timedelta(days=1)


safe_growth = growth


def fill_time_gaps(frame: pd.DataFrame, grain: str) -> pd.DataFrame:
    """Add missing periods with zero, so a chart does not bridge them."""
    if frame.empty:
        return frame
    index = pd.date_range(frame["periodo"].min(), frame["periodo"].max(), freq=_GRAIN_FREQUENCIES[grain])
    return (
        frame.set_index("periodo")
        .reindex(index, fill_value=0)
        .rename_axis("periodo")
        .reset_index()
    )


def filter_options(engine: Engine) -> dict[str, object]:
    sql = f"""
        SELECT (SELECT array_agg(DISTINCT state::text ORDER BY state::text) FROM customers) AS states,
               MIN((created_at AT TIME ZONE '{TIMEZONE}')::date) AS min_date,
               MAX((created_at AT TIME ZONE '{TIMEZONE}')::date) AS max_date
        FROM orders
    """
    row = pd.read_sql(text(sql), engine).iloc[0]
    return {
        "states": list(row["states"] or []),
        "min_date": row["min_date"],
        "max_date": row["max_date"],
    }


def overview_kpis(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> dict[str, float | int | None]:
    sql = f"""
        SELECT {_REVENUE} AS faturamento,
               {_ORDER_COUNT} AS pedidos,
               {_TICKET} AS ticket_medio,
               {_CANCELLED} AS cancelados,
               COUNT(*) AS total_pedidos,
               {_CANCEL_RATE} AS taxa_cancelamento
        {_ORDERS}
        WHERE {_FILTERS}
    """
    row = pd.read_sql(text(sql), engine, params=_params(start, end, states)).iloc[0]
    return {
        "faturamento": float(row["faturamento"]),
        "pedidos": int(row["pedidos"]),
        "ticket_medio": None if pd.isna(row["ticket_medio"]) else float(row["ticket_medio"]),
        "cancelados": int(row["cancelados"]),
        "total_pedidos": int(row["total_pedidos"]),
        "taxa_cancelamento": None if pd.isna(row["taxa_cancelamento"]) else float(row["taxa_cancelamento"]),
    }


def revenue_over_time(
    engine: Engine, start: date, end: date, states: tuple[str, ...], grain: str = "month"
) -> pd.DataFrame:
    if grain not in GRAINS:
        raise ValueError(f"Granularidade inválida: {grain!r}")
    sql = f"""
        SELECT date_trunc(:grain, o.created_at AT TIME ZONE '{TIMEZONE}')::date AS periodo,
               {_REVENUE} AS faturamento,
               {_ORDER_COUNT} AS pedidos
        {_ORDERS}
        WHERE {_FILTERS}
        GROUP BY periodo
        ORDER BY periodo
    """
    frame = _read(engine, sql, {**_params(start, end, states), "grain": grain}, ("faturamento",))
    frame["periodo"] = pd.to_datetime(frame["periodo"])
    return frame


def revenue_by_state(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    sql = f"""
        SELECT c.state AS estado, {_REVENUE} AS faturamento, {_ORDER_COUNT} AS pedidos
        {_ORDERS}
        WHERE {_FILTERS}
        GROUP BY c.state
        ORDER BY faturamento DESC
    """
    return _read(engine, sql, _params(start, end, states), ("faturamento",))


def orders_by_status(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    sql = f"""
        SELECT o.status AS status, COUNT(*) AS pedidos
        {_ORDERS}
        WHERE {_FILTERS}
        GROUP BY o.status
        ORDER BY pedidos DESC
    """
    return _read(engine, sql, _params(start, end, states), ())


def orders_by_payment(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    sql = f"""
        SELECT o.payment AS pagamento, COUNT(*) AS pedidos
        {_ORDERS}
        WHERE {_FILTERS}
        GROUP BY o.payment
        ORDER BY pedidos DESC
    """
    return _read(engine, sql, _params(start, end, states), ())


def top_products(
    engine: Engine, start: date, end: date, states: tuple[str, ...], limit: int = 10
) -> pd.DataFrame:
    sql = f"""
        SELECT p.product_id::text AS product_id, p.name AS produto,
               p.macro_category AS macro_categoria,
               {_REVENUE} AS faturamento, {_ORDER_COUNT} AS pedidos
        {_ORDERS_PRODUCTS}
        WHERE {_FILTERS}
        GROUP BY p.product_id, p.name, p.macro_category
        HAVING {_ORDER_COUNT} > 0
        ORDER BY faturamento DESC, p.name
        LIMIT :limit
    """
    return _read(engine, sql, {**_params(start, end, states), "limit": limit}, ("faturamento",))


def category_summary(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    sql = f"""
        SELECT p.macro_category AS macro_categoria, {_REVENUE} AS faturamento,
               {_ORDER_COUNT} AS pedidos, {_CANCELLED} AS cancelados,
               {_CANCEL_RATE} AS taxa_cancelamento
        {_ORDERS_PRODUCTS}
        WHERE {_FILTERS}
        GROUP BY p.macro_category
        ORDER BY faturamento DESC
    """
    return _read(engine, sql, _params(start, end, states), ("faturamento", "taxa_cancelamento"))


def customers_by_segment(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    active = "COUNT(DISTINCT o.customer_id) FILTER (WHERE o.status <> 'cancelled')"
    sql = f"""
        SELECT c.segment AS segmento, {_REVENUE} AS faturamento, {_ORDER_COUNT} AS pedidos,
               {_TICKET} AS ticket_medio, {active} AS clientes_ativos,
               {_ORDER_COUNT}::numeric / NULLIF({active}, 0) AS frequencia
        {_ORDERS}
        WHERE {_FILTERS}
        GROUP BY c.segment
        ORDER BY faturamento DESC
    """
    return _read(engine, sql, _params(start, end, states), ("faturamento", "ticket_medio", "frequencia"))


def customers_by_state(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    sql = f"""
        SELECT c.state AS estado, {_REVENUE} AS faturamento, {_TICKET} AS ticket_medio
        {_ORDERS}
        WHERE {_FILTERS}
        GROUP BY c.state
        ORDER BY faturamento DESC
    """
    return _read(engine, sql, _params(start, end, states), ("faturamento", "ticket_medio"))


def review_summary(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> dict[str, float | int | None]:
    sql = f"""
        SELECT COUNT(*) AS avaliacoes, AVG(r.rating) AS nota_media
        {_REVIEWS}
        WHERE {_FILTERS}
    """
    row = pd.read_sql(text(sql), engine, params=_params(start, end, states)).iloc[0]
    return {
        "avaliacoes": int(row["avaliacoes"]),
        "nota_media": None if pd.isna(row["nota_media"]) else float(row["nota_media"]),
    }


def sentiment_distribution(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    sql = f"""
        SELECT r.sentiment AS sentimento, COUNT(*) AS avaliacoes,
               COUNT(*)::numeric / SUM(COUNT(*)) OVER () AS pct
        {_REVIEWS}
        WHERE {_FILTERS}
        GROUP BY r.sentiment
        ORDER BY avaliacoes DESC
    """
    return _read(engine, sql, _params(start, end, states), ("pct",))


def rating_by_category(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    sql = f"""
        SELECT p.macro_category AS macro_categoria, COUNT(*) AS avaliacoes,
               AVG(r.rating) AS nota_media
        {_REVIEWS}
        WHERE {_FILTERS}
        GROUP BY p.macro_category
        ORDER BY nota_media
    """
    return _read(engine, sql, _params(start, end, states), ("nota_media",))


def negative_comments(
    engine: Engine, start: date, end: date, states: tuple[str, ...], limit: int = 50
) -> pd.DataFrame:
    sql = f"""
        SELECT (o.created_at AT TIME ZONE '{TIMEZONE}')::date AS data, p.name AS produto,
               p.macro_category AS macro_categoria, r.rating AS nota, r.comment AS comentario
        {_REVIEWS}
        WHERE {_FILTERS} AND r.sentiment = 'negative'
        ORDER BY o.created_at DESC
        LIMIT :limit
    """
    return _read(engine, sql, {**_params(start, end, states), "limit": limit}, ())


def kpi_series(
    engine: Engine, start: date, end: date, states: tuple[str, ...], grain: str = "month"
) -> pd.DataFrame:
    """All headline KPIs per period, for sparklines and period comparisons."""
    if grain not in GRAINS:
        raise ValueError(f"Granularidade inválida: {grain!r}")
    sql = f"""
        SELECT date_trunc(:grain, o.created_at AT TIME ZONE '{TIMEZONE}')::date AS periodo,
               {_REVENUE} AS faturamento,
               {_ORDER_COUNT} AS pedidos,
               COALESCE({_TICKET}, 0) AS ticket_medio,
               COALESCE({_CANCEL_RATE}, 0) AS taxa_cancelamento
        {_ORDERS}
        WHERE {_FILTERS}
        GROUP BY periodo
        ORDER BY periodo
    """
    numeric = ("faturamento", "ticket_medio", "taxa_cancelamento")
    frame = _read(engine, sql, {**_params(start, end, states), "grain": grain}, numeric)
    frame["periodo"] = pd.to_datetime(frame["periodo"])
    return frame


def orders_heatmap(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    """Orders by local weekday (1 = Monday) and hour."""
    local = f"o.created_at AT TIME ZONE '{TIMEZONE}'"
    sql = f"""
        SELECT EXTRACT(ISODOW FROM {local})::int AS dia_semana,
               EXTRACT(HOUR FROM {local})::int AS hora,
               {_ORDER_COUNT} AS pedidos
        {_ORDERS}
        WHERE {_FILTERS}
        GROUP BY dia_semana, hora
        ORDER BY dia_semana, hora
    """
    return _read(engine, sql, _params(start, end, states), ())


def state_scorecard(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    active = "COUNT(DISTINCT o.customer_id) FILTER (WHERE o.status <> 'cancelled')"
    sql = f"""
        WITH sales AS (
            SELECT c.state AS estado, {_REVENUE} AS faturamento, {_ORDER_COUNT} AS pedidos,
                   {_TICKET} AS ticket_medio, {_CANCEL_RATE} AS taxa_cancelamento,
                   {active} AS clientes_ativos
            {_ORDERS}
            WHERE {_FILTERS}
            GROUP BY c.state
        ),
        ratings AS (
            SELECT c.state AS estado, AVG(r.rating) AS nota_media, COUNT(*) AS avaliacoes
            {_REVIEWS}
            WHERE {_FILTERS}
            GROUP BY c.state
        )
        SELECT s.estado, s.faturamento, s.pedidos, s.ticket_medio, s.taxa_cancelamento,
               s.clientes_ativos, r.nota_media, COALESCE(r.avaliacoes, 0) AS avaliacoes
        FROM sales s
        LEFT JOIN ratings r ON r.estado = s.estado
        ORDER BY s.faturamento DESC
    """
    numeric = ("faturamento", "ticket_medio", "taxa_cancelamento", "nota_media")
    return _read(engine, sql, _params(start, end, states), numeric)


def product_performance(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    """Every product with sales in the period; ranking and growth happen in pandas."""
    sql = f"""
        SELECT p.product_id::text AS product_id, p.name AS produto,
               p.macro_category AS macro_categoria,
               {_REVENUE} AS faturamento, {_ORDER_COUNT} AS pedidos
        {_ORDERS_PRODUCTS}
        WHERE {_FILTERS}
        GROUP BY p.product_id, p.name, p.macro_category
        ORDER BY faturamento DESC, p.name
    """
    return _read(engine, sql, _params(start, end, states), ("faturamento",))


def category_state_matrix(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    sql = f"""
        SELECT p.macro_category AS macro_categoria, c.state AS estado, {_REVENUE} AS faturamento
        {_ORDERS_PRODUCTS}
        WHERE {_FILTERS}
        GROUP BY p.macro_category, c.state
    """
    return _read(engine, sql, _params(start, end, states), ("faturamento",))


def payment_over_time(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    sql = f"""
        SELECT date_trunc('month', o.created_at AT TIME ZONE '{TIMEZONE}')::date AS periodo,
               o.payment AS pagamento, COUNT(*) AS pedidos
        {_ORDERS}
        WHERE {_FILTERS}
        GROUP BY periodo, o.payment
        ORDER BY periodo
    """
    frame = _read(engine, sql, _params(start, end, states), ())
    frame["periodo"] = pd.to_datetime(frame["periodo"])
    return frame


def order_frequency(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    """How many customers placed N non-cancelled orders in the period."""
    sql = f"""
        SELECT pedidos_cliente, COUNT(*) AS clientes
        FROM (
            SELECT o.customer_id, COUNT(*) AS pedidos_cliente
            {_ORDERS}
            WHERE {_FILTERS} AND o.status <> 'cancelled'
            GROUP BY o.customer_id
        ) por_cliente
        GROUP BY pedidos_cliente
        ORDER BY pedidos_cliente
    """
    return _read(engine, sql, _params(start, end, states), ())


def rating_distribution(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    sql = f"""
        SELECT r.rating AS nota, COUNT(*) AS avaliacoes
        {_REVIEWS}
        WHERE {_FILTERS}
        GROUP BY r.rating
        ORDER BY r.rating
    """
    return _read(engine, sql, _params(start, end, states), ())


def sentiment_by_category(engine: Engine, start: date, end: date, states: tuple[str, ...]) -> pd.DataFrame:
    sql = f"""
        SELECT p.macro_category AS macro_categoria, r.sentiment AS sentimento, COUNT(*) AS avaliacoes
        {_REVIEWS}
        WHERE {_FILTERS}
        GROUP BY p.macro_category, r.sentiment
    """
    return _read(engine, sql, _params(start, end, states), ())
