# pandas Knowledge Base

> **Purpose**: Load, type, aggregate, and format Postgres data for the ShopAgent dashboard
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)
> **Version**: pandas 3.1.0 docs (requires Python >= 3.11; Streamlit 1.66 allows `pandas>=1.5.3,<4`)

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/read-sql.md](concepts/read-sql.md) | `read_sql` with SQLAlchemy or psycopg2, binds, errors |
| [concepts/dtypes.md](concepts/dtypes.md) | Decimal to float, NULLs, empty results, pandas 3 strings |
| [concepts/epoch-datetimes.md](concepts/epoch-datetimes.md) | `orders.created_at` as epoch ms or `TIMESTAMPTZ`, time zones |
| [concepts/time-resampling.md](concepts/time-resampling.md) | `resample`, offset aliases, gap filling, rolling averages |
| [concepts/sql-vs-pandas.md](concepts/sql-vs-pandas.md) | When to aggregate in SQL and when in pandas |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/parameterized-queries.md](patterns/parameterized-queries.md) | Dates, lists, limits, and safe dynamic SQL |
| [patterns/kpi-aggregations.md](patterns/kpi-aggregations.md) | KPI totals, `groupby`, `pivot_table`, shares |
| [patterns/ptbr-display-formatting.md](patterns/ptbr-display-formatting.md) | `R$`, percent, dates, tables, safe growth |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Fast lookup tables

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Binds, never interpolation** | Filter values travel through `params` |
| **Types at the boundary** | Queries return float, int, and datetime columns, even when empty |
| **One time zone** | Stored in UTC or epoch, shown in `America/Sao_Paulo` |
| **SQL first** | Postgres aggregates; pandas does the last-mile reshaping |
| **Format last** | Numbers stay numeric until the moment they are displayed |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/read-sql.md, concepts/dtypes.md, patterns/ptbr-display-formatting.md |
| **Intermediate** | concepts/epoch-datetimes.md, concepts/sql-vs-pandas.md, patterns/parameterized-queries.md |
| **Advanced** | concepts/time-resampling.md, patterns/kpi-aggregations.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| python-developer | patterns/parameterized-queries.md, patterns/kpi-aggregations.md, patterns/ptbr-display-formatting.md | Write `src/queries.py` and formatters |
| code-reviewer | concepts/read-sql.md, concepts/epoch-datetimes.md | Check binds, dtypes, time zone handling |

---

## Related Domains

| Domain | Use |
|--------|-----|
| [streamlit](../streamlit/index.md) | Caching and displaying these DataFrames |
| [plotly](../plotly/index.md) | Charting aggregated frames |
| [supabase](../supabase/patterns/shopagent-ledger-queries.md) | Existing Ledger business queries |
