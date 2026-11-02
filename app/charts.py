"""Plotly figure builders. Values arrive aggregated; labels are pt-BR here."""

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.formatting import PAYMENT_LABELS, SENTIMENT_LABELS
from theme import AQUA, AXIS, BLUE, CRITICAL, GRID, INK, INK_MUTED, INK_SECONDARY, ORANGE, SEQUENTIAL, YELLOW

CHART_HEIGHT = 320
WEEKDAYS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
PAYMENT_COLORS = {"Pix": BLUE, "Cartão de crédito": ORANGE, "Boleto": AQUA}
GRAIN_TICKS = {"day": "%d/%m", "week": "%d/%m", "month": "%b/%y"}
GRAIN_HOVER = {"day": "%d/%m/%Y", "week": "Semana de %d/%m/%Y", "month": "%b/%Y"}
MAX_BAR_PX = 22

PLOTLY_CONFIG: dict[str, Any] = {
    "displaylogo": False,
    "displayModeBar": False,
    "scrollZoom": False,
    "locale": "pt-BR",
    "locales": {
        "pt-BR": {
            "format": {
                "shortMonths": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                                "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
                "months": ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
                           "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
                "date": "%d/%m/%Y",
                "decimal": ",",
                "thousands": ".",
            }
        }
    },
}


def _layout(fig: go.Figure, height: int = CHART_HEIGHT, *, legend: bool = False) -> go.Figure:
    fig.update_layout(
        height=height,
        separators=",.",
        showlegend=legend,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0, "title_text": None,
                "font": {"color": INK_SECONDARY, "size": 12}},
        margin={"t": 34 if legend else 8, "r": 18, "b": 6, "l": 6},
        hovermode="closest",
        dragmode=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": INK_SECONDARY, "size": 12},
        hoverlabel={"bgcolor": "#1b2740", "bordercolor": AXIS, "font": {"color": INK, "size": 13}},
    )
    fig.update_xaxes(title_text=None, showgrid=False, linecolor=AXIS, tickfont={"color": INK_MUTED},
                     zeroline=False)
    fig.update_yaxes(title_text=None, gridcolor=GRID, gridwidth=1, griddash="solid", linecolor=AXIS,
                     tickfont={"color": INK_MUTED}, zeroline=False)
    return fig


def _hbar(frame: pd.DataFrame, value: str, group: str, hover: str, height: int, *,
          color: str = BLUE, text: pd.Series | None = None) -> go.Figure:
    """Ranked thin bars with the value at the tip."""
    ordered = frame.sort_values(value).reset_index(drop=True)
    fig = go.Figure(go.Bar(
        x=ordered[value], y=ordered[group], orientation="h", marker_color=color, marker_cornerradius=4,
        marker_line_width=0, width=0.52, hovertemplate=hover,
        text=None if text is None else text.reindex(frame.sort_values(value).index).tolist(),
        textposition="outside", cliponaxis=False, textfont={"color": INK_SECONDARY},
    ))
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)", tickfont={"color": INK_SECONDARY}, automargin=True)
    top = float(frame[value].max()) if len(frame) else 0
    fig.update_xaxes(showgrid=True, gridcolor=GRID, tickformat=",d", range=[0, top * 1.16 or 1])
    return _layout(fig, height)


def compact_brl(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:.1f} mi".replace(".", ",")
    if abs(value) >= 1_000:
        return f"R$ {value / 1_000:.0f} mil"
    return f"R$ {value:.0f}"


