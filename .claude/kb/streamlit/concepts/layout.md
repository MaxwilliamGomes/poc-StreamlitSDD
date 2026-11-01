# Layout

> **Purpose**: Arrange KPI rows, charts, and tables with columns, tabs, and containers
> **Confidence**: 0.95
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## Overview

Dashboards use `layout="wide"`, then stack rows of `st.columns` for KPIs and paired charts, and
`st.tabs` for alternate views of the same data. Tabs do not save work by default: all tab content is
computed and sent to the browser, whichever tab is selected.

## The Pattern

```python
import streamlit as st

from charts import revenue_by_category_chart, revenue_trend_chart, top_products_chart
from components.kpis import render_kpi_row

st.set_page_config(page_title="Vendas | ShopAgent", layout="wide")
st.title("Vendas")

render_kpi_row(kpis)                                   # Row 1: KPI cards

left, right = st.columns([2, 1], gap="medium")         # Row 2: 2/3 + 1/3
with left:
    st.plotly_chart(revenue_trend_chart(daily), key="trend")
with right:
    st.plotly_chart(revenue_by_category_chart(by_category), key="category")

tab_products, tab_table = st.tabs(["Top produtos", "Tabela"])  # Row 3
with tab_products:
    st.plotly_chart(top_products_chart(top), key="top_products")
with tab_table:
    st.dataframe(table, hide_index=True)
```

## Quick Reference

| API | Signature (keyword options) | Notes |
|-----|-----------------------------|-------|
| `st.columns(spec)` | `gap, vertical_alignment, border, width, wrap` | `spec` is an int or relative widths |
| `st.tabs(tabs)` | `default, key, on_change, bind, width, height` | Labels accept inline Markdown only |
| `st.container()` | `border, key, width, height, horizontal, gap` | `horizontal=True` lays out a row |
| `st.set_page_config()` | `page_title, page_icon, layout, initial_sidebar_state` | `layout="wide"` for dashboards |
| `st.sidebar` | Works with `with` or as `st.sidebar.widget(...)` | Filters live here |
| `st.dataframe(data)` | `hide_index, column_config, width, height` | `use_container_width` is deprecated |

| `gap` value | Meaning |
|-------------|---------|
| `"xxsmall"` to `"xxlarge"` | Named spacing; default `"small"` |
| Non-negative `int` | Pixels |
| `None` | No gap |

## Lazy Tabs

Expensive tabs can run only when selected. Set `on_change="rerun"`, then guard the content with
`tab.open`, which is `True` or `False` once tabs track state.

```python
tab_trend, tab_heatmap = st.tabs(
    ["Tendência", "Mapa de calor"], key="sales_tab", on_change="rerun"
)
if tab_trend.open:
    with tab_trend:
        st.plotly_chart(revenue_trend_chart(daily), key="trend")
if tab_heatmap.open:
    with tab_heatmap:
        heatmap = load_revenue_heatmap(filters.start, filters.end)  # Runs only here
        st.plotly_chart(revenue_heatmap_chart(heatmap), key="heatmap")
```

Tab state tracking cannot be used inside cache-decorated functions.

## Fragments

`@st.fragment` reruns one section alone, so a chart-local control does not rerun the whole page.
`run_every="1m"` refreshes that section on a timer, which suits a live KPI strip while ShadowTraffic
produces orders. The refresh still respects the cached function's TTL.

```python
@st.fragment(run_every="1m")
def live_kpis() -> None:
    render_kpi_row(load_kpis(filters.start, filters.end, filters.states))
```

## Common Mistakes

### Wrong

```python
st.plotly_chart(fig, use_container_width=True)  # Deprecated
cols = st.columns(6)                             # Six cards cramp narrow screens
```

### Correct

```python
st.plotly_chart(fig, key="trend")  # width="stretch" is the default
row = st.columns(4, gap="small")   # Wrap further KPIs onto a second row
```

## Related

- [Theming](../concepts/theming.md)
- [KPI Cards](../patterns/kpi-cards.md)
- [Plotly Streamlit integration](../../plotly/concepts/streamlit-integration.md)
