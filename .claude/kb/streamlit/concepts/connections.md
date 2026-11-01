# Connections

> **Purpose**: Choose how the dashboard reaches Postgres -- SQLAlchemy engine, `st.connection`, or psycopg2
> **Confidence**: 0.95
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## Overview

The architecture keeps data logic apart from the interface so a future agent can reuse the queries.
That rules out Streamlit imports in `src/`. So the default is a SQLAlchemy engine built in `src/db.py`
from environment variables and cached in the app with `st.cache_resource`.

## The Pattern

```python
# src/db.py -- no Streamlit import
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, Engine, create_engine

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def create_db_engine() -> Engine:
    url = URL.create(
        "postgresql+psycopg2",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],  # Plain text, not URL encoded
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ["POSTGRES_DB"],
    )
    return create_engine(url, pool_pre_ping=True)
```

`POSTGRES_PORT` matters on this machine, because a native Postgres already holds port 5432.

## Quick Reference

| Option | Good for | Limits here |
|--------|----------|-------------|
| Engine in `src/db.py` | This dashboard; reusable outside Streamlit | You write the `st.cache_data` wrappers |
| `st.connection(..., type="sql")` | Single-file prototypes | Query caching lives in Streamlit, not reusable by an agent |
| psycopg2 connection | Scripts such as `src/day2/ledger_queries.py` | No pooling; `pandas.read_sql` warns |
| psycopg2 `ThreadedConnectionPool` | Pooling without SQLAlchemy | Manual `getconn`/`putconn`; `read_sql` still warns |

| Fact | Detail |
|------|--------|
| Default pool | `QueuePool`, `pool_size=5`, `max_overflow=10` |
| `pool_pre_ping=True` | Tests liveness on checkout, for small overhead |
| Engine lifetime | Created once per URL, held for the process, used concurrently |

## Why Not Cache a psycopg2 Connection

A psycopg2 connection is thread-safe, but threads sharing it share one session and one transaction,
and commands are serialized. After a failed statement, "the transaction will be aborted" until
`rollback()`. So one bad query from one user breaks reads for every session. An engine hands each
read its own pooled connection instead.

## st.connection Reference

```toml
# .streamlit/secrets.toml -- NOT covered by this repo's .gitignore yet
[connections.shopagent]
type = "sql"
dialect = "postgresql"
host = "localhost"
port = "5432"
database = "shopagent"
username = "shopagent"
password = "shopagent"
```

```python
conn = st.connection("shopagent", type="sql")
df = conn.query(
    "SELECT * FROM orders WHERE status = :status",
    params={"status": "delivered"},
    ttl="5m",  # Default None caches forever; ttl=0 disables caching
)
```

| Behavior | Detail |
|----------|--------|
| Requirements | `SQLAlchemy>=2.0` plus a driver (`streamlit[sql]`, `psycopg2-binary`) |
| Required fields | `url`, or `dialect` + `username` + `host` |
| Kwargs | Override `secrets.toml`, so env vars can be passed as kwargs |
| Object cache | Cached with `st.cache_resource` |
| Stale connection | `conn.reset()` |
| Query retries | 3 attempts on database errors, per the source |

## Common Mistakes

### Wrong

```python
# Password with @ breaks the string; credentials are hard-coded
engine = create_engine("postgresql://shopagent:p@ss@localhost/shopagent")
```

### Correct

```python
url = URL.create("postgresql+psycopg2", username=user, password=password, host=host)
engine = create_engine(url, pool_pre_ping=True)
```

## Related

- [Caching](../concepts/caching.md)
- [Data Access Layer](../patterns/data-access-layer.md)
- [pandas read_sql](../../pandas/concepts/read-sql.md)
