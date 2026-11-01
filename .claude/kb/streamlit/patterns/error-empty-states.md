# Error and Empty States

> **Purpose**: Show useful messages when Postgres fails or filters match nothing, without leaking details
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## When to Use

- Every page section that reads from the database
- Filter combinations that return zero rows
- Local development, where Docker may be down or the port taken

## Implementation

```python
# app/components/states.py
import logging
from collections.abc import Callable
from typing import ParamSpec

import pandas as pd
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)
P = ParamSpec("P")

# pandas wraps failures during execution; connection failures stay SQLAlchemy errors
DB_ERRORS = (SQLAlchemyError, pd.errors.DatabaseError)

MSG_DB_ERROR = "Não foi possível consultar o banco de dados. Tente novamente em instantes."
MSG_EMPTY = "Nenhum dado encontrado para os filtros selecionados."


def safe_load(
    loader: Callable[P, pd.DataFrame], *args: P.args, **kwargs: P.kwargs
) -> pd.DataFrame | None:
    """Return the DataFrame, or None after showing an error message."""
    try:
        return loader(*args, **kwargs)
    except DB_ERRORS:
        logger.exception("Database read failed: %s", getattr(loader, "__name__", loader))
        st.error(MSG_DB_ERROR, title="Erro de dados", icon=":material/error:")
        return None


def has_rows(frame: pd.DataFrame | None, message: str = MSG_EMPTY) -> bool:
    """Show the empty state and return False when there is nothing to draw."""
    if frame is None:
        return False  # safe_load already reported the failure
    if frame.empty:
        st.info(message, icon=":material/search_off:")
        return False
    return True
```

## Choosing the Scope of a Failure

| Situation | Handling |
|-----------|----------|
| The page cannot work without this data | Message, then `st.stop()` |
| One section of several failed | Message in that section; the rest keeps rendering |
| Range still being selected | `st.info`, then `st.stop()` |
| Zero rows after filtering | `st.info` in place of the chart |
| Zero rows in a KPI | Show `-`, not `R$ 0,00` when the value is unknown |

`st.stop()` ends the script immediately, so render the message first. Nothing below it runs, including
other sections.

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `DB_ERRORS` | `SQLAlchemyError`, `DatabaseError` | Errors treated as data failures |
| `client.showErrorDetails` | Set `"none"` for viewers | Hides uncaught tracebacks |
| Log level | `logger.exception` | Full details stay in server logs |

## Which Exception Arrives

| Failure | Raised as |
|---------|-----------|
| Server down, wrong port, bad password | `sqlalchemy.exc.OperationalError` |
| Bad SQL, missing column during execution | `pandas.errors.DatabaseError` (pandas 3.0+) |
| Missing env var in `src/db.py` | `KeyError`; a setup bug, so let it surface |

In pandas 3.x, connecting happens outside the wrapped `execute`, so both families must be caught.
Do not show `str(exc)` to viewers: pandas includes the full SQL text in its message.

## Example Usage

```python
# app/pages/1_Vendas.py
from components.states import has_rows, safe_load

daily = safe_load(load_daily_revenue, filters.start, filters.end, filters.states)
if has_rows(daily):
    st.plotly_chart(revenue_trend_chart(daily), key="trend")

top = safe_load(load_top_products, filters.start, filters.end, filters.states)
if has_rows(top, "Nenhum produto vendido neste período."):
    st.plotly_chart(top_products_chart(top), key="top_products")
```

## Status Elements

| API | Use |
|-----|-----|
| `st.error(body, *, icon, width, title)` | Failure |
| `st.warning(...)` | Degraded result, such as partial data |
| `st.info(...)` | Empty state or guidance |
| `st.spinner(text, *, show_time, width)` | Long operation outside a cached function |

`icon` accepts an emoji or `":material/icon_name:"`.

## See Also

- [Data Access Layer](data-access-layer.md)
- [Caching](../concepts/caching.md)
- [Theming](../concepts/theming.md)
