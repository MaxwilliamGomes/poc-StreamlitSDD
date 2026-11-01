# Session State

> **Purpose**: Hold per-user values across reruns and keep filter values across pages
> **Confidence**: 0.95
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## Overview

`st.session_state` is a per-session key-value store that survives reruns. A widget with a `key` is
stored under that key automatically. State belongs to the browser connection, so reloading the tab
resets it. At the end of a run, Streamlit deletes data for widgets that were not rendered, which
includes widgets on other pages.

## The Pattern

```python
import streamlit as st

STATE_DEFAULTS = {"granularity": "D"}

for key, value in STATE_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_filters() -> None:
    """Callbacks run before the script body, so widgets are not yet rendered."""
    for key in ("filter_period", "filter_states"):
        if key in st.session_state:
            del st.session_state[key]


st.sidebar.segmented_control(
    "Granularidade",
    options=["D", "W", "MS"],
    format_func={"D": "Dia", "W": "Semana", "MS": "Mês"}.get,
    key="granularity",
)
st.sidebar.button("Limpar filtros", on_click=reset_filters)

# segmented_control returns None once the user deselects the active option
granularity = st.session_state["granularity"] or "D"
```

## Quick Reference

| Input | Output | Notes |
|-------|--------|-------|
| `st.session_state["k"]` | Value | Raises if `k` was never set |
| `st.session_state.get("k", d)` | Value or `d` | Safe read |
| `"k" in st.session_state` | `bool` | Initialize guard |
| `del st.session_state["k"]` | Removes key | Inside a callback for widget keys |
| `st.widget(..., key="k")` | Value at `session_state["k"]` | Pages read it directly |
| `on_change=fn, args=(...)` | Runs before the rerun | Args are captured at widget creation |

## `persist_state`

| Value | Keeps the value when |
|-------|----------------------|
| `None` (default) | Only while the widget renders |
| `"page"` | Hidden on the same page; lost on page switch |
| `"session"` | For the whole session, including page switches |

`persist_state` requires `key`, and it is not available on buttons, file or media inputs,
`st.chat_input`, or `st.data_editor`. The docs say `"session"` also works for identical widgets with
the same key on multiple pages, which suits a shared filter helper. If `bind="query-params"` is also
set, the binding takes precedence.

## `bind="query-params"`

The widget syncs with a URL parameter named after `key`, so a filtered view can be shared as a link.
The parameter is dropped when the value equals the default, and invalid values are ignored. A bound
parameter can only be changed through `st.session_state`, not `st.query_params`.

## Restrictions

| Rule | Consequence |
|------|-------------|
| Cannot set a widget's value after it renders | `StreamlitAPIException` |
| Setting state and passing `value` together | Discouraged, logs a warning |
| Button-like widgets | State cannot be set through Session State |
| Forms | Only `st.form_submit_button` can have a callback |

## Common Mistakes

### Wrong

```python
states = st.multiselect("Estados", options, key="filter_states")
if st.button("Limpar"):
    st.session_state["filter_states"] = []  # Widget already rendered: raises
```

### Correct

```python
def clear_states() -> None:
    st.session_state["filter_states"] = []

states = st.multiselect("Estados", options, key="filter_states")
st.button("Limpar", on_click=clear_states)
```

## Related

- [Multipage Apps](../concepts/multipage-apps.md)
- [Sidebar Filters](../patterns/sidebar-filters.md)
