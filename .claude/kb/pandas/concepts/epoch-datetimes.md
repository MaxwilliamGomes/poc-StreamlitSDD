# Epoch Datetimes

> **Purpose**: Handle `orders.created_at` whether it is `bigint` epoch ms or `TIMESTAMPTZ`, in Brazilian time
> **Confidence**: 0.95
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; behavior run on local pandas 2.2.3)

## Overview

Since 2026-11-02, `src/prepare_data.py` gives `orders.created_at` the `TIMESTAMPTZ` type. The `bigint`
epoch form survives only in `raw_orders`. Check the real type first, because it changes both the
filter and the conversion. Store and compare in UTC or epoch, convert to `America/Sao_Paulo` for grouping, and drop the
time zone only just before charting.

## The Pattern

```sql
-- Run first: the answer decides which SQL applies
SELECT data_type
FROM information_schema.columns
WHERE table_name = 'orders' AND column_name = 'created_at';
```

```python
# src/time_range.py
from datetime import date, timedelta

import pandas as pd
from pandas.api.types import is_numeric_dtype

APP_TIMEZONE = "America/Sao_Paulo"


def normalize_created_at(values: pd.Series) -> pd.Series:
    """Return local, tz-aware datetimes from epoch ms or TIMESTAMPTZ values."""
    if is_numeric_dtype(values):
        parsed = pd.to_datetime(values, unit="ms", utc=True)
    else:
        parsed = pd.to_datetime(values, utc=True)
    return parsed.dt.tz_convert(APP_TIMEZONE)


def to_chart_time(values: pd.Series) -> pd.Series:
    """Drop the zone, keeping wall-clock time, so Plotly shows local time."""
    return values.dt.tz_localize(None)


def to_epoch_ms_bounds(start: date, end: date) -> tuple[int, int]:
    """Local inclusive dates to a half-open [start, end + 1 day) epoch ms range."""
    lower = pd.Timestamp(start, tz=APP_TIMEZONE)
    upper = pd.Timestamp(end, tz=APP_TIMEZONE) + pd.Timedelta(days=1)
    return int(lower.timestamp() * 1000), int(upper.timestamp() * 1000)


def previous_period(start: date, end: date) -> tuple[date, date]:
    """The same-length window ending the day before `start`."""
    length = (end - start).days + 1
    previous_end = start - timedelta(days=1)
    return previous_end - timedelta(days=length - 1), previous_end
```

## Quick Reference

| Input | Output | Notes |
|-------|--------|-------|
| `pd.to_datetime(s, unit="ms", utc=True)` | `datetime64[..., UTC]` | Epoch ms to aware UTC |
| `s.dt.tz_convert(APP_TIMEZONE)` | Same instant, local zone | For aware data |
| `s.dt.tz_localize(None)` | Naive local wall clock | Before Plotly |
| `to_epoch_ms_bounds(date(2026,4,1), date(2026,4,30))` | `(1775012400000, 1777604400000)` | April 1 to May 1, -03:00 |

## Filters and Buckets by Column Type

| Task | `bigint` epoch ms | `TIMESTAMPTZ` |
|------|-------------------|---------------|
| Lower bound | `created_at >= :start_ms` | `created_at >= :start_at` |
| Upper bound | `created_at < :end_ms` | `created_at < :end_at` |
| Bound values | Integers | Aware `datetime` |
| To timestamp | `to_timestamp(created_at / 1000.0)` | `created_at` |
| Local day | `(to_timestamp(created_at / 1000.0) AT TIME ZONE 'America/Sao_Paulo')::date` | `(created_at AT TIME ZONE 'America/Sao_Paulo')::date` |

`to_timestamp` takes epoch seconds, so divide by `1000.0`. `AT TIME ZONE` on a `timestamptz` returns a
`timestamp` as it would appear in that zone. Compare the raw column against bounds, so the
`idx_orders_created_at` index can be used.

## pandas 3 Notes

| Topic | Detail |
|-------|--------|
| Resolution | pandas 3.1 numeric input defaults to microseconds, or ns if needed |
| `astype("int64")` on datetimes | Units follow the resolution; use `.dt.as_unit("ms")` first |
| `parse_dates` with `format` on ints | Deprecated in 3.1, so convert after reading |
| `.values` on tz-aware data | Deprecated in 3.1; use `.array` |
| `datetime.date` in `DatetimeIndex` lookups | Implicit conversion deprecated; use `to_datetime` |
| `Series.dt.dayofweek` | Deprecated; use `day_of_week` |
| Windows time zones | Needs `tzdata`, which pandas requires on Windows |

## Common Mistakes

### Wrong

```python
pd.to_datetime(frame["created_at"])               # Integers read as nanoseconds: year 1970
pd.to_datetime(frame["created_at"], unit="s")     # Milliseconds read as seconds: out of range
frame["dia"] = frame["created_at"].dt.date        # UTC date; evening orders land on the next day
```

```sql
WHERE to_timestamp(created_at / 1000.0) >= :start  -- A function on the column skips the index
```

### Correct

```python
local = normalize_created_at(frame["created_at"])
frame = frame.assign(created_at=local, dia=local.dt.normalize())
```

```sql
WHERE created_at >= :start_ms AND created_at < :end_ms
```

## Related

- [Time Resampling](../concepts/time-resampling.md)
- [Parameterized Queries](../patterns/parameterized-queries.md)
- [Time Series Chart](../../plotly/patterns/time-series-chart.md)
