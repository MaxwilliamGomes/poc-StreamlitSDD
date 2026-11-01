# Streamlit Integration

> **Purpose**: Render figures with `st.plotly_chart` so that theme, width, config, and formatting behave
> **Confidence**: 0.95
> **MCP Validated**: 2026-11-01 (official docs via WebFetch and Streamlit source; Context7/Exa unavailable)

## Overview

`st.plotly_chart` renders a figure with Streamlit's own theme by default, so charts follow
`.streamlit/config.toml` in light and dark modes. Importing Streamlit also registers a `"streamlit"`
Plotly template and makes it the default. Settings placed directly on `fig.layout` survive; values in a
template may be replaced in the browser.

## The Pattern

```python
import streamlit as st

from charts import PLOTLY_CONFIG, revenue_trend_chart

fig = revenue_trend_chart(daily)

st.plotly_chart(
    fig,
    key="vendas_trend",     # Stable, unique within the page
    config=PLOTLY_CONFIG,   # Locale and toolbar options
)
```

`width="stretch"` and `theme="streamlit"` are the defaults, so neither needs passing.

## Quick Reference

| Parameter | Default | Notes |
|-----------|---------|-------|
| `figure_or_data` | Required | A Plotly figure, data object, or dict/list of them |
| `use_container_width` | `None` | Deprecated; will be removed |
| `width` | `"stretch"` | `"content"` or pixels |
| `height` | `"content"` | `"stretch"` or pixels; content uses the figure's height |
| `theme` | `"streamlit"` | `None` uses Plotly's native theme |
| `key` | `None` | Stable identity; needed to read selection state |
| `on_select` | `"ignore"` | `"rerun"` or a callback |
| `selection_mode` | All | `"points"`, `"box"`, `"lasso"` |
| `config` | `None` | Plotly config dict |
| `alt` | `None` | Screen-reader description |

## How the Theme Works

| Layer | What happens |
|-------|--------------|
| Python import | `pio.templates.default = "streamlit"`, with stand-in colors |
| Browser | Stand-ins become `theme.chartCategoricalColors` and related colors |
| Browser | Streamlit writes into `layout.template.layout` (fonts, grid, margins, hover) |
| Figure | Values in `fig.layout` keep priority over the template |

Consequences for this dashboard:

| Goal | Do |
|------|-----|
| Brand palette | Set `theme.chartCategoricalColors` in `config.toml` |
| Semantic color per status | `color_discrete_map` |
| Separators, height, margins | `fig.update_layout(...)` directly |
| Fully custom Plotly template | `theme=None`, and lose light/dark sync |

Streamlit never reads `layout.separators` or `config.locale`, so pt-BR settings pass through.

## Selections as Filters

```python
event = st.plotly_chart(
    fig,
    key="states_chart",
    on_select="rerun",
    selection_mode="points",
    config=PLOTLY_CONFIG,
)
selected = [point["y"] for point in event.selection.points]
```

With `on_select` enabled, the call returns a dict-like `PlotlyState` whose `selection` holds `points`,
`point_indices`, `box`, and `lasso`. With the default `"ignore"`, it returns a placeholder, so read
`selection` only when selections are on.

## Dependencies

| Package | Note |
|---------|------|
| `plotly` | Streamlit requires `>=4.0.0`; this KB documents 7.1.0 |
| `orjson` | Optional; speeds up large figures |
| `streamlit[charts]` | Installs the charting extras, including `plotly` and `orjson` |

## Common Mistakes

### Wrong

```python
st.plotly_chart(fig, use_container_width=True)                 # Deprecated
fig.update_layout(template="my_template")                      # Partly overridden by the theme
pio.templates.default = "plotly_white"                         # Drops the theme's colors
```

### Correct

```python
fig.update_layout(separators=",.", margin=dict(t=40, b=8, l=8, r=8))
st.plotly_chart(fig, key="trend", config=PLOTLY_CONFIG)
```

## Related

- [pt-BR Formatting](../concepts/pt-br-formatting.md)
- [Shared Layout Helper](../patterns/shared-layout-helper.md)
- [Streamlit Theming](../../streamlit/concepts/theming.md)
- [Streamlit Layout](../../streamlit/concepts/layout.md)
