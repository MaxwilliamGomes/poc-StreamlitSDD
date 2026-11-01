# Shared Layout Helper

> **Purpose**: Give every chart the same layout, pt-BR separators, hover text, and toolbar
> **MCP Validated**: 2026-11-01 (official docs and Streamlit/plotly.js source; not rendered in a browser)

## When to Use

- Every figure the dashboard renders
- Changing chart defaults in one place
- Testing chart functions without a running Streamlit app

## Implementation

```python
# app/charts_base.py
from typing import Any

import plotly.graph_objects as go

CHART_HEIGHT = 380
SEPARATORS_PT_BR = ",."  # Decimal first, thousands second

PT_BR_FORMAT: dict[str, Any] = {
    "days": ["Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira",
             "Quinta-feira", "Sexta-feira", "Sábado"],
    "shortDays": ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"],
    "months": ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
               "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
    "shortMonths": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                    "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
    "date": "%d/%m/%Y",
    "decimal": ",",
    "thousands": ".",
}

PLOTLY_CONFIG: dict[str, Any] = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["select2d", "lasso2d"],
    "locale": "pt-BR",
    "locales": {"pt-BR": {"format": PT_BR_FORMAT}},
}


def apply_dashboard_layout(
    fig: go.Figure,
    *,
    title: str | None = None,
    height: int = CHART_HEIGHT,
    hovermode: str = "closest",
    show_legend: bool = True,
) -> go.Figure:
    """Apply shared settings directly on fig.layout, where the theme keeps them."""
    fig.update_layout(
        title_text=title,
        height=height,
        separators=SEPARATORS_PT_BR,
        hovermode=hovermode,
        showlegend=show_legend,
        legend_title_text=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(t=56 if title else 24, r=8, b=8, l=8),
    )
    fig.update_xaxes(title_text=None)
    fig.update_yaxes(title_text=None)
    return fig


def format_axis_brl(fig: go.Figure, axis: str = "y") -> go.Figure:
    """Format one value axis as whole reais."""
    update = fig.update_yaxes if axis == "y" else fig.update_xaxes
    update(tickprefix="R$ ", tickformat=",.0f")
    return fig
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `CHART_HEIGHT` | `380` | Height of standard charts |
| `SEPARATORS_PT_BR` | `",."` | Must be set per figure, on `layout` |
| `hovermode` | `"closest"` | Use `"x unified"` for several series over time |
| `show_legend` | `True` | Turn off for single-series charts |
| `displaylogo` | `False` | Streamlit already defaults this to off |
| `modeBarButtonsToRemove` | select tools | Remove them unless the chart uses `on_select` |

## Design Notes

| Decision | Reason |
|----------|--------|
| Function, not a Plotly template | `theme="streamlit"` rewrites template layout values in the browser |
| No colors here | Palette comes from `theme.chartCategoricalColors` |
| Axis titles removed | The chart title and hover text name the measure |
| No Streamlit import | Figures can be tested with plain pytest |
| Legend above the plot | Avoids overlap with long category labels |

A Plotly template remains the right tool only with `theme=None`:

```python
import plotly.graph_objects as go
import plotly.io as pio

pio.templates["shopagent"] = go.layout.Template(layout=dict(separators=",."))
fig = px.bar(df, x="estado", y="faturamento", template="plotly+shopagent")
```

`"plotly+shopagent"` merges both templates. A custom template alone replaces the base look.

## Example Usage

```python
# app/charts.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from charts_base import apply_dashboard_layout, format_axis_brl


def revenue_by_month_chart(monthly: pd.DataFrame) -> go.Figure:
    fig = px.bar(monthly, x="mes", y="faturamento")
    fig.update_traces(hovertemplate="%{x|%b/%Y}<br>R$ %{y:,.2f}<extra></extra>")
    fig.update_xaxes(tickformat="%b/%Y", dtick="M1")
    format_axis_brl(fig)
    return apply_dashboard_layout(fig, title="Faturamento mensal", show_legend=False)
```

```python
# app/pages/1_Vendas.py
from charts import revenue_by_month_chart
from charts_base import PLOTLY_CONFIG

st.plotly_chart(revenue_by_month_chart(monthly), key="monthly", config=PLOTLY_CONFIG)
```

```python
# tests/test_charts.py
def test_layout_uses_pt_br_separators() -> None:
    fig = apply_dashboard_layout(go.Figure())
    assert fig.layout.separators == ",."
```

## See Also

- [pt-BR Formatting](../concepts/pt-br-formatting.md)
- [Streamlit Integration](../concepts/streamlit-integration.md)
- [Time Series Chart](time-series-chart.md)
