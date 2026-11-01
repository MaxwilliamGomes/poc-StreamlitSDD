# Caching

> **Purpose**: Choose between `st.cache_data` and `st.cache_resource` and set explicit TTLs
> **Confidence**: 0.95
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## Overview

Streamlit reruns the script on every interaction, so database reads must be cached. `st.cache_data`
stores a pickled result and gives each caller a copy. `st.cache_resource` stores one object that all
sessions share. Project rule: every database read uses `st.cache_data` with an explicit TTL.

## The Pattern

```python
from datetime import date

import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine

from src import db, queries


@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    """One pooled engine per server process, shared by all sessions."""
    return db.create_db_engine()


@st.cache_data(ttl="5m", max_entries=256, show_spinner="Consultando o banco...")
def load_daily_revenue(
    start: date, end: date, states: tuple[str, ...]
) -> pd.DataFrame:
    """Each distinct argument set is one cache entry, expiring after 5 minutes."""
    return queries.daily_revenue(get_engine(), start, end, states)
```

## Quick Reference

| Aspect | `st.cache_data` | `st.cache_resource` |
|--------|-----------------|---------------------|
| Stores | Pickled return value | The object itself |
| Each call gets | Its own copy | The same shared object |
| Return must be | Serializable | Thread-safe |
| Mutation by callers | Safe | Visible to everyone |
| Use for | DataFrames, lists, dicts | Engines, pools, clients |

| Parameter | Default | Use |
|-----------|---------|-----|
| `ttl` | `None` (never expires) | Always set it for database reads |
| `max_entries` | `None` (unbounded) | Limit memory; filters multiply entries |
| `show_spinner` | `True` | Bool or custom text |
| `persist` | `None` | `"disk"`; makes `ttl` ignored |
| `scope` | `"global"` | `"session"` drops entries on disconnect |
| `refresh_mode` | `"foreground"` | `"background"` serves the expired value while refreshing |
| `hash_funcs` | `None` | Custom hashers for unhashable arguments |

## Cache Keys and Unhashable Arguments

Arguments form the key. A leading underscore excludes a parameter from hashing, so `_engine` skips
the engine, but then it cannot distinguish two databases. Prefer calling `get_engine()` inside the
cached function. Normalize filters before calling so the same selection hits the same entry:

```python
states = tuple(sorted(selected_states))  # ["RJ", "SP"] and ["SP", "RJ"] share an entry
```

## Clearing

| Call | Effect |
|------|--------|
| `load_daily_revenue.clear()` | All entries of that function |
| `load_daily_revenue.clear(start, end, states)` | Only that entry |
| `st.cache_data.clear()` | All data caches, for every function |

Filter options change rarely, while orders keep arriving from ShadowTraffic. Use a longer TTL such as
`"1h"` for option lists and a short one such as `"5m"` for KPIs.

## Common Mistakes

### Wrong

```python
@st.cache_resource
def load_orders():                     # A shared, mutable DataFrame
    return pd.read_sql(SQL, engine)

@st.cache_data                         # No TTL: stale until the server restarts
def load_kpis():
    ...

@st.cache_data(ttl="5m")
def load(conn, start):                 # A connection is not hashable
    ...
```

### Correct

```python
@st.cache_data(ttl="5m")
def load_orders(start: date, end: date) -> pd.DataFrame:
    return queries.orders(get_engine(), start, end)
```

## Related

- [Connections](../concepts/connections.md)
- [Data Access Layer](../patterns/data-access-layer.md)
- [Error and Empty States](../patterns/error-empty-states.md)
