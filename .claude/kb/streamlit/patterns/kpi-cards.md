# KPI Cards

> **Purpose**: Render a row of pt-BR KPI cards with `st.metric`, deltas, and optional sparklines
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## When to Use

- Headline numbers: revenue, orders, average ticket, cancellation rate
- Comparing the selected period with the previous one
- Showing a short trend inside a card

## Implementation

```python
# app/components/kpis.py
from dataclasses import dataclass

import streamlit as st

from src.formatting import format_brl, format_int, format_percent, format_signed_percent


@dataclass(frozen=True)
class Kpis:
    revenue: float
    orders: int
    average_ticket: float | None
    cancel_rate: float | None
    revenue_delta: float | None   # Fraction: 0.125 means +12,5%
    orders_delta: float | None
    daily_revenue: tuple[float, ...] = ()


def render_kpi_row(kpis: Kpis) -> None:
    revenue, orders, ticket, cancel = st.columns(4, gap="small")

    with revenue:
        st.metric(
            "Faturamento",
            format_brl(kpis.revenue),
            delta=format_signed_percent(kpis.revenue_delta),
            delta_description="vs. período anterior",
            chart_data=kpis.daily_revenue or None,
            chart_type="area",
            border=True,
        )
    with orders:
        st.metric(
            "Pedidos",
            format_int(kpis.orders),
            delta=format_signed_percent(kpis.orders_delta),
            delta_description="vs. período anterior",
            border=True,
        )
    with ticket:
        st.metric(
            "Ticket médio",
            format_brl(kpis.average_ticket),
            help="Faturamento dividido pelo número de pedidos não cancelados.",
            border=True,
        )
    with cancel:
        st.metric(
            "Cancelamentos",
            format_percent(kpis.cancel_rate),
            border=True,
        )
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `delta` | `None` | `None` hides the delta |
| `delta_color` | `"normal"` | `"inverse"` when a drop is good; `"off"`, or a named color |
| `delta_arrow` | `"auto"` | `"up"`, `"down"`, `"off"` |
| `delta_description` | `None` | Muted text beside the delta |
| `border` | `False` | Card outline |
| `chart_data` | `None` | Iterable of numbers for a sparkline |
| `chart_type` | `"line"` | `"line"`, `"area"`, `"bar"` |
| `format` | `None` | Numeric values only; has no fixed pt-BR option |
| `help` | `None` | Tooltip beside the label |

## Why Strings, Not `format=`

`st.metric(format=...)` formats numeric values only. Its presets include `"dollar"`, `"euro"`, and
`"yen"`, but no BRL. `"localized"` follows `navigator.languages`, the viewer's browser, so it cannot
guarantee pt-BR. A preformatted string always renders as written.

A string delta follows a sign rule: text starting with `-` shows as negative. So
`format_signed_percent` must emit a leading `+` or `-`. For cancellations, a rise is bad, so if that
card gets a delta, set `delta_color="inverse"`.

## Example Usage

```python
# app/Home.py
from components.kpis import Kpis, render_kpi_row

current = load_kpi_totals(filters.start, filters.end, filters.states)
previous = load_kpi_totals(*previous_period(filters.start, filters.end), filters.states)

render_kpi_row(
    Kpis(
        revenue=current.revenue,
        orders=current.orders,
        average_ticket=current.average_ticket,
        cancel_rate=current.cancel_rate,
        revenue_delta=safe_growth(current.revenue, previous.revenue),
        orders_delta=safe_growth(current.orders, previous.orders),
    )
)
```

`safe_growth` must return `None` on a zero base. The result then hides the delta instead of showing
infinity. Formatters and `safe_growth` are defined in
[pt-BR Display Formatting](../../pandas/patterns/ptbr-display-formatting.md).

## See Also

- [Layout](../concepts/layout.md)
- [KPI Aggregations](../../pandas/patterns/kpi-aggregations.md)
- [Error and Empty States](error-empty-states.md)
