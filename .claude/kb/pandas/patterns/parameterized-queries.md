# Parameterized Queries

> **Purpose**: Pass every filter value through binds, including optional lists and limits
> **MCP Validated**: 2026-11-01 (official docs, SQLAlchemy and pandas source; not run against Postgres)

## When to Use

- Any query shaped by sidebar filters
- Optional filters, where an empty selection means "all"
- Sort or grouping choices, which binds cannot express

## Implementation

```python
# src/queries.py
from dataclasses import dataclass
from datetime import date

import pandas as pd
from sqlalchemy import Engine, text

from src.time_range import to_epoch_ms_bounds

GROUPINGS = {
    "estado": "c.state",
    "segmento": "c.segment",
    "pagamento": "o.payment",
}

REVENUE_BY_GROUP_SQL = """
    SELECT {group_column} AS grupo,
           COUNT(*)     AS pedidos,
           SUM(o.total) AS faturamento
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.created_at >= :start_ms
      AND o.created_at <  :end_ms
      AND (CAST(:states AS text[])   IS NULL OR c.state   = ANY(CAST(:states AS text[])))
      AND (CAST(:segments AS text[]) IS NULL OR c.segment = ANY(CAST(:segments AS text[])))
    GROUP BY grupo
    ORDER BY faturamento DESC
    LIMIT :limit
"""


@dataclass(frozen=True)
class OrderFilters:
    start: date
    end: date
    states: tuple[str, ...] = ()
    segments: tuple[str, ...] = ()

    def to_params(self) -> dict[str, object]:
        start_ms, end_ms = to_epoch_ms_bounds(self.start, self.end)
        return {
            "start_ms": start_ms,
            "end_ms": end_ms,
            "states": list(self.states) or None,
            "segments": list(self.segments) or None,
        }


def revenue_by_group(
    engine: Engine, group: str, filters: OrderFilters, limit: int = 20
) -> pd.DataFrame:
    if group not in GROUPINGS:
        raise ValueError(f"Unknown grouping '{group}'. Valid: {sorted(GROUPINGS)}")

    # The identifier comes from the allow-list above, never from user text
    statement = text(REVENUE_BY_GROUP_SQL.format(group_column=GROUPINGS[group]))
    return pd.read_sql(
        statement,
        engine,
        params={**filters.to_params(), "limit": limit},
        dtype={"pedidos": "int64", "faturamento": "float64"},
    )
```

## Configuration

| Value kind | Bind? | How |
|------------|-------|-----|
| Date bounds, status, limit | Yes | `:name` |
| List | Yes | psycopg2 adapts a list to `ARRAY`, with `= ANY(...)` |
| Empty selection | Yes | `None`, with `CAST(:x AS text[]) IS NULL` |
| Text search | Yes | `name ILIKE :pattern`, with `f"%{term}%"` as the value |
| Column name | No | Allow-list |
| `ASC`/`DESC` | No | Allow-list |

## Why `CAST` and `ANY`

| Form | Result |
|------|--------|
| `c.state = ANY(:states)` | Works for a list, but `NULL` needs a type |
| `:states::text[]` | `text()` does not bind it; the literal reaches Postgres |
| `CAST(:states AS text[])` | Bound, typed, and usable with `NULL` |
| `IN :states` | Needs `bindparam("states", expanding=True)`; `IN ()` is invalid |

`customers.state` is `CHAR(2)`. Comparing it with `text[]` works here because all values use both
characters, so trailing-space padding does not come into play. Prefer `ANY` with lists, since psycopg2
documents that it handles empty lists, while `IN ()` fails.

## psycopg2 Style

The same query shape in a plain-string form, as used by `src/day2/ledger_queries.py`:

```python
sql = """
    SELECT status, COUNT(*) AS total
    FROM orders
    WHERE created_at >= %(start_ms)s AND created_at < %(end_ms)s
      AND (%(states)s IS NULL OR status = ANY(%(states)s))
    GROUP BY status
"""
with connection.cursor() as cursor:
    cursor.execute(sql, {"start_ms": start_ms, "end_ms": end_ms, "states": ["delivered"]})
```

| Rule | Detail |
|------|--------|
| Placeholders | Always `%s` or `%(name)s`, unquoted, for every type |
| Literal `%` | `%%` when parameters are used |
| Identifiers | `psycopg2.sql`, not binds |
| Rule from the docs | "Never use `%` or `+` to merge values into queries" |

## Example Usage

```python
# app/data.py
@st.cache_data(ttl=KPI_TTL, max_entries=256, show_spinner=False)
def load_revenue_by_group(group: str, filters: queries.OrderFilters) -> pd.DataFrame:
    return queries.revenue_by_group(get_engine(), group, filters)
```

A frozen dataclass of hashable fields works as a cache argument. If hashing fails, pass plain fields.

```python
frame = load_revenue_by_group(
    "estado", OrderFilters(filters.start, filters.end, filters.states, filters.segments)
)
```

## See Also

- [read_sql](../concepts/read-sql.md)
- [Epoch Datetimes](../concepts/epoch-datetimes.md)
- [Streamlit Sidebar Filters](../../streamlit/patterns/sidebar-filters.md)
