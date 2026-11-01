# KPI Aggregations

> **Purpose**: Compute dashboard KPIs with SQL totals, `groupby` summaries, and pivots
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; pandas logic run on local pandas 2.2.3)

## When to Use

- Headline cards for the selected and previous period
- Summaries of a frame already in memory
- Long-to-wide reshaping for tables and heatmaps

## Implementation

```python
# src/queries.py
from dataclasses import dataclass
from datetime import date

import pandas as pd
from sqlalchemy import Engine, text

from src.time_range import to_epoch_ms_bounds

KPI_TOTALS_SQL = text("""
    SELECT COUNT(*) FILTER (WHERE o.status <> 'cancelled')     AS pedidos,
           COUNT(*) FILTER (WHERE o.status = 'cancelled')      AS cancelados,
           COUNT(*)                                            AS todos,
           COALESCE(SUM(o.total) FILTER (WHERE o.status <> 'cancelled'), 0) AS faturamento
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.created_at >= :start_ms
      AND o.created_at <  :end_ms
      AND (CAST(:states AS text[]) IS NULL OR c.state = ANY(CAST(:states AS text[])))
""")


@dataclass(frozen=True)
class KpiTotals:
    revenue: float
    orders: int
    average_ticket: float | None
    cancel_rate: float | None


def kpi_totals(
    engine: Engine, start: date, end: date, states: tuple[str, ...]
) -> KpiTotals:
    start_ms, end_ms = to_epoch_ms_bounds(start, end)
    row = pd.read_sql(
        KPI_TOTALS_SQL,
        engine,
        params={"start_ms": start_ms, "end_ms": end_ms, "states": list(states) or None},
        dtype={
            "pedidos": "int64",
            "cancelados": "int64",
            "todos": "int64",
            "faturamento": "float64",
        },
    ).iloc[0]

    return KpiTotals(
        revenue=float(row["faturamento"]),
        orders=int(row["pedidos"]),
        average_ticket=(
            float(row["faturamento"] / row["pedidos"]) if row["pedidos"] else None
        ),
        cancel_rate=float(row["cancelados"] / row["todos"]) if row["todos"] else None,
    )
```

```python
# Summaries of an in-memory frame
def summarize_by_state(orders: pd.DataFrame) -> pd.DataFrame:
    summary = (
        orders.groupby("estado", as_index=False)
        .agg(
            pedidos=("order_id", "nunique"),
            clientes=("customer_id", "nunique"),
            faturamento=("total", "sum"),
        )
        .sort_values("faturamento", ascending=False, ignore_index=True)
    )
    return summary.assign(
        ticket_medio=summary["faturamento"] / summary["pedidos"],
        participacao=summary["faturamento"] / summary["faturamento"].sum(),
    )


def state_category_pivot(frame: pd.DataFrame) -> pd.DataFrame:
    """Expect long columns `estado`, `categoria`, `faturamento`."""
    return frame.pivot_table(
        index="estado",
        columns="categoria",
        values="faturamento",
        aggfunc="sum",
        fill_value=0,
    )
```

## Configuration

| `groupby` option | Default | Use |
|------------------|---------|-----|
| `as_index` | `True` | `False` gives SQL-style columns, as Plotly expects |
| `sort` | `True` | Sorts group keys, not values |
| `observed` | `True` (since 3.0) | Only affects categoricals |
| `dropna` | `True` | `False` keeps NULL keys, such as a missing brand |

| `pivot_table` option | Default | Use |
|----------------------|---------|-----|
| `aggfunc` | `"mean"` | Set `"sum"` for revenue |
| `fill_value` | `None` | `0` for empty combinations |
| `margins` | `False` | `True` adds totals |
| `margins_name` | `"All"` | Set `"Total"` for pt-BR tables |
| `observed` | `True` | Changed in 3.0 |
| `sort` | `True` | Sorts the result |

## KPI Definitions

| KPI | Definition | Note |
|-----|------------|------|
| Faturamento | `SUM(total)` of non-cancelled orders | Decide once; apply to all pages |
| Pedidos | Count of non-cancelled orders | Each order row is a single product |
| Ticket médio | Faturamento / pedidos | `None` when there are no orders |
| Taxa de cancelamento | Cancelled / all orders | Fraction, 0 to 1 |
| Crescimento | `safe_growth(atual, anterior)` | `None` on a zero base |
| Participação | Group revenue / total revenue | From the full, not top-N, total |

`SUM` over no rows is `NULL` in Postgres, hence `COALESCE`. An aggregate without `GROUP BY` always
returns one row, so `.iloc[0]` is safe.

## Useful Operations

| Need | Code |
|------|------|
| Top N | `frame.nlargest(10, "faturamento")` |
| Rank | `frame["faturamento"].rank(ascending=False, method="dense")` |
| Wide to long | `frame.melt(id_vars="dia", var_name="status", value_name="pedidos")` |
| Row share | `pd.crosstab(frame["estado"], frame["status"], normalize="index")` |

## Example Usage

```python
# app/data.py
@st.cache_data(ttl=KPI_TTL, show_spinner=False)
def load_kpi_totals(
    start: date, end: date, states: tuple[str, ...]
) -> queries.KpiTotals:
    return queries.kpi_totals(get_engine(), start, end, states)
```

A frozen dataclass of plain values pickles normally, so it is a valid `st.cache_data` return value.

## See Also

- [SQL vs pandas](../concepts/sql-vs-pandas.md)
- [pt-BR Display Formatting](ptbr-display-formatting.md)
- [Streamlit KPI Cards](../../streamlit/patterns/kpi-cards.md)
- [Plotly Category Breakdown](../../plotly/patterns/category-breakdown.md)
