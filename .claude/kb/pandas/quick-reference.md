# pandas Quick Reference

> Fast lookup tables. For code examples, see linked files.
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## read_sql (3.1.0)

| Argument | Default | Note |
|----------|---------|------|
| `sql` | Required | `text(...)` or a string |
| `con` | Required | SQLAlchemy engine/connection, ADBC, URI string, or sqlite3 |
| `params` | `None` | `:name` with `text()`; `%(name)s` with a plain string |
| `coerce_float` | `True` | Converts `Decimal` to float |
| `dtype` | `None` | Column dtypes, also applied to empty results |
| `parse_dates` | `None` | Avoid `format` on integer columns |
| `chunksize` | `None` | Rarely lowers peak memory without a server-side cursor |

## Conversions

| Input | Code | Result |
|-------|------|--------|
| `Decimal` in `object` | `s.astype("float64")` | `float64`, `None` becomes `NaN` |
| Epoch ms | `pd.to_datetime(s, unit="ms", utc=True)` | UTC-aware |
| `TIMESTAMPTZ` values | `pd.to_datetime(s, utc=True)` | UTC-aware |
| UTC to local | `s.dt.tz_convert("America/Sao_Paulo")` | Local-aware |
| Local to chart | `s.dt.tz_localize(None)` | Naive wall clock |
| `date` objects | `pd.to_datetime(s)` | `datetime64` |
| Nullable integer | `s.astype("Int64")` | Keeps `<NA>` |

## Offset Aliases

| Alias | Meaning | Removed alias |
|-------|---------|---------------|
| `h`, `min`, `s` | Hour, minute, second | |
| `D` | Calendar day | |
| `W` | Week ending Sunday (`W-SUN`) | |
| `MS` | Month start | |
| `ME` | Month end | `M` |
| `QE` | Quarter end | `Q` |
| `YE` | Year end | `Y` |

## Aggregation

| Need | Code |
|------|------|
| Named KPIs | `df.groupby("estado", as_index=False).agg(pedidos=("order_id", "count"))` |
| Share of total | `df["faturamento"] / df["faturamento"].sum()` |
| Top N | `df.nlargest(10, "faturamento")` |
| Two-way table | `df.pivot_table(index=..., columns=..., values=..., aggfunc="sum", fill_value=0)` |
| Moving average | `s.rolling(7, min_periods=1).mean()` |

## Decision Matrix

| Use Case | Choose |
|----------|--------|
| Totals, top N, group sums | SQL |
| Fill missing days | pandas `reindex` |
| Rolling means | pandas, on the aggregated series |
| Currency labels | `src/formatting.py` |
| Formatted table | `df.style.format(...)` in `st.dataframe` |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| f-string values into SQL | `params={"status": status}` |
| Pass a raw psycopg2 connection to `read_sql` | Pass a SQLAlchemy engine |
| `:states::text[]` in `text()` | `CAST(:states AS text[])` |
| `resample("M")`, `"H"`, `"T"` | `"ME"`, `"h"`, `"min"` |
| `parse_dates={"created_at": {"format": ...}}` on integers | `pd.to_datetime` after reading |
| `s.pct_change()` shown directly | `safe_growth`; a zero base gives `inf` |
| `locale.setlocale` | String formatters |
| `Styler.format("{:.2f}", thousands=".")` | `precision=2` or a function |
| `df["a"]["b"] = 1` | `df.loc[:, ...]` or `df.assign(...)` |
| Average of averages | `sum(total) / sum(count)` |

## Related Documentation

| Topic | Path |
|-------|------|
| Loading data | `concepts/read-sql.md` |
| Epoch timestamps | `concepts/epoch-datetimes.md` |
| Formatters | `patterns/ptbr-display-formatting.md` |
| Full Index | `index.md` |
