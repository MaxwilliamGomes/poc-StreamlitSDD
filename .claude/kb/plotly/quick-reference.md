# Plotly Quick Reference

> Fast lookup tables. For code examples, see linked files.
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)

## Chart by KPI

| KPI | Chart | Call |
|-----|-------|------|
| Revenue over time | Line | `px.line(df, x="dia", y="faturamento", markers=True)` |
| Monthly revenue | Bars | `px.bar(df, x="mes", y="faturamento")` |
| Top products, top states | Horizontal bars | `px.bar(df, x="faturamento", y="nome", orientation="h")` |
| Status or payment share (few parts) | Donut | `px.pie(df, names="status", values="pedidos", hole=0.5)` |
| Revenue by category and brand | Treemap | `px.treemap(df, path=["categoria", "marca"], values="faturamento")` |
| State by category | Heatmap | `px.imshow(pivot, text_auto=True, aspect="auto")` |

## Common Express Arguments

| Argument | Purpose |
|----------|---------|
| `labels={"faturamento": "Faturamento"}` | Axis, legend, and hover names |
| `color="status"` | One trace per value |
| `color_discrete_map={...}` | Fixed color per value |
| `category_orders={"status": [...]}` | Order of axes, legends, facets |
| `custom_data=["pedidos"]` | Extra fields for `%{customdata[0]}` |
| `text_auto=".2f"` | Bar labels from a numeric format |
| `hole=0.5` | Donut (`px.pie`) |
| `height=380` | Figure height in pixels |

## pt-BR Formats

| Goal | Setting |
|------|---------|
| `1.234,56` separators | `fig.update_layout(separators=",.")` |
| Currency in hover | `"R$ %{y:,.2f}"` |
| Axis currency | `tickprefix="R$ ", tickformat=",.0f"` |
| Percent | `"%{y:.1%}"` for a 0-1 fraction |
| Date | `%{x\|%d/%m/%Y}`, `tickformat="%d/%m"` |
| Month name | `%b/%Y`, with `PLOTLY_CONFIG` locale |
| Hide trace box | Add `<extra></extra>` |

## Layout Calls

| Call | Effect |
|------|--------|
| `fig.update_layout(...)` | Figure-wide settings |
| `fig.update_traces(...)` | Applies to all traces |
| `fig.update_xaxes(...)`, `fig.update_yaxes(...)` | All axes of that direction |
| `fig.update_yaxes(categoryorder="total ascending")` | Largest bar on top |
| `fig.add_trace(go.Scatter(...))` | Add to a `px` figure |

## Decision Matrix

| Use Case | Choose |
|----------|--------|
| Standard chart from a tidy DataFrame | Plotly Express |
| Add a line over `px` bars | `px`, then `fig.add_trace` |
| Two value axes | `make_subplots(specs=[[{"secondary_y": True}]])` |
| Shared look | `apply_dashboard_layout(fig)` |
| Brand palette | `theme.chartCategoricalColors` in Streamlit |
| Semantic colors | `color_discrete_map` |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| `use_container_width=True` | Omit it; `width="stretch"` is the default |
| `"%{y:$,.2f}"` | `"R$ %{y:,.2f}"` |
| Rely on a template for `separators` | Set it on `fig.layout` |
| Pass tz-aware datetimes | Convert to local, then drop the timezone |
| `%b` without the locale config | Pass `config=PLOTLY_CONFIG` |
| `px.line_mapbox`, `titlefont` | Use `line_map`, `title_font` |
| Pie with many slices | Sorted horizontal bars |

## Related Documentation

| Topic | Path |
|-------|------|
| Chart selection | `concepts/chart-selection.md` |
| pt-BR formatting | `concepts/pt-br-formatting.md` |
| Layout helper | `patterns/shared-layout-helper.md` |
| Full Index | `index.md` |
