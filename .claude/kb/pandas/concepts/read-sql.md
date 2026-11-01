# read_sql

> **Purpose**: Load Postgres query results into DataFrames with bound parameters
> **Confidence**: 0.95
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## Overview

`pd.read_sql` runs a query and returns a DataFrame. Officially it supports SQLAlchemy connectables,
ADBC connections, URI strings, and sqlite3. A raw psycopg2 connection works but emits a `UserWarning`,
because other DBAPI objects are untested. This project passes a SQLAlchemy engine.

## The Pattern

```python
import pandas as pd
from sqlalchemy import Engine, text

ORDERS_BY_STATUS_SQL = text("""
    SELECT status, COUNT(*) AS pedidos, SUM(total) AS faturamento
    FROM orders
    WHERE created_at >= :start_ms AND created_at < :end_ms
    GROUP BY status
    ORDER BY faturamento DESC
""")


def orders_by_status(engine: Engine, start_ms: int, end_ms: int) -> pd.DataFrame:
    return pd.read_sql(
        ORDERS_BY_STATUS_SQL,
        engine,
        params={"start_ms": start_ms, "end_ms": end_ms},
        dtype={"pedidos": "int64", "faturamento": "float64"},
    )
```

## Quick Reference

| `sql` type | Placeholder | Executed through |
|------------|-------------|------------------|
| `text("... :name")` | `:name` | SQLAlchemy binds |
| Plain string, SQLAlchemy `con` | `%(name)s` | `exec_driver_sql`, so psycopg2 style |
| Plain string, raw psycopg2 | `%(name)s` or `%s` | Driver directly, with a warning |
| `st.connection(...).query` | `:name` | Wraps the string in `text()` |

| Parameter | Default | Notes |
|-----------|---------|-------|
| `coerce_float` | `True` | `Decimal` to float; may lose precision above 2**53 |
| `dtype` | `None` | Mapping such as `{"faturamento": "float64"}` |
| `index_col` | `None` | Usually leave columns as columns |
| `parse_dates` | `None` | Convert after reading instead |
| `chunksize` | `None` | Returns an iterator; rarely lowers peak memory |
| `dtype_backend` | Not set | `"numpy_nullable"`, `"pyarrow"`; experimental |

## Engine vs Raw psycopg2

```python
# Works, but pandas warns that this connection type is untested
with psycopg2.connect(**settings) as connection:
    frame = pd.read_sql(
        "SELECT * FROM orders WHERE status = %(status)s",
        connection,
        params={"status": "delivered"},
    )
```

If a script must stay on psycopg2 without pandas warnings, use a cursor and build the frame:

```python
with connection.cursor() as cursor:
    cursor.execute(sql, params)
    columns = [description[0] for description in cursor.description]
    frame = pd.DataFrame.from_records(cursor.fetchall(), columns=columns, coerce_float=True)
```

## Errors

| Failure | Exception |
|---------|-----------|
| SQL fails during execution (pandas 3.0+) | `pandas.errors.DatabaseError`, chained from the driver error |
| Cannot connect | `sqlalchemy.exc.OperationalError` |

The `DatabaseError` message includes the full SQL text. Log it, but do not show it to viewers.

## Escaping

| Case | Write |
|------|-------|
| `LIKE` in `text()` | `name LIKE :pattern`, with `%` in the value |
| Literal `%` in a plain string with `params` | `%%` |
| Postgres cast in `text()` | `o.created_at::date` works |
| Cast on a bind in `text()` | `CAST(:x AS text[])`; `:x::text[]` is not bound |

The bind pattern is `(?<![:\w\x5c]):(\w+)(?![:\w])`, which rejects a name followed by `:`.

## Common Mistakes

### Wrong

```python
sql = f"SELECT * FROM orders WHERE status = '{status}'"  # SQL injection
pd.read_sql(sql, engine)

pd.read_sql("SELECT * FROM orders WHERE status = :status", engine, params=params)
# A plain string goes to the driver, which does not understand :status
```

### Correct

```python
pd.read_sql(
    text("SELECT * FROM orders WHERE status = :status"),
    engine,
    params={"status": status},
)
```

## Related

- [Dtypes](../concepts/dtypes.md)
- [SQL vs pandas](../concepts/sql-vs-pandas.md)
- [Parameterized Queries](../patterns/parameterized-queries.md)
- [Streamlit Connections](../../streamlit/concepts/connections.md)