def revenue_comparison(current: pd.DataFrame, previous: pd.DataFrame, grain: str) -> go.Figure:
    """Current period in the accent, previous as context, aligned by position."""
    fig = go.Figure()
    positions = current["periodo"]
    if not previous.empty:
        aligned = previous.head(len(current))
        fig.add_trace(go.Scatter(
            x=positions.iloc[: len(aligned)], y=aligned["faturamento"], name="Período anterior",
            mode="lines", line={"color": INK_MUTED, "width": 2, "shape": "spline", "smoothing": .6},
            hovertemplate="Anterior: <b>R$ %{y:,.2f}</b><extra></extra>",
        ))
    fig.add_trace(go.Scatter(
        x=positions, y=current["faturamento"], name="Período atual", mode="lines+markers",
        line={"color": BLUE, "width": 2, "shape": "spline", "smoothing": .6},
        marker={"size": 8, "color": BLUE, "line": {"color": "#101827", "width": 2}},
        fill="tozeroy", fillcolor="rgba(57,135,229,.10)",
        hovertemplate="Atual: <b>R$ %{y:,.2f}</b><extra></extra>",
    ))
    if len(current):
        peak = current.loc[current["faturamento"].idxmax()]
        fig.add_annotation(x=peak["periodo"], y=peak["faturamento"], text=f"<b>{compact_brl(peak['faturamento'])}</b>",
                           showarrow=False, yshift=16, font={"color": INK, "size": 12})
    fig.update_xaxes(tickformat=GRAIN_TICKS[grain], hoverformat=GRAIN_HOVER[grain], showspikes=True,
                     spikecolor=AXIS, spikethickness=1, spikedash="solid", spikemode="across")
    fig.update_yaxes(tickprefix="R$ ", tickformat="~s", rangemode="tozero")
    _layout(fig, 340, legend=not previous.empty)
    return fig.update_layout(hovermode="x unified")


def revenue_trend(frame: pd.DataFrame, grain: str) -> go.Figure:
    """Series plus a moving average that smooths daily noise."""
    fig = go.Figure(go.Scatter(
        x=frame["periodo"], y=frame["faturamento"], name="Faturamento", mode="lines",
        line={"color": BLUE, "width": 2}, fill="tozeroy", fillcolor="rgba(57,135,229,.10)",
        hovertemplate="Faturamento: <b>R$ %{y:,.2f}</b><extra></extra>",
    ))
    if grain == "day" and len(frame) >= 7:
        smooth = frame["faturamento"].rolling(7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=frame["periodo"], y=smooth, name="Média de 7 dias", mode="lines",
            line={"color": ORANGE, "width": 2},
            hovertemplate="Média de 7 dias: <b>R$ %{y:,.2f}</b><extra></extra>",
        ))
    fig.update_xaxes(tickformat=GRAIN_TICKS[grain], hoverformat=GRAIN_HOVER[grain], showspikes=True,
                     spikecolor=AXIS, spikethickness=1, spikedash="solid", spikemode="across")
    fig.update_yaxes(tickprefix="R$ ", tickformat="~s", rangemode="tozero")
    _layout(fig, 340, legend=len(fig.data) > 1)
    return fig.update_layout(hovermode="x unified")


def state_bars(frame: pd.DataFrame) -> go.Figure:
    labels = frame["faturamento"].map(compact_brl)
    fig = _hbar(frame, "faturamento", "estado", "%{y}<br><b>R$ %{x:,.2f}</b><extra>Clique para filtrar</extra>",
                300, text=labels)
    return fig.update_xaxes(visible=False)


def payment_bars(frame: pd.DataFrame) -> go.Figure:
    labeled = frame.assign(rotulo=frame["pagamento"].map(PAYMENT_LABELS))
    labels = labeled["pedidos"].map(lambda value: f"{value:,}".replace(",", "."))
    fig = _hbar(labeled, "pedidos", "rotulo", "%{y}<br><b>%{x:,} pedidos</b><extra></extra>", 170, text=labels)
    return fig.update_xaxes(visible=False)


def orders_heatmap(frame: pd.DataFrame) -> go.Figure:
    """Weekday by hour, one hue from near the surface to light."""
    grid = frame.pivot_table(index="dia_semana", columns="hora", values="pedidos", fill_value=0)
    grid = grid.reindex(index=range(1, 8), columns=range(8, 24), fill_value=0)
    scale = [[i / (len(SEQUENTIAL) - 1), color] for i, color in enumerate(SEQUENTIAL)]
    fig = go.Figure(go.Heatmap(
        z=grid.values, x=[f"{hour}h" for hour in grid.columns], y=WEEKDAYS, colorscale=scale, xgap=2, ygap=2,
        hovertemplate="%{y}, %{x}<br><b>%{z} pedidos</b><extra></extra>",
        colorbar={"thickness": 8, "outlinewidth": 0, "tickfont": {"color": INK_MUTED}},
    ))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return _layout(fig, 300)


