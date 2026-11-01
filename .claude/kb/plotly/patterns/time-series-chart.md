# Time Series Chart

> **Purpose**: Plot revenue over time with pt-BR dates, a moving average, and an optional second axis
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## When to Use

- Revenue or orders by day, week, or month
- Comparing a series with its moving average
- Relating revenue and orders when both really matter on one chart

## Implementation

```python
# app/charts.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from charts_base import apply_dashboard_layout, format_axis_brl

DATE_FORMATS = {
    "h": {"tick": "%d/%m %Hh", "hover": "%d/%m/%Y %H:%M"},
    "D": {"tick": "%d/%m", "hover": "%d/%m/%Y"},
    "W": {"tick": "%d/%m", "hover": "semana até %d/%m/%Y"},
    "MS": {"tick": "%b/%Y", "hover": "%B de %Y"},
}


def revenue_trend_chart(
    frame: pd.DataFrame, granularity: str = "D", title: str = "Faturamento"
) -> go.Figure:
    """Expect columns `periodo` (naive local datetime) and `faturamento`."""
    formats = DATE_FORMATS[granularity]
    fig = px.line(frame, x="periodo", y="faturamento", markers=True)
    fig.update_traces(
        hovertemplate=(
            f"%{{x|{formats['hover']}}}<br>R$ %{{y:,.2f}}<extra></extra>"
        ),
    )
    fig.update_xaxes(tickformat=formats["tick"])
    format_axis_brl(fig)
    return apply_dashboard_layout(fig, title=title, show_legend=False)


def revenue_with_moving_average_chart(frame: pd.DataFrame) -> go.Figure:
    """Expect `periodo`, `faturamento`, and `media_7d`."""
    fig = revenue_trend_chart(frame)
    fig.update_traces(name="Diário", showlegend=True)
    fig.add_trace(
        go.Scatter(
            x=frame["periodo"],
            y=frame["media_7d"],
            mode="lines",
            name="Média de 7 dias",
            hovertemplate="Média: R$ %{y:,.2f}<extra></extra>",
        )
    )
    return apply_dashboard_layout(fig, title="Faturamento", hovermode="x unified")


def revenue_and_orders_chart(frame: pd.DataFrame) -> go.Figure:
    """Dual axis, for when both measures must appear together."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=frame["periodo"],
            y=frame["faturamento"],
            name="Faturamento",
            hovertemplate="R$ %{y:,.2f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=frame["periodo"],
            y=frame["pedidos"],
            name="Pedidos",
            mode="lines+markers",
            hovertemplate="%{y:,d} pedidos<extra></extra>",
        ),
        secondary_y=True,
    )
    apply_dashboard_layout(fig, title="Faturamento e pedidos", hovermode="x unified")
    fig.update_yaxes(tickprefix="R$ ", tickformat=",.0f", secondary_y=False)
    fig.update_yaxes(tickformat=",d", showgrid=False, secondary_y=True)
    return fig
```

## Configuration

| Setting | Options | Description |
|---------|---------|-------------|
| `granularity` | `"h"`, `"D"`, `"W"`, `"MS"` | Same aliases as pandas resampling |
| `markers` | `True` | Helps with sparse series; drop above about 90 points |
| `dtick` | `"M1"`, ms number | Fixed tick interval |
| `ticklabelmode` | `"period"` | Centers labels inside the period |
| `hovermode` | `"x unified"` | One hover box for all series |
| `rangeslider_visible` | `False` | Turn on for long histories |

## Date Axis Notes

| Topic | Detail |
|-------|--------|
| Axis type | Plotly detects dates from pandas date columns |
| Input | Naive local datetimes, gaps filled with zero in pandas |
| Zoom-dependent ticks | `tickformatstops` |
| Range buttons | `rangeselector` on the x axis |
| `tickformat` newline | `"%b\n%Y"` shows the second line only once per unique value |
| Months | Names need `config=PLOTLY_CONFIG` |

Plotly connects points, so a missing day reads as a straight line, not as zero. Reindex in pandas when
"no sales" is the truth: [Time Resampling](../../pandas/concepts/time-resampling.md).

## Example Usage

```python
# app/pages/1_Vendas.py
trend = with_moving_average(daily)  # Adds media_7d in pandas
st.plotly_chart(
    revenue_with_moving_average_chart(trend),
    key="vendas_trend",
    config=PLOTLY_CONFIG,
)
```

With today's roughly 8-minute dataset, use `granularity="h"` or add a minute format until dates are
spread out.

## See Also

- [Shared Layout Helper](shared-layout-helper.md)
- [pt-BR Formatting](../concepts/pt-br-formatting.md)
- [Chart Selection](../concepts/chart-selection.md)
