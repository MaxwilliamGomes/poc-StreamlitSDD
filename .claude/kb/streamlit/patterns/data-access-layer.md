# Data Access Layer

> **Purpose**: Keep SQL in `src/queries.py`, add caching in `app/data.py`, and let pages see only DataFrames
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## When to Use

- Any page that reads from Postgres
- Any query a future agent could reuse as a tool
- Adding a KPI: one function in `src/queries.py`, one wrapper in `app/data.py`

## Implementation

```python
# src/queries.py -- SQL only; no Streamlit import
from datetime import date

import pandas as pd
from sqlalchemy import Engine, text

from src.time_range import to_epoch_ms_bounds

DAILY_REVENUE_SQL = text("""
    SELECT (to_timestamp(o.created_at / 1000.0) AT TIME ZONE 'America/Sao_Paulo')::date AS dia,
           COUNT(*)     AS pedidos,
           SUM(o.total) AS faturamento
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.created_at >= :start_ms
      AND o.created_at <  :end_ms
      AND o.status <> 'cancelled'
      AND (CAST(:states AS text[]) IS NULL OR c.state = ANY(CAST(:states AS text[])))
    GROUP BY dia
    ORDER BY dia
""")


def daily_revenue(
    engine: Engine, start: date, end: date, states: tuple[str, ...]
) -> pd.DataFrame:
    start_ms, end_ms = to_epoch_ms_bounds(start, end)
    frame = pd.read_sql(
        DAILY_REVENUE_SQL,
        engine,
        params={
            "start_ms": start_ms,
            "end_ms": end_ms,
            "states": list(states) or None,  # Empty selection means "all states"
        },
        dtype={"pedidos": "int64", "faturamento": "float64"},
    )
    frame["dia"] = pd.to_datetime(frame["dia"])
    return frame
```

```python
# app/data.py -- the only app module that calls src.queries
from datetime import date

import pandas as pd
import streamlit as st
from sqlalchemy import Engine

from src import db, queries

KPI_TTL = "5m"
OPTIONS_TTL = "1h"


@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    return db.create_db_engine()


@st.cache_data(ttl=KPI_TTL, max_entries=256, show_spinner="Consultando o banco...")
def load_daily_revenue(
    start: date, end: date, states: tuple[str, ...]
) -> pd.DataFrame:
    return queries.daily_revenue(get_engine(), start, end, states)


@st.cache_data(ttl=OPTIONS_TTL, show_spinner=False)
def load_filter_options() -> dict[str, list[str]]:
    return queries.filter_options(get_engine())
```

The example shows the old `bigint` epoch column. This repo now has `TIMESTAMPTZ`: bind timezone-aware
bounds, as `src/queries.py` does. See [Epoch Datetimes](../../pandas/concepts/epoch-datetimes.md).

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `KPI_TTL` | `"5m"` | Allowed staleness of order-based KPIs |
| `OPTIONS_TTL` | `"1h"` | Allowed staleness of filter option lists |
| `max_entries` | `256` | Bound on entries created by filter combinations |
| `status <> 'cancelled'` | Excludes cancelled | Revenue rule; define it once per KPI |

## Layer Rules

| Layer | May import | Must not |
|-------|------------|----------|
| `src/queries.py` | pandas, SQLAlchemy | Import Streamlit |
| `app/data.py` | `src`, Streamlit | Contain SQL |
| `app/pages/*` | `data`, `components`, `charts` | Contain SQL or call `src.queries` |

`text()` does not bind `:states::text[]`, because its pattern rejects a name followed by `:`.
Use `CAST(:states AS text[])`. Plain casts such as `o.created_at::date` are fine.

## Example Usage

```python
# app/pages/1_Vendas.py
from components.filters import render_sidebar_filters
from data import load_daily_revenue

filters = render_sidebar_filters()
daily = load_daily_revenue(filters.start, filters.end, filters.states)
```

## See Also

- [Caching](../concepts/caching.md)
- [Connections](../concepts/connections.md)
- [Error and Empty States](error-empty-states.md)
- [Parameterized Queries](../../pandas/patterns/parameterized-queries.md)