def revenue_change(current: pd.DataFrame, previous: pd.DataFrame) -> go.Figure:
    """Diverging bars: how much each state added or lost against the previous period."""
    joined = current.set_index("estado")[["faturamento"]].join(
        previous.set_index("estado")[["faturamento"]], how="outer", rsuffix="_ant"
    ).fillna(0)
    joined = joined.assign(delta=joined["faturamento"] - joined["faturamento_ant"]).sort_values("delta")
    labels = [f"{'+' if value >= 0 else '−'}{compact_brl(abs(value))}" for value in joined["delta"]]
    fig = go.Figure(go.Bar(
        x=joined["delta"], y=joined.index, orientation="h", width=.52, marker_cornerradius=4,
        marker_line_width=0, marker_color=[BLUE if value >= 0 else ORANGE for value in joined["delta"]],
        text=labels, textposition="outside", cliponaxis=False, textfont={"color": INK_SECONDARY},
        hovertemplate="%{y}<br><b>R$ %{x:+,.2f}</b><extra></extra>",
    ))
    reach = float(joined["delta"].abs().max()) or 1
    fig.update_xaxes(visible=False, range=[-reach * 1.32, reach * 1.32])
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)", tickfont={"color": INK_SECONDARY})
    fig.add_vline(x=0, line_color=AXIS, line_width=1)
    return _layout(fig, 320)


def payment_mix(frame: pd.DataFrame) -> go.Figure:
    """Monthly share, stacked to 100%, so the mix change is what stands out."""
    labeled = frame.assign(rotulo=frame["pagamento"].map(PAYMENT_LABELS))
    fig = px.bar(labeled, x="periodo", y="pedidos", color="rotulo", color_discrete_map=PAYMENT_COLORS,
                 category_orders={"rotulo": list(PAYMENT_COLORS)})
    fig.update_traces(marker_line_color="#101827", marker_line_width=2,
                      hovertemplate="%{fullData.name}<br><b>%{y:,} pedidos</b><extra></extra>")
    fig.update_layout(barmode="stack", barnorm="percent", bargap=.72)
    fig.update_xaxes(tickformat="%b/%y", dtick="M1")
    fig.update_yaxes(ticksuffix="%", range=[0, 100])
    return _layout(fig, 320, legend=True)


def category_lollipop(frame: pd.DataFrame, average: float | None) -> go.Figure:
    """Emphasis: categories above the average take the accent, the rest stay gray."""
    ordered = frame.sort_values("taxa_cancelamento").reset_index(drop=True)
    above = ordered["taxa_cancelamento"] > (average or 0)
    fig = go.Figure()
    for _, row in ordered.iterrows():
        fig.add_shape(type="line", x0=0, x1=row["taxa_cancelamento"], y0=row["macro_categoria"],
                      y1=row["macro_categoria"], line={"color": AXIS, "width": 2})
    fig.add_trace(go.Scatter(
        x=ordered["taxa_cancelamento"], y=ordered["macro_categoria"], mode="markers+text",
        marker={"size": 12, "color": [ORANGE if flag else INK_MUTED for flag in above],
                "line": {"color": "#101827", "width": 2}},
        text=[f"{value:.1%}".replace(".", ",") for value in ordered["taxa_cancelamento"]],
        textposition="middle right", textfont={"color": INK_SECONDARY},
        hovertemplate="%{y}<br><b>%{x:.1%}</b><extra></extra>", cliponaxis=False,
    ))
    if average is not None:
        fig.add_vline(x=average, line_color=INK_MUTED, line_width=1,
                      annotation_text=f"Média {average:.1%}".replace(".", ","),
                      annotation_position="top", annotation_font_color=INK_SECONDARY)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)", tickfont={"color": INK_SECONDARY})
    fig.update_xaxes(tickformat=".0%", rangemode="tozero", showgrid=False)
    fig.update_xaxes(range=[0, float(ordered["taxa_cancelamento"].max()) * 1.25 or 1])
    return _layout(fig, 340).update_layout(margin={"t": 26})


