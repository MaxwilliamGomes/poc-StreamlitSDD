# Dtypes

> **Purpose**: Return predictable column types from every query, including empty results
> **Confidence**: 0.95
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; behavior run on local pandas 2.2.3)

## Overview

psycopg2 returns `numeric` and `decimal` columns as Python `Decimal`. `SUM(orders.total)` is therefore
a `Decimal`, and so is any `AVG`. `read_sql` converts these to float by default,
but an empty result has no values to inspect and stays `object`. Declaring `dtype` handles both cases.

## The Pattern

```python
import pandas as pd
from sqlalchemy import Engine, text

KPI_DTYPES = {
    "pedidos": "int64",
    "itens": "int64",
    "faturamento": "float64",
    "ticket_medio": "float64",
}


def revenue_by_state(engine: Engine, start_ms: int, end_ms: int) -> pd.DataFrame:
    return pd.read_sql(
        text("""
            SELECT c.state AS estado,
                   COUNT(*) AS pedidos,
                   SUM(o.qty) AS itens,
                   SUM(o.total) AS faturamento,
                   AVG(o.total) AS ticket_medio
            FROM orders o
            JOIN customers c ON c.customer_id = o.customer_id
            WHERE o.created_at >= :start_ms AND o.created_at < :end_ms
            GROUP BY c.state
        """),
        engine,
        params={"start_ms": start_ms, "end_ms": end_ms},
        dtype=KPI_DTYPES,
    )
```

## Quick Reference

| Postgres | psycopg2 value | Default pandas | Declare |
|----------|----------------|----------------|---------|
| `DECIMAL(10,2)`, `numeric` | `Decimal` | `float64` via `coerce_float` | `float64` |
| `SUM(int)` | `int` or `Decimal` | Varies | `int64`, or `Int64` with NULLs |
| `COUNT(*)` | `int` | `int64` | `int64` |
| `AVG(...)` | `Decimal` | `float64` | `float64` |
| `INTEGER` with NULLs | `int`, `None` | `float64` | `Int64` |
| `bigint` epoch ms | `int` | `int64`, or `float64` with NULLs | Convert to datetime |
| `TIMESTAMPTZ` | `datetime` | `datetime64` or `object` | `pd.to_datetime(..., utc=True)` |
| `date` | `date` | `object` | `pd.to_datetime(...)` |
| `UUID` | `str`, or `uuid.UUID` through SQLAlchemy | `object` or `str` | Select `order_id::text` if displayed |
| `VARCHAR` | `str` | `str` in 3.0, `object` before | Leave as text |

Observed locally with `from_records`, which `read_sql` uses:

| Rows | `coerce_float=True` | `coerce_float=False` |
|------|---------------------|----------------------|
| `Decimal("1234.56")`, `None` | `float64`, `NaN` | `object` with `Decimal`, `None` |
| Empty result | `object` | `object` |

## Float for Display, Decimal for Accounting

`float64` is correct for a dashboard. Sums of `DECIMAL(10,2)` values stay far below 2**53, and display
rounds to two places. Compute exact totals in Postgres and let pandas carry the result. Do not sum
floats in pandas and then compare them with a ledger value for equality.

## pandas 3 Changes

| Change | Impact |
|--------|--------|
| Default `str` dtype | Text columns are `str`, not `object`; only strings and missing values allowed |
| Missing strings | Always `NaN` |
| PyArrow | Backs `str` when installed; Streamlit requires it |
| Copy-on-Write | Indexing results act as copies; chained assignment no longer works |
| `SettingWithCopyWarning` | Removed |

Code that checks `dtype == object` for text breaks. Use `pd.api.types.is_string_dtype`.

## Categoricals

Low-cardinality labels such as `status` can be `category`. `groupby` has defaulted to `observed=True`
since 3.0, so unused categories are dropped unless `observed=False` is passed. That is useful for
showing a status with zero orders. Text columns from Postgres need no conversion otherwise.

## Common Mistakes

### Wrong

```python
frame = pd.read_sql(sql, engine)
total = frame["faturamento"].sum()     # On an empty result: object column, 0
frame["faturamento"] / 2               # TypeError risk if Decimal remains (coerce_float=False)
frame["total"]["a"] = 0                # Chained assignment has no effect in pandas 3
```

### Correct

```python
frame = pd.read_sql(sql, engine, dtype={"faturamento": "float64"})
frame = frame.assign(metade=frame["faturamento"] / 2)
```

## Related

- [read_sql](../concepts/read-sql.md)
- [Epoch Datetimes](../concepts/epoch-datetimes.md)
- [KPI Aggregations](../patterns/kpi-aggregations.md)
