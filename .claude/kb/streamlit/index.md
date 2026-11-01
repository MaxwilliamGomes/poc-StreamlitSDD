# Streamlit Knowledge Base

> **Purpose**: Build the ShopAgent e-commerce dashboard in Streamlit -- multipage app, cached Postgres reads, filters, KPI cards, layout, theming, failure states
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)
> **Version**: Streamlit 1.66.0 docs (PyPI latest at validation: 1.66.1; requires Python >= 3.11)

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/multipage-apps.md](concepts/multipage-apps.md) | `app/Home.py` + `app/pages/`, labels, order, importing `src/` |
| [concepts/caching.md](concepts/caching.md) | `st.cache_data` with explicit TTL vs `st.cache_resource` |
| [concepts/connections.md](concepts/connections.md) | `st.connection` vs SQLAlchemy engine vs raw psycopg2 |
| [concepts/session-state.md](concepts/session-state.md) | Rerun model, widget keys, keeping values across pages |
| [concepts/layout.md](concepts/layout.md) | Columns, tabs, containers, wide page config |
| [concepts/theming.md](concepts/theming.md) | `.streamlit/config.toml` theme and client options |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/data-access-layer.md](patterns/data-access-layer.md) | Cached `app/data.py` over framework-free `src/queries.py` |
| [patterns/sidebar-filters.md](patterns/sidebar-filters.md) | Shared sidebar filters that survive page changes |
| [patterns/kpi-cards.md](patterns/kpi-cards.md) | KPI row with `st.metric` and pt-BR values |
| [patterns/error-empty-states.md](patterns/error-empty-states.md) | Database failures, empty results, partial page rendering |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Fast lookup tables

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Rerun model** | Every interaction reruns the page script top to bottom; caches make that cheap |
| **Two caches** | `st.cache_data` copies serializable results; `st.cache_resource` shares one object |
| **Framework-free queries** | `src/` never imports Streamlit, so a future agent can reuse the queries |
| **Explicit TTL** | Every database read declares how stale it may be |
| **Formatted strings** | Streamlit has no fixed pt-BR formatter, so values are formatted in Python |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/multipage-apps.md, concepts/layout.md, patterns/kpi-cards.md |
| **Intermediate** | concepts/caching.md, concepts/connections.md, patterns/data-access-layer.md |
| **Advanced** | concepts/session-state.md, patterns/sidebar-filters.md, patterns/error-empty-states.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| python-developer | patterns/data-access-layer.md, patterns/sidebar-filters.md, patterns/kpi-cards.md | Build dashboard pages and the cached data layer |
| code-reviewer | concepts/caching.md, patterns/error-empty-states.md | Check TTLs, SQL placement, failure handling |

---

## Related Domains

| Domain | Use |
|--------|-----|
| [plotly](../plotly/index.md) | Charts rendered through `st.plotly_chart` |
| [pandas](../pandas/index.md) | `read_sql`, dtypes, aggregation, pt-BR formatters |
