# pt-BR Formatting

> **Purpose**: Show currency, numbers, and dates in pt-BR across axes, labels, and hover text
> **Confidence**: 0.90
> **MCP Validated**: 2026-11-01 (plotly.js source and official docs read)
> **Build Confirmed**: 2026-11-02 (Streamlit 1.66.1, Plotly 7.1.0, pandas 3.1.0, in the browser)

## Overview

Plotly formats numbers with d3-format and dates with d3-time-format. `layout.separators` sets the
decimal and thousands characters, and `,.2f` then renders `1.234,56`. Month and weekday names come
from the chart's locale, which defaults to English. In Streamlit, the pt-BR locale must be supplied
inline through `config["locales"]`, because the bundle does not register it.

## The Pattern

```python
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

HOVER_BRL = "%{x|%d/%m/%Y}<br>Faturamento: R$ %{y:,.2f}<extra></extra>"


def revenue_trend(daily: pd.DataFrame) -> go.Figure:
    fig = px.line(daily, x="dia", y="faturamento", markers=True)
    fig.update_traces(hovertemplate=HOVER_BRL)
    fig.update_xaxes(title=None, tickformat="%d/%m")
    fig.update_yaxes(title=None, tickprefix="R$ ", tickformat=",.0f")
    fig.update_layout(separators=",.")  # Decimal first, thousands second
    return fig
```

## Quick Reference

| Input | Output | Notes |
|-------|--------|-------|
| `%{y:,.2f}` with `separators=",."` | `1.234,56` | Hover and text templates |
| `R$ %{y:,.2f}` | `R$ 1.234,56` | Literal prefix |
| `tickformat=",.0f"` + `tickprefix="R$ "` | `R$ 1.235` | Axis ticks |
| `%{y:.1%}` | `12,5%` | Value must be a fraction |
| `%{x\|%d/%m/%Y}` | `15/03/2026` | Pipe for dates, colon for numbers |
| `tickformat="%d/%m"` | `15/03` | Short date ticks |
| `tickformat="%b/%Y"` | `Mar/2026` | Needs the locale config below |
| `%{customdata[0]:,d}` | `1.234` | Extra fields via `custom_data` |
| `<extra></extra>` | No trace box | Removes the secondary hover box |

## Why Not `$`

In d3-format, `$` inserts the locale's currency symbol, and the default English locale gives `$`.
Plotly's automatic number formatting ignores the `currency` key, so write `R$ ` as literal text.

## Month and Day Names

`%b`, `%B`, `%a`, and `%A` use the chart's locale. plotly.js ships a `pt-BR` locale, but it must be
registered with a script tag, which Streamlit does not expose. The `locales` config option takes the
same definition inline for one chart. Streamlit passes `config` through unchanged.

```python
PT_BR_FORMAT = {
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
PLOTLY_CONFIG = {"locale": "pt-BR", "locales": {"pt-BR": {"format": PT_BR_FORMAT}}}
```

This comes from the `locales` description and `getFormatObj` in the plotly.js source; it was not
rendered in a browser. Confirm it once on the first chart. If names stay in English, fall back to
numeric formats such as `%m/%Y`, which need no locale.

## Time Zones

Convert timestamps to `America/Sao_Paulo` in pandas and drop the zone before charting, so the chart
shows wall-clock time. See [Epoch Datetimes](../../pandas/concepts/epoch-datetimes.md).

## Common Mistakes

### Wrong

```python
fig.update_traces(hovertemplate="R$ %{y}")          # Raw, unformatted number
fig.update_traces(hovertemplate="%{y:$,.2f}")       # Dollar sign
fig.update_traces(hovertemplate="%{y:.2f}%")        # Prints the fraction with a % sign
```

### Correct

```python
fig.update_layout(separators=",.")
fig.update_traces(hovertemplate="R$ %{y:,.2f}<extra></extra>")
fig.update_traces(hovertemplate="%{y:.1%}<extra></extra>")
```

## Related

- [Streamlit Integration](../concepts/streamlit-integration.md)
- [Shared Layout Helper](../patterns/shared-layout-helper.md)
- [pt-BR Display Formatting](../../pandas/patterns/ptbr-display-formatting.md)
