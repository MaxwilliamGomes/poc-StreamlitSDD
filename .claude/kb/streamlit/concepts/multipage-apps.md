# Multipage Apps

> **Purpose**: Structure the dashboard as `app/Home.py` plus `app/pages/` and make `src/` importable
> **Confidence**: 0.95
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## Overview

The file passed to `streamlit run` is the entrypoint and homepage. Each `.py` file directly inside a
`pages/` folder next to it becomes a page; subfolders and non-Python files are ignored. Pages share
imported modules and `st.session_state`.

## The Pattern

```text
app/
  Home.py              # Entrypoint: "Home" (visão geral), always listed first
  data.py              # Cached data layer (importable: app/ is on sys.path)
  charts.py            # Plotly figure builders
  components/          # Shared UI, ignored as pages because it is a subfolder
    filters.py
  pages/
    1_Vendas.py        # Label "Vendas"
    2_Produtos.py      # Label "Produtos"
    3_Clientes.py      # Label "Clientes"
    4_Avaliações.py    # Label "Avaliações"
```

```python
# app/pages/1_Vendas.py
import streamlit as st

from components.filters import render_sidebar_filters
from data import load_daily_revenue

st.set_page_config(page_title="Vendas | ShopAgent", layout="wide")
st.title("Vendas")

filters = render_sidebar_filters()
daily = load_daily_revenue(filters.start, filters.end, filters.states)
```

```bash
# From the repository root
python -m streamlit run app/Home.py
```

## Import Path

Streamlit inserts only the entrypoint's folder into `sys.path` (`_fix_sys_path` in
`lib/streamlit/web/bootstrap.py`). So `from data import ...` works, but `from src import ...` does not
under a plain `streamlit run app/Home.py`.

| Launch | `app/` importable | Repo root importable |
|--------|-------------------|----------------------|
| `streamlit run app/Home.py` | Yes | No |
| `python -m streamlit run app/Home.py` (from root) | Yes | Yes, `-m` adds the working directory |
| `PYTHONPATH=. streamlit run app/Home.py` (bash) | Yes | Yes, the approach in Streamlit's docs |

## Quick Reference

| Input | Output | Notes |
|-------|--------|-------|
| `1_Vendas.py` | Label `Vendas`, sorted first | Numbered files sort before unnumbered ones |
| `03_x.py` and `3_x.py` | Same sort position | Numbers compare numerically |
| `123_hello_dear_world.py` | `hello dear world` | Underscores become spaces |
| `st.set_page_config(...)` | Applies to that page | May be called repeatedly; calls are additive |
| `st.switch_page("pages/1_Vendas.py")` | Navigates in code | Path is relative to the entrypoint |

## `pages/` vs `st.navigation`

| Aspect | `pages/` directory | `st.Page` + `st.navigation` |
|--------|--------------------|-----------------------------|
| Setup | Automatic | Router entrypoint, then `pg.run()` |
| Shared sidebar | Call a helper on each page | Render once in the entrypoint |
| Filters across pages | `persist_state="session"` | Entrypoint widgets, the docs' preferred option |
| Sections, top nav | No | `dict` of sections, `position="top"` |

This repo uses `st.navigation`: `app/Home.py` is the router, draws the filters once, and the overview
lives in `app/pages/visao_geral.py`. Calling `st.navigation` in any session makes Streamlit ignore `pages/` in all
sessions until the server restarts, so do not mix the two.

## Common Mistakes

### Wrong

```python
# app/pages/1_Vendas.py: hard-coded path hack and SQL inside the page
import sys
sys.path.append("C:/Users/PICHAU/Desktop/...")
df = pd.read_sql("SELECT ...", engine)
```

### Correct

```python
# Launch from the root; the page imports the cached layer only
from data import load_daily_revenue

df = load_daily_revenue(filters.start, filters.end, filters.states)
```

## Related

- [Session State](../concepts/session-state.md)
- [Layout](../concepts/layout.md)
- [Data Access Layer](../patterns/data-access-layer.md)
- [Sidebar Filters](../patterns/sidebar-filters.md)
