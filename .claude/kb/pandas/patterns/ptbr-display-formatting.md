# pt-BR Display Formatting

> **Purpose**: Format currency, numbers, percentages, and dates for display without changing the data
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; formatters run on local pandas 2.2.3)

## When to Use

- KPI values in `st.metric`
- Tables in `st.dataframe`
- Any text shown to users that contains a number or a date

## Implementation

```python
# src/formatting.py -- no Streamlit import, safe to reuse and unit test
from datetime import date, datetime

import pandas as pd

EMPTY = "-"
SWAP_SEPARATORS = str.maketrans(",.", ".,")
MONTHS = ("jan", "fev", "mar", "abr", "mai", "jun",
          "jul", "ago", "set", "out", "nov", "dez")


def _is_missing(value: object) -> bool:
    return value is None or pd.isna(value)


def format_number(value: float | None, decimals: int = 0) -> str:
    if _is_missing(value):
        return EMPTY
    return f"{value:,.{decimals}f}".translate(SWAP_SEPARATORS)


def format_int(value: int | None) -> str:
    return format_number(value, 0)


def format_brl(value: float | None, decimals: int = 2) -> str:
    if _is_missing(value):
        return EMPTY
    sign = "-" if value < 0 else ""
    return f"{sign}R$ {format_number(abs(value), decimals)}"


def format_percent(fraction: float | None, decimals: int = 1) -> str:
    """Format a 0-1 fraction: 0.125 becomes 12,5%."""
    if _is_missing(fraction):
        return EMPTY
    return f"{format_number(fraction * 100, decimals)}%"


def format_signed_percent(fraction: float | None, decimals: int = 1) -> str | None:
    """Delta text for st.metric; None hides the delta."""
    if _is_missing(fraction):
        return None
    sign = "+" if fraction >= 0 else "-"
    return f"{sign}{format_percent(abs(fraction), decimals)}"


def format_date(value: date | datetime | None) -> str:
    if _is_missing(value):
        return EMPTY
    return value.strftime("%d/%m/%Y")


def format_month(value: date | datetime | None) -> str:
    """Independent of the process locale: Abr/2026."""
    if _is_missing(value):
        return EMPTY
    return f"{MONTHS[value.month - 1].capitalize()}/{value.year}"


def safe_growth(current: float, previous: float | None) -> float | None:
    """Return a fraction, or None when there is no base to compare with."""
    if not previous:
        return None
    return (current - previous) / previous
```

## Configuration

| Function | Input | Output |
|----------|-------|--------|
| `format_brl(1234567.891)` | `float` | `R$ 1.234.567,89` |
| `format_brl(-5.5)` | `float` | `-R$ 5,50` |
| `format_brl(None)` | `None` or `NaN` | `-` |
| `format_int(1234)` | `int` | `1.234` |
| `format_percent(0.125)` | Fraction | `12,5%` |
| `format_signed_percent(-0.05)` | Fraction | `-5,0%` |
| `format_date(date(2026, 3, 15))` | Date | `15/03/2026` |
| `format_month(date(2026, 4, 1))` | Date | `Abr/2026` |
| `safe_growth(120, 100)` | Numbers | `0.2` |
| `safe_growth(1, 0)` | Zero base | `None` |

## Tables

Use a Styler, which sends formatted text while keeping the original numeric column. Do not replace the
data with strings.

```python
import streamlit as st

from src.formatting import format_brl, format_date, format_int, format_percent

styled = summary.style.format(
    {
        "dia": format_date,
        "pedidos": format_int,
        "faturamento": format_brl,
        "participacao": format_percent,
    },
    na_rep="-",
)
st.dataframe(
    styled,
    hide_index=True,
    column_config={
        "dia": "Dia",
        "pedidos": "Pedidos",
        "faturamento": "Faturamento",
        "participacao": "Participação",
    },
)
```

Styler needs `jinja2`, so declare it in the requirements when the dashboard stack is pinned.
`column_config` values here are plain labels. A `NumberColumn(format=...)` on the same column would take
precedence over the Styler. Styling is not supported on lazily loaded rows, so leave `lazy` unset.

## Styler Pitfalls

| Call | Result (observed) |
|------|-------------------|
| `format(precision=2, thousands=".", decimal=",")` | `1.234.567,50` |
| `format("{:.2f}", thousands=".", decimal=",")` | `1234567,50`; thousands are lost |
| `format(callable)` | Your function decides everything |

## Why Not `locale`

`locale.setlocale` is program-wide and "not thread-safe on most systems". Streamlit serves sessions
from threads, so one call would affect everyone. `pt_BR` names also vary by OS. String formatters avoid
both problems, and `strftime("%b")` would depend on that same locale, which is why `MONTHS` is explicit.

## Where Each Format Lives

| Target | Tool |
|--------|------|
| KPI card | `format_brl`, passed as a string to `st.metric` |
| Table | `Styler.format` with the same functions |
| Chart | `separators=",."` and hover templates |
| Filter input | `st.date_input(format="DD/MM/YYYY")` |

## Example Usage

```python
from src.formatting import format_brl, format_signed_percent, safe_growth

delta = safe_growth(current.revenue, previous.revenue)
st.metric(
    "Faturamento",
    format_brl(current.revenue),
    delta=format_signed_percent(delta),
)
```

## See Also

- [KPI Aggregations](kpi-aggregations.md)
- [Streamlit KPI Cards](../../streamlit/patterns/kpi-cards.md)
- [Plotly pt-BR Formatting](../../plotly/concepts/pt-br-formatting.md)
