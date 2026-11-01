# Category Breakdown

> **Purpose**: Show parts of a whole -- status, payment, category hierarchy, and two-way heatmaps
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## When to Use

- Status or payment mix, with five parts or fewer
- Revenue by category and brand
- Comparing two dimensions, such as state and category

## Implementation

```python
# app/charts.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from charts_base import apply_dashboard_layout

STATUS_ORDER = ["Em processamento", "Enviado", "Entregue", "Cancelado"]
STATUS_COLORS = {
    "Em processamento": "#64748B",
    "Enviado": "#2563EB",
    "Entregue": "#16A34A",
    "Cancelado": "#DC2626",
}


def status_donut_chart(frame: pd.DataFrame) -> go.Figure:
    """Expect `status_label` and `pedidos`."""
    fig = px.pie(
        frame,
        names="status_label",
        values="pedidos",
        hole=0.55,
        color="status_label",
        color_discrete_map=STATUS_COLORS,
        category_orders={"status_label": STATUS_ORDER},
    )
    fig.update_traces(
        textinfo="percent",
        sort=False,  # Keep category_orders instead of sorting by size
        hovertemplate="%{label}<br>%{value:,d} pedidos (%{percent})<extra></extra>",
    )
    return apply_dashboard_layout(fig, title="Pedidos por status")


def category_treemap_chart(frame: pd.DataFrame) -> go.Figure:
    """Expect `categoria`, `marca`, and `faturamento`, with no missing path values."""
    fig = px.treemap(
        frame,
        path=[px.Constant("Todas"), "categoria", "marca"],
        values="faturamento",
    )
    fig.update_traces(
        root_color="rgba(0,0,0,0)",
        textinfo="label+percent root",
        hovertemplate="%{label}<br>R$ %{value:,.2f}<extra></extra>",
    )
    return apply_dashboard_layout(fig, title="Faturamento por categoria e marca")


def state_category_heatmap_chart(pivot: pd.DataFrame) -> go.Figure:
    """Expect a pivot: states on the index, categories on the columns, revenue values."""
    fig = px.imshow(pivot, aspect="auto", text_auto=",.0f")
    fig.update_traces(
        hovertemplate=(
            "%{y} / %{x}<br>R$ %{z:,.2f}<extra></extra>"
        ),
    )
    fig.update_coloraxes(colorbar_title_text="R$", colorbar_tickformat=",.0f")
    return apply_dashboard_layout(fig, title="Faturamento por estado e categoria")
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `hole` | `0.55` | `px.pie` argument; fraction of the radius removed |
| `sort` | `False` | Trace attribute; `True` would reorder slices by size |
| `textinfo` | `"percent"` | Also `"label"`, `"value"`, `"percent+label"` |
| `path` | `[Constant, ...]` | Outer level first; do not combine with `ids` or `parents` |
| `root_color` | Transparent | Fits light and dark themes |
| `text_auto` | `",.0f"` | Numeric text format |
| `aspect` | `"auto"` | Fills the plot area with non-square cells |

Status colors carry meaning, so they are fixed in code. All other palettes come from the theme.

## Donut Limits

Use a donut when parts sum to a meaningful whole and there are at most about five. `status` (4 values)
and `payment` (3 values) qualify; `category` may not, depending on the data. `segment` is usually
better shown as a comparison of ticket values, not as shares.

## Preparing the Data

| Chart | pandas step |
|-------|-------------|
| Donut | `df.assign(status_label=df["status"].map(STATUS_LABELS))` |
| Treemap | `df.dropna(subset=["categoria", "marca"])` |
| Heatmap | `df.pivot_table(index=..., columns=..., values=..., aggfunc="sum", fill_value=0)` |

`products.brand` is nullable in `init.sql`, and a treemap `path` with missing values can fail. Replace
missing brands with a label such as `"Sem marca"` before charting.

## Example Usage

```python
# app/pages/1_Vendas.py
left, right = st.columns(2, gap="medium")
with left:
    st.plotly_chart(status_donut_chart(by_status), key="status", config=PLOTLY_CONFIG)
with right:
    st.plotly_chart(payment_donut_chart(by_payment), key="payment", config=PLOTLY_CONFIG)
```

## See Also

- [Chart Selection](../concepts/chart-selection.md)
- [Ranking Bar Chart](ranking-bar-chart.md)
- [KPI Aggregations](../../pandas/patterns/kpi-aggregations.md)
