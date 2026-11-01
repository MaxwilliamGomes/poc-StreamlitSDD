# SQL vs pandas

> **Purpose**: Decide where each aggregation runs
> **Confidence**: 0.90
> **MCP Validated**: 2026-11-01 (APIs checked against official docs; the division of work is editorial)

## Overview

Default to SQL. Postgres already has the data, the indexes, and the exact `numeric` arithmetic, and a
query in `src/queries.py` can later serve as an agent tool. pandas then handles what is awkward in SQL
or specific to presentation. These rules are this project's judgment, not a statement from the docs.

## The Pattern

```python
import pandas as pd
from sqlalchemy import Engine, text

TOP_PRODUCTS_SQL = text("""
    SELECT p.name AS nome,
           p.category AS categoria,
           COUNT(*) AS pedidos,
           SUM(o.total) AS faturamento
    FROM orders o
    JOIN products p ON p.product_id = o.product_id
    WHERE o.created_at >= :start_ms AND o.created_at < :end_ms
      AND o.status <> 'cancelled'
    GROUP BY p.product_id, p.name, p.category
    ORDER BY faturamento DESC
    LIMIT :limit
""")


def top_products(
    engine: Engine, start_ms: int, end_ms: int, limit: int = 10
) -> pd.DataFrame:
    """SQL aggregates, sorts, and limits; pandas adds the share afterward."""
    frame = pd.read_sql(
        TOP_PRODUCTS_SQL,
        engine,
        params={"start_ms": start_ms, "end_ms": end_ms, "limit": limit},
        dtype={"pedidos": "int64", "faturamento": "float64"},
    )
    return frame.assign(share=frame["faturamento"] / frame["faturamento"].sum())
```

Here `share` means share of the top 10, not of all revenue. For share of the total, compute it in SQL
with `SUM(SUM(o.total)) OVER ()` before the `LIMIT` applies.

## Quick Reference

| Task | Where | Reason |
|------|-------|--------|
| Filter rows | SQL | Uses indexes, moves less data |
| Joins | SQL | Foreign keys and indexes exist |
| `SUM`, `COUNT`, `AVG` by group | SQL | Exact and fast |
| Top N | SQL | `ORDER BY ... LIMIT` |
| `COUNT(DISTINCT ...)` | SQL | Cannot be recombined later |
| Share of the full total | SQL | Window function sees all rows |
| Fill missing days | pandas | `reindex` is simpler |
| Rolling average | pandas | Short, on an aggregated series |
| Pivot for a heatmap | pandas | `pivot_table` on long SQL output |
| Period-over-period growth | pandas | Two cached results, one calculation |
| Labels and display formats | pandas | Presentation |

## Warning Signs

| Sign | Action |
|------|--------|
| `SELECT *` from `orders` in a page | Write an aggregate query |
| Rows fetched only to `groupby` once | Move the `GROUP BY` to SQL |
| Filtering in pandas after fetching everything | Add `WHERE` with binds |
| Same aggregate in two pages | One function in `src/queries.py` |
| Long `.apply` over rows | Vectorize, or do it in SQL |

## When Raw Rows Are Reasonable

A small filtered window, an order detail table, or several KPIs drawn from one cached frame can justify
fetching rows. Bound the query with a date range and a `LIMIT`. Every fetched frame is also pickled into
the `st.cache_data` entry, so memory scales with rows times filter combinations.

## Non-Additive Metrics

| Metric | Correct total |
|--------|---------------|
| Ticket médio | `SUM(faturamento) / SUM(pedidos)`, never the mean of means |
| Unique customers | Query distinct counts per grain; they do not add up |
| Share of status | Recompute from counts |

## Common Mistakes

### Wrong

```python
orders = pd.read_sql(text("SELECT * FROM orders"), engine)
result = orders.groupby("status")["total"].sum()   # Whole table on every miss
overall_ticket = by_state["ticket_medio"].mean()   # Ignores order volume
```

### Correct

```python
by_status = load_orders_by_status(filters.start, filters.end, filters.states)
overall_ticket = by_state["faturamento"].sum() / by_state["pedidos"].sum()
```

## Related

- [read_sql](../concepts/read-sql.md)
- [KPI Aggregations](../patterns/kpi-aggregations.md)
- [Streamlit Data Access Layer](../../streamlit/patterns/data-access-layer.md)
