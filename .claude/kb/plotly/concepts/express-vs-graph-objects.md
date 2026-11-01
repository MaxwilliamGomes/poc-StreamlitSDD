# Express vs Graph Objects

> **Purpose**: Decide when to use Plotly Express and when to drop to `graph_objects`
> **Confidence**: 0.95
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## Overview

Plotly's docs recommend Plotly Express by default. Express builds a figure from a tidy DataFrame in
one call and returns a `go.Figure`, so `graph_objects` remains available afterward. Use `go`
directly only when a figure mixes trace types or needs dual axes or per-trace control.

## The Pattern

```python
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def monthly_revenue_with_trend(monthly: pd.DataFrame) -> go.Figure:
    """Express for the bars, a graph object for the extra line."""
    fig = px.bar(
        monthly,
        x="mes",
        y="faturamento",
        labels={"mes": "Mês", "faturamento": "Faturamento"},
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["mes"],
            y=monthly["media_3m"],
            mode="lines",
            name="Média de 3 meses",
        )
    )
    return fig
```

## Quick Reference

| Need | Use | Reason |
|------|-----|--------|
| Line, bar, pie, treemap, heatmap | `px` | One call from a DataFrame |
| One trace per category | `px` with `color=` | Grouping is automatic |
| Extra series on a chart | `px` + `fig.add_trace(go...)` | Figures are interchangeable |
| Two value axes | `make_subplots` + `go` | Mixed axes are easier from `go` |
| Chart type missing from `px` | `go` | Example: `mesh`, `isosurface` |
| Fine control of one trace | `go` or `fig.update_traces(selector=...)` | Direct attribute access |

## Adjusting a Figure

| Method | Scope |
|--------|-------|
| `fig.update_layout(...)` | Title, margins, legend, separators, hover mode |
| `fig.update_traces(...)` | All traces, or those matching `selector` |
| `fig.update_xaxes(...)`, `fig.update_yaxes(...)` | Axes |
| `fig.add_trace(...)` | Add one trace |
| `fig.add_hline(y=...)` | Reference line such as a target |

Magic underscore notation is available: `fig.update_layout(legend_title_text="Status")`.

## Tidy Input

Express works best with one row per observation. Aggregate first, and pass long format rather than
one column per series.

| Long (preferred) | Wide (avoid) |
|------------------|--------------|
| `dia, status, faturamento` | `dia, delivered, shipped, cancelled` |

Use `DataFrame.melt` when a query returns wide data.

## Version Notes (7.x)

Plotly 7.0.0 removed these, none of which the dashboard should need:

| Removed | Use instead |
|---------|-------------|
| Mapbox functions (`scatter_mapbox`, `line_mapbox`, ...) | `scatter_map`, `line_map`, ... |
| Figure factories such as `create_distplot`, `create_gantt` | `px` equivalents |
| Kaleido below 1.0, Orca | Kaleido 1.x for static export |
| `rgb()` strings with 0-1 fractions, `hsv()` strings | Standard CSS colors |

## Common Mistakes

### Wrong

```python
# Hand-built traces for what color= does automatically
fig = go.Figure()
for status, group in df.groupby("status"):
    fig.add_trace(go.Bar(x=group["dia"], y=group["faturamento"], name=status))
```

### Correct

```python
fig = px.bar(df, x="dia", y="faturamento", color="status")
```

## Related

- [Chart Selection](../concepts/chart-selection.md)
- [Shared Layout Helper](../patterns/shared-layout-helper.md)
- [Time Series Chart](../patterns/time-series-chart.md)
