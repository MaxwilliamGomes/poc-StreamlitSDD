# Ranking Bar Chart

> **Purpose**: Show top products, states, or brands as sorted horizontal bars with pt-BR value labels
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## When to Use

- Top N rankings by revenue or orders
- Long category labels, such as product names
- More categories than a donut can carry

## Implementation

```python
# app/charts.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from charts_base import apply_dashboard_layout

ROW_HEIGHT = 34
MIN_HEIGHT = 240
HEADER_HEIGHT = 80


def ranking_chart(
    frame: pd.DataFrame,
    *,
    category: str,
    value: str = "faturamento",
    orders: str = "pedidos",
    title: str = "Ranking",
) -> go.Figure:
    """Expect one row per category, already limited to the top N."""
    fig = px.bar(
        frame,
        x=value,
        y=category,
        orientation="h",
        text=value,
        custom_data=[orders],
    )
    fig.update_traces(
        texttemplate="R$ %{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Faturamento: R$ %{x:,.2f}<br>"
            "Pedidos: %{customdata[0]:,d}"
            "<extra></extra>"
        ),
    )
    fig.update_yaxes(categoryorder="total ascending")  # Largest bar on top
    fig.update_xaxes(showticklabels=False, showgrid=False)

    height = max(MIN_HEIGHT, HEADER_HEIGHT + ROW_HEIGHT * len(frame))
    fig = apply_dashboard_layout(fig, title=title, height=height, show_legend=False)
    fig.update_layout(margin_r=72)  # Room for labels outside the bars
    return fig
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `orientation` | `"h"` | Needs a categorical `y` |
| `categoryorder` | `"total ascending"` | Horizontal charts draw the first category at the bottom |
| `textposition` | `"outside"` | Labels beyond the bar end |
| `cliponaxis` | `False` | Keeps outside labels from being cut |
| `ROW_HEIGHT` | `34` | Height follows the row count |
| `margin_r` | `72` | Space for the longest label |

`categoryorder` also accepts `"total descending"`, `"category ascending"`, `"category descending"`, and
`"array"` with `categoryarray`.

## Stacked and Grouped Variants

| Need | Call |
|------|------|
| Compare states by status | `px.bar(df, x="estado", y="pedidos", color="status", barmode="group")` |
| Composition of each state | `px.bar(df, ..., color="status")`; default `barmode="relative"` stacks |
| Sort stacks by total | `fig.update_xaxes(categoryorder="total descending")` |

## Keeping Long Names Readable

Truncate in pandas and keep the full name in the hover text through `custom_data`:

```python
ranked = ranked.assign(rotulo=ranked["nome"].str.slice(0, 32))
fig = px.bar(
    ranked, x="faturamento", y="rotulo", orientation="h", custom_data=["nome", "pedidos"]
)
fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>R$ %{x:,.2f}<extra></extra>")
```

Two products can share the same first 32 characters, and identical labels merge into one bar. Keep
labels unique before charting.

## Selection as a Filter

```python
event = st.plotly_chart(
    ranking_chart(by_state, category="estado", title="Top estados"),
    key="top_states",
    on_select="rerun",
    selection_mode="points",
    config=PLOTLY_CONFIG,
)
states = tuple(sorted(point["y"] for point in event.selection.points))
```

## Example Usage

```python
# app/pages/2_Produtos.py
top = safe_load(load_top_products, filters.start, filters.end, filters.states, limit=10)
if has_rows(top):
    st.plotly_chart(
        ranking_chart(top, category="nome", title="Top 10 produtos"),
        key="top_products",
        config=PLOTLY_CONFIG,
    )
```

Limit rows in SQL with `ORDER BY ... LIMIT :limit`. There is no need to fetch every product and then
take the head in pandas.

## See Also

- [Chart Selection](../concepts/chart-selection.md)
- [Shared Layout Helper](shared-layout-helper.md)
- [Category Breakdown](category-breakdown.md)
- [SQL vs pandas](../../pandas/concepts/sql-vs-pandas.md)
