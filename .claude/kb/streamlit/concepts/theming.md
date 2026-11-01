# Theming

> **Purpose**: Set the dashboard's appearance in `.streamlit/config.toml`
> **Confidence**: 0.95
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## Overview

Theme options live in the `[theme]` table of `.streamlit/config.toml`, and most update while the app
runs. Chart colors are part of the theme, so Plotly charts rendered with `theme="streamlit"` pick up
the same palette. Do not put colors in code unless a color carries meaning, such as an order status.

## The Pattern

```toml
# .streamlit/config.toml, at the repository root
[theme]
base = "light"
primaryColor = "#0F766E"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F4F6F8"
textColor = "#1F2933"
borderColor = "#D9DEE4"
baseRadius = "medium"
showWidgetBorder = true
metricValueFontSize = "1.75rem"
metricValueFontWeight = 600
chartCategoricalColors = ["#0F766E", "#2563EB", "#D97706", "#7C3AED", "#DC2626", "#475569"]

[client]
toolbarMode = "minimal"
showErrorDetails = "none"
```

The values above are placeholders; the dashboard's real palette is still to be chosen.

## Config File Lookup

From highest to lowest precedence:

| Source | Location |
|--------|----------|
| Command line | `streamlit run app/Home.py --server.port 8502` |
| Environment | `STREAMLIT_*` variables |
| Script-level | `.streamlit/config.toml` next to the entrypoint (`app/.streamlit/`) |
| Per-project | `$CWD/.streamlit/config.toml` |
| Global | `%userprofile%/.streamlit/config.toml` on Windows |

Launching from the repository root makes the root `.streamlit/config.toml` the per-project file.

## Quick Reference

| Option | Type | Notes |
|--------|------|-------|
| `base` | `"light"`, `"dark"`, or a theme file path/URL | Base scheme |
| `primaryColor` | color | Interactive elements, highlights |
| `backgroundColor` | color | App background |
| `secondaryBackgroundColor` | color | Most interactive widgets |
| `textColor` | color | Body text |
| `font`, `headingFont` | string | Body and heading fonts |
| `baseRadius` | `"none"` to `"full"`, or a size | Corner radius |
| `borderColor`, `showWidgetBorder` | color, bool | Borders |
| `chartCategoricalColors` | array of colors | Series colors for Plotly |
| `chartSequentialColors` | array of 10 colors | Continuous scales |
| `redColor`, `greenColor` | color | Basic palette |
| `metricValueFontSize` | string such as `"1.75rem"` | `[theme]` only; a bare number is ignored |
| `metricValueFontWeight` | integer, 100-900 | `[theme]` only |
| `showSidebarBorder` | bool | `[theme]` only |

| Table | Purpose |
|-------|---------|
| `[theme.sidebar]` | Sidebar overrides |
| `[theme.light]`, `[theme.dark]` | Per-mode values |
| `[theme.light.sidebar]`, `[theme.dark.sidebar]` | Per-mode sidebar values |

| Client option | Values |
|---------------|--------|
| `toolbarMode` | `"auto"`, `"developer"`, `"viewer"`, `"minimal"` |
| `showSidebarNavigation` | `true`, `false` |
| `showErrorDetails` | `"full"`, `"stacktrace"`, `"type"`, `"none"` |

`showErrorDetails = "none"` hides uncaught tracebacks from viewers. Keep `"full"` while developing.

## Common Mistakes

### Wrong

```python
# Palette repeated in code bypasses the theme
px.bar(df, x="estado", y="faturamento", color_discrete_sequence=["#0F766E"])
```

```toml
[theme]
chartSequentialColors = ["#0F766E", "#2563EB"]  # Must list 10 colors
```

### Correct

```python
# The palette comes from theme.chartCategoricalColors
px.bar(df, x="estado", y="faturamento")
```

## Related

- [Layout](../concepts/layout.md)
- [Plotly Streamlit integration](../../plotly/concepts/streamlit-integration.md)