def category_matrix(frame: pd.DataFrame) -> go.Figure:
    grid = frame.pivot_table(index="macro_categoria", columns="estado", values="faturamento", fill_value=0)
    grid = grid.loc[grid.sum(axis=1).sort_values().index]
    scale = [[i / (len(SEQUENTIAL) - 1), color] for i, color in enumerate(SEQUENTIAL)]
    fig = go.Figure(go.Heatmap(
        z=grid.values, x=grid.columns.tolist(), y=grid.index.tolist(), colorscale=scale, xgap=2, ygap=2,
        hovertemplate="%{y} · %{x}<br><b>R$ %{z:,.2f}</b><extra></extra>",
        colorbar={"thickness": 8, "outlinewidth": 0, "tickprefix": "R$ ", "tickformat": "~s",
                  "tickfont": {"color": INK_MUTED}},
    ))
    fig.update_xaxes(side="top")
    fig.update_yaxes(showgrid=False, tickfont={"color": INK_SECONDARY})
    return _layout(fig, 340).update_layout(margin={"t": 26})


def frequency_columns(frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=frame["pedidos_cliente"], y=frame["clientes"], marker_color=BLUE, marker_cornerradius=4,
        marker_line_width=0, hovertemplate="%{x} pedidos<br><b>%{y} clientes</b><extra></extra>",
    ))
    fig.update_layout(bargap=.62)
    fig.update_xaxes(dtick=1 if len(frame) <= 14 else 2, title_text="Pedidos no período")
    _layout(fig, 300)
    return fig.update_xaxes(title_text="Pedidos no período", title_font={"color": INK_MUTED, "size": 12})


def segment_bars(frame: pd.DataFrame) -> go.Figure:
    labels = frame["faturamento"].map(compact_brl)
    fig = _hbar(frame, "faturamento", "rotulo", "%{y}<br><b>R$ %{x:,.2f}</b><extra></extra>", 170, text=labels)
    return fig.update_xaxes(visible=False)


def rating_columns(frame: pd.DataFrame) -> go.Figure:
    grid = frame.set_index("nota").reindex(range(1, 6), fill_value=0).reset_index()
    fig = go.Figure(go.Bar(
        x=[f"{note} ★" for note in grid["nota"]], y=grid["avaliacoes"], marker_color=BLUE,
        marker_cornerradius=4, marker_line_width=0, text=grid["avaliacoes"], textposition="outside",
        cliponaxis=False, textfont={"color": INK_SECONDARY},
        hovertemplate="%{x}<br><b>%{y} avaliações</b><extra></extra>",
    ))
    fig.update_layout(bargap=.62)
    fig.update_yaxes(visible=False, rangemode="tozero")
    return _layout(fig, 250)


def sentiment_diverging(frame: pd.DataFrame, minimum: int) -> go.Figure:
    """Ordered scale centered on neutral; small groups carry a mark on their label."""
    wide = frame.pivot_table(index="macro_categoria", columns="sentimento", values="avaliacoes", fill_value=0)
    wide = wide.reindex(columns=["negative", "neutral", "positive"], fill_value=0)
    totals = wide.sum(axis=1)
    share = wide.div(totals, axis=0)
    share = share.assign(saldo=share["positive"] - share["negative"]).sort_values("saldo")
    labels = [
        f"{name} (n={int(totals[name])}){' ⚠' if totals[name] < minimum else ''}" for name in share.index
    ]
    half = share["neutral"] / 2
    series = (
        ("negative", -(share["negative"]), -(half + share["negative"]) , CRITICAL),
        ("neutral", share["neutral"], -half, AXIS),
        ("positive", share["positive"], half, BLUE),
    )
    fig = go.Figure()
    for key, values, base, color in series:
        fig.add_trace(go.Bar(
            y=labels, x=values.abs(), base=base, orientation="h", name=SENTIMENT_LABELS[key], marker_color=color,
            marker_cornerradius=4, marker_line_color="#101827", marker_line_width=2, width=.56,
            customdata=share[key].to_numpy(),
            hovertemplate=f"%{{y}}<br>{SENTIMENT_LABELS[key]}: <b>%{{customdata:.1%}}</b><extra></extra>",
        ))
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(tickformat=".0%", showgrid=True, gridcolor=GRID, zeroline=True, zerolinecolor=AXIS)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)", tickfont={"color": INK_SECONDARY})
    return _layout(fig, 360, legend=True)


STATUS_SEGMENTS = {
    "delivered": BLUE, "shipped": AQUA, "processing": YELLOW, "cancelled": ORANGE,
}
SENTIMENT_SEGMENTS = {"positive": BLUE, "neutral": AXIS, "negative": CRITICAL}
