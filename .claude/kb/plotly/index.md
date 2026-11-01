# Plotly Knowledge Base

> **Purpose**: Build the ShopAgent dashboard's charts -- KPI chart choice, a shared layout helper, pt-BR formatting, Streamlit rendering
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)
> **Version**: Plotly 7.1.0 (Python), bundling plotly.js 4.1.1, rendered through Streamlit 1.66.0

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/express-vs-graph-objects.md](concepts/express-vs-graph-objects.md) | When to use Plotly Express and when to use `go` |
| [concepts/chart-selection.md](concepts/chart-selection.md) | Which chart for which KPI |
| [concepts/pt-br-formatting.md](concepts/pt-br-formatting.md) | Separators, currency, dates, month names, hover templates |
| [concepts/streamlit-integration.md](concepts/streamlit-integration.md) | `st.plotly_chart`, themes, config, selections |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/shared-layout-helper.md](patterns/shared-layout-helper.md) | One helper for layout, separators, and chart config |
| [patterns/time-series-chart.md](patterns/time-series-chart.md) | Revenue trend, moving average, dual axis |
| [patterns/ranking-bar-chart.md](patterns/ranking-bar-chart.md) | Top products and states as sorted horizontal bars |
| [patterns/category-breakdown.md](patterns/category-breakdown.md) | Status, payment, category, and heatmap breakdowns |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Fast lookup tables

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Express first** | `px` is the default; its functions return `go.Figure` for later adjustments |
| **Layout-level settings** | `layout.separators` survives Streamlit's theme; template values may not |
| **d3 formats** | `,.2f` plus `separators=",."` gives `1.234,56` |
| **Inline locale** | `config["locales"]` supplies pt-BR month names without a script tag |
| **Figures are pure** | Builders take a DataFrame and return a figure; pages render them |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/express-vs-graph-objects.md, concepts/chart-selection.md |
| **Intermediate** | concepts/pt-br-formatting.md, patterns/shared-layout-helper.md, patterns/ranking-bar-chart.md |
| **Advanced** | concepts/streamlit-integration.md, patterns/time-series-chart.md, patterns/category-breakdown.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| python-developer | patterns/shared-layout-helper.md, patterns/time-series-chart.md, patterns/ranking-bar-chart.md | Build chart functions in `app/charts.py` |
| code-reviewer | concepts/pt-br-formatting.md, concepts/streamlit-integration.md | Check formatting and deprecated arguments |

---

## Related Domains

| Domain | Use |
|--------|-----|
| [streamlit](../streamlit/index.md) | Pages, layout, and theme around the charts |
| [pandas](../pandas/index.md) | Aggregated DataFrames that the charts receive |
