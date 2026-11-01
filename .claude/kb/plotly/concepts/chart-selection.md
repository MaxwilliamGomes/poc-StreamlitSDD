# Chart Selection

> **Purpose**: Match each dashboard KPI to the chart that answers it
> **Confidence**: 0.90
> **MCP Validated**: 2026-11-01 (API calls checked against official docs; the selection guidance is editorial)

## Overview

Choose the chart from the question: change over time needs a line, ranking needs sorted bars, and part
of a whole needs a donut or treemap. The Plotly docs describe what each chart does, not when to pick
it, so the rules below are this project's editorial choices. A single number belongs in `st.metric`,
not in a chart.

## The Pattern

```python
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def revenue_trend(daily: pd.DataFrame) -> go.Figure:
    """Change over time: is revenue growing?"""
    return px.line(daily, x="dia", y="faturamento", markers=True)


def top_products(ranked: pd.DataFrame) -> go.Figure:
    """Ranking: which products sell most?"""
    fig = px.bar(ranked, x="faturamento", y="nome", orientation="h")
    fig.update_yaxes(categoryorder="total ascending")
    return fig


def orders_by_status(by_status: pd.DataFrame) -> go.Figure:
    """Part of a whole with few categories."""
    return px.pie(by_status, names="status", values="pedidos", hole=0.5)
```

## Quick Reference

| Question | Page | Chart | Key fields |
|----------|------|-------|------------|
| How is revenue evolving? | Vendas | Line | `orders.created_at`, `total` |
| Which months were best? | Vendas | Vertical bars | Month, revenue |
| Which products lead? | Produtos | Horizontal bars | `products.name`, revenue |
| Which categories and brands matter? | Produtos | Treemap | `category`, `brand` |
| Which states buy most? | Clientes | Horizontal bars | `customers.state` |
| How do segments compare? | Clientes | Grouped bars | `segment`, ticket |
| What is the status mix? | Vendas | Donut | `status` (4 values) |
| How do customers pay? | Vendas | Donut | `payment` (3 values) |
| Where do state and category meet? | Clientes | Heatmap | Pivot of revenue |
| How are ratings distributed? | Avaliações | Vertical bars | `rating` |

## Selection Rules

| Situation | Rule |
|-----------|------|
| 2-5 parts of a whole | Donut is fine |
| More than 5 parts | Sorted horizontal bars |
| Long labels, such as product names | Horizontal bars |
| Under 3 time points | Bars or a KPI, not a line |
| Two measures with different units | Two charts first; dual axis only if the link matters |
| Hierarchy of two levels | Treemap |
| Exact values needed | `st.dataframe` next to the chart |

## Data Caveat

Orders currently span about 8 minutes, so a daily line has a single point. Until
`shadowtraffic.json` spreads dates over a longer period, use hourly or minute buckets for development.
Otherwise a correct chart looks broken.

## Fixed Category Order

Domain values have a natural order. Keep it with `category_orders` instead of sorting by value:

```python
STATUS_ORDER = ["processing", "shipped", "delivered", "cancelled"]
STATUS_LABELS = {
    "processing": "Em processamento",
    "shipped": "Enviado",
    "delivered": "Entregue",
    "cancelled": "Cancelado",
}
```

Map raw values to labels in pandas before charting, because `labels=` renames columns, not values.

## Common Mistakes

### Wrong

```python
# Pie of 30 products: unreadable slices
px.pie(by_product, names="nome", values="faturamento")
```

### Correct

```python
top = by_product.nlargest(10, "faturamento")
fig = px.bar(top, x="faturamento", y="nome", orientation="h")
fig.update_yaxes(categoryorder="total ascending")
```

## Related

- [Express vs Graph Objects](../concepts/express-vs-graph-objects.md)
- [Time Series Chart](../patterns/time-series-chart.md)
- [Ranking Bar Chart](../patterns/ranking-bar-chart.md)
- [Category Breakdown](../patterns/category-breakdown.md)
