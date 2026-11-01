# Time Resampling

> **Purpose**: Bucket orders by hour, day, week, or month and fill gaps for charts
> **Confidence**: 0.95
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; behavior run on local pandas 2.2.3)

## Overview

`DataFrame.resample` groups a datetime index or column into calendar bins. Unlike `groupby`, it emits
bins with no rows, so a day with no sales appears. Use it for detail-level rows. When SQL has already
aggregated by day, fill the missing days with `reindex`.

## The Pattern

```python
import pandas as pd


def revenue_series(orders: pd.DataFrame, rule: str = "D") -> pd.DataFrame:
    """Resample raw orders with tz-aware `created_at`, `order_id`, `total`."""
    return (
        orders.resample(rule, on="created_at")
        .agg(pedidos=("order_id", "size"), faturamento=("total", "sum"))
        .rename_axis("periodo")
        .reset_index()
        .assign(periodo=lambda frame: frame["periodo"].dt.tz_localize(None))
    )


def fill_missing_days(daily: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Add zero rows to a frame already aggregated by day in SQL."""
    calendar = pd.date_range(start, end, freq="D", name="dia")
    return (
        daily.assign(dia=pd.to_datetime(daily["dia"]))
        .set_index("dia")
        .reindex(calendar, fill_value=0)
        .reset_index()
    )


def with_moving_average(daily: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    return daily.assign(
        media_7d=daily["faturamento"].rolling(window, min_periods=1).mean()
    )
```

## Quick Reference

| Rule | Bin | Default closed/label |
|------|-----|----------------------|
| `"min"`, `"h"` | Minute, hour | left / left |
| `"D"` | Day | left / left |
| `"W"` | Week ending Sunday | right / right |
| `"MS"` | Month, labeled by first day | left / left |
| `"ME"` | Month, labeled by last day | right / right |
| `"QE"` | Quarter, labeled by last day | right / right |

| Parameter | Default | Notes |
|-----------|---------|-------|
| `on` | `None` | Datetime column instead of the index |
| `closed` | See above | Side of the bin included |
| `label` | See above | Which edge names the bin |
| `origin` | `"start_day"` | Only affects fixed frequencies |
| `group_keys` | `False` | Only relevant to `.apply()` |

## Which Monthly Rule

Use `"MS"` for charts. A label like `2026-04-01` works directly with `tickformat="%b/%Y"`, whereas `"ME"`
labels the same bin `2026-04-30`.

## Empty Bins

| Aggregation | Empty bin gives | Use for |
|-------------|-----------------|---------|
| `.sum()` | `0` | Revenue, order counts |
| `.sum(min_count=1)` | `NaN` | Unknown instead of zero |
| `.size()` | `0` | Counts |
| `.mean()` | `NaN` | Ticket: no orders means no ticket |

`resample` covers only the range between the first and last row. To show days before the first or after
the last order, use `reindex` with the selected period.

## Weeks Starting on Monday

The default `"W"` ends on Sunday and labels by that Sunday. To label each week by its Monday, use:

```python
orders.resample("W-MON", on="created_at", closed="left", label="left")["total"].sum()
```

## Time Zones

Resample after converting to local time. Otherwise a day bin is a UTC day, which starts at 21:00 in
Brasília. On tz-aware data, `"D"` bins follow local calendar days.

## Removed Aliases

pandas 3.0 enforced the renames `M` to `ME`, `Q` to `QE`, and `Y` to `YE` for offsets. Period aliases
differ and keep `M`, `Q`, `Y`. `H`, `T`, and `S` were replaced by `h`, `min`, and `s`.

## Common Mistakes

### Wrong

```python
orders.resample("M", on="created_at")["total"].sum()     # Removed alias
orders.groupby(orders["created_at"].dt.date)["total"].sum()  # Missing days vanish
utc_orders.resample("D", on="created_at")["total"].sum() # UTC day boundaries
```

### Correct

```python
local = orders.assign(created_at=normalize_created_at(orders["created_at"]))
local.resample("MS", on="created_at")["total"].sum()
```

## Related

- [Epoch Datetimes](../concepts/epoch-datetimes.md)
- [SQL vs pandas](../concepts/sql-vs-pandas.md)
- [Time Series Chart](../../plotly/patterns/time-series-chart.md)
