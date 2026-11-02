# Sidebar Filters

> **Purpose**: Render one set of sidebar filters on every page and keep the selection across page changes
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## When to Use

- Filters shared by several pages: period, state, category, segment
- Apps built on the `pages/` directory, where the sidebar must be drawn by each page
- Passing filter values into cached loaders

## Implementation

```python
# app/components/filters.py
from dataclasses import dataclass
from datetime import date, timedelta

import streamlit as st

from data import load_filter_options

DEFAULT_WINDOW_DAYS = 30
FILTER_KEYS = ("filter_period", "filter_states", "filter_segments")
SEGMENT_LABELS = {"premium": "Premium", "standard": "Padrão", "basic": "Básico"}


@dataclass(frozen=True)
class Filters:
    start: date
    end: date
    states: tuple[str, ...]
    segments: tuple[str, ...]


def reset_filters() -> None:
    for key in FILTER_KEYS:
        if key in st.session_state:
            del st.session_state[key]


def render_sidebar_filters() -> Filters:
    options = load_filter_options()
    today = date.today()
    default_period = (today - timedelta(days=DEFAULT_WINDOW_DAYS), today)

    with st.sidebar:
        st.header("Filtros")
        period = st.date_input(
            "Período",
            value=default_period,
            format="DD/MM/YYYY",
            key="filter_period",
            persist_state="session",
        )
        states = st.multiselect(
            "Estados",
            options=options["states"],
            placeholder="Todos",
            key="filter_states",
            persist_state="session",
        )
        segments = st.multiselect(
            "Segmentos",
            options=list(SEGMENT_LABELS),
            format_func=SEGMENT_LABELS.get,
            placeholder="Todos",
            key="filter_segments",
            persist_state="session",
        )
        st.button("Limpar filtros", on_click=reset_filters)

    # While the user picks a range, the widget holds fewer than two dates.
    if len(period) != 2:
        st.info("Selecione a data final do período.")
        st.stop()

    return Filters(
        start=period[0],
        end=period[1],
        states=tuple(sorted(states)),  # Sorted, so reordering reuses the cache
        segments=tuple(sorted(segments)),
    )
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `DEFAULT_WINDOW_DAYS` | `30` | Initial period |
| `persist_state` | `"session"` | Keeps values across page switches |
| `format` | `"DD/MM/YYYY"` | pt-BR display; also `.` or `-` as separators |
| `placeholder` | `"Todos"` | An empty selection means "no filter" |

## Behavior Notes

| Topic | Detail |
|-------|--------|
| Same widget on each page | Call the helper with the same arguments; the docs require identical widgets |
| Date limits | Default `min_value`/`max_value` span 10 years around the initial value |
| Changing `format` | Resets the widget even with a `key` |
| Default period | This repo anchors it on `MIN`/`MAX` of `created_at`, from a cached query |

Anchoring the default on the data: pass `max(created_at)` from a cached query instead of
`date.today()`, so the first screen is not empty.

## Alternative: Filters in a Router Entrypoint

The docs prefer widgets in an `st.navigation` entrypoint. They render once and keep their state,
because the entrypoint runs on every rerun. Use this if the app moves to `st.navigation`.

```python
# app/Home.py as a router
import streamlit as st

pg = st.navigation([st.Page("pages/overview.py", title="Visão geral"),
                    st.Page("pages/vendas.py", title="Vendas")])
st.sidebar.multiselect("Estados", options, key="filter_states")
pg.run()
```

Pages then read `st.session_state["filter_states"]`.

## Example Usage

```python
# app/pages/1_Vendas.py
filters = render_sidebar_filters()
daily = load_daily_revenue(filters.start, filters.end, filters.states)
```

## See Also

- [Session State](../concepts/session-state.md)
- [Multipage Apps](../concepts/multipage-apps.md)
- [Data Access Layer](data-access-layer.md)
