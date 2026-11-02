"""Pure HTML builders. Every data value goes through `escape`."""

from base64 import b64encode
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from html import escape as _escape

import pandas as pd

from src.formatting import EMPTY, format_delta, format_number, format_percent
from theme import BLUE, GRID


def escape(value: object) -> str:
    return _escape(str(value))


def svg_image(svg: str, alt: str, css_class: str) -> str:
    """`st.html` strips inline SVG, so charts travel as images."""
    encoded = b64encode(svg.encode("utf-8")).decode("ascii")
    return f'<img class="{css_class}" src="data:image/svg+xml;base64,{encoded}" alt="{escape(alt)}">'


@dataclass(frozen=True)
class Column:
    """One column of a conditional table; `render` returns trusted, escaped HTML."""

    title: str
    render: Callable[[pd.Series], str]


def sparkline(values: Sequence[float]) -> str:
    """Area sparkline with an end dot; hidden when there is no trend to show."""
    points = [float(value) for value in values]
    if len(points) < 2:
        return ""
    low, high = min(points), max(points)
    span = (high - low) or 1
    width, height = 200, 42
    step = width / (len(points) - 1)
    coords = [(i * step, height - 5 - (p - low) / span * (height - 12)) for i, p in enumerate(points)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    area = f"0,{height} {line} {width},{height}"
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 0 {width + 6} {height}" preserveAspectRatio="none">'
        f'<polygon points="{area}" fill="{BLUE}" fill-opacity=".14"/>'
        f'<polyline points="{line}" fill="none" stroke="{BLUE}" stroke-width="2" '
        'stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/>'
        '</svg>'
    )
    return svg_image(svg, "", "spark")


def delta_badge(growth: float | None, *, lower_is_better: bool = False) -> str:
    """Direction carries an arrow, so color is never the only signal."""
    if growth is None:
        return f'<span class="delta none">{EMPTY}</span>'
    good = growth <= 0 if lower_is_better else growth >= 0
    arrow = "▲" if growth >= 0 else "▼"
    return f'<span class="delta {"good" if good else "bad"}">{arrow} {escape(format_delta(abs(growth)).lstrip("+"))}</span>'


def stat_tile(
    label: str,
    value: str,
    growth: float | None,
    previous: str,
    trend: Sequence[float] = (),
    *,
    lower_is_better: bool = False,
    hero: bool = False,
) -> str:
    context = "vs. período anterior" if growth is not None else "sem período anterior"
    return f"""
    <div class="tile{' hero' if hero else ''}" tabindex="0" aria-label="{escape(label)}: {escape(value)}, {context}">
      <div class="tile-label">{escape(label)}</div>
      <div class="tile-value">{escape(value)}</div>
      <div class="tile-row">{delta_badge(growth, lower_is_better=lower_is_better)}<span>{context}</span></div>
      {sparkline(trend)}
      <div class="tip">
        <div><span>Período atual</span><b>{escape(value)}</b></div>
        <div><span>Período anterior</span><b>{escape(previous)}</b></div>
      </div>
    </div>"""


def insights(findings: Sequence[str]) -> str:
    items = "".join(f'<div class="insight">{escape(text)}</div>' for text in findings)
    return f'<div class="insights">{items}</div>'


def segmented_bar(parts: Sequence[tuple[str, float, str]]) -> str:
    """One whole split into at most six parts; the share prints only where it fits."""
    total = sum(value for _, value, _ in parts) or 1
    blocks, legend = [], []
    for name, value, color in parts:
        share = value / total
        text = format_percent(share, 0) if share >= 0.09 else ""
        title = f"{name}: {format_number(value)} ({format_percent(share)})"
        blocks.append(
            f'<div style="width:{share * 100:.2f}%;background:{color}" title="{escape(title)}">{text}</div>'
        )
        legend.append(f'<span><i style="background:{color}"></i>{escape(name)} · {format_number(value)}</span>')
    return f'<div class="seg">{"".join(blocks)}</div><div class="legend">{"".join(legend)}</div>'


def data_bar(text: str, value: float, maximum: float) -> str:
    width = 0 if not maximum else max(value / maximum, 0) * 100
    return f'<span class="databar"><i style="width:{width:.1f}%"></i><b>{escape(text)}</b></span>'


def trend_cell(growth: float | None, *, lower_is_better: bool = False) -> str:
    if growth is None:
        return EMPTY
    good = growth <= 0 if lower_is_better else growth >= 0
    arrow = "▲" if growth >= 0 else "▼"
    return f'<span class="{"up" if good else "down"}">{arrow} {escape(format_percent(abs(growth)))}</span>'


def heat_cell(text: str, value: float | None, low: float, high: float, *, invert: bool = False) -> str:
    """Conditional fill: stronger means worse when `invert` is set."""
    if value is None or pd.isna(value):
        return EMPTY
    ratio = 0 if high == low else (value - low) / (high - low)
    color = "230,103,103" if invert else "57,135,229"
    return f'<span class="heat" style="background:rgba({color},{0.08 + ratio * 0.5:.2f})">{escape(text)}</span>'


def conditional_table(frame: pd.DataFrame, columns: Sequence[Column]) -> str:
    head = "".join(f"<th>{escape(column.title)}</th>" for column in columns)
    rows = "".join(
        "<tr>" + "".join(f"<td>{column.render(row)}</td>" for column in columns) + "</tr>"
        for _, row in frame.iterrows()
    )
    return f'<table class="ctable"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>'


def rating_ring(rating: float, count: int) -> str:
    """Meter: one ratio against the 5-point limit."""
    circumference = 2 * 3.14159 * 42
    filled = max(min(rating / 5, 1), 0) * circumference
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="42" fill="none" stroke="{GRID}" stroke-width="9"/>
        <circle cx="50" cy="50" r="42" fill="none" stroke="{BLUE}" stroke-width="9" stroke-linecap="round"
          stroke-dasharray="{filled:.1f} {circumference:.1f}" transform="rotate(-90 50 50)"/>
        <text x="50" y="50" text-anchor="middle" dominant-baseline="central" fill="#f0f3f8"
          font-family="Segoe UI, sans-serif" font-size="21" font-weight="600">{format_number(rating, 2)}</text>
      </svg>"""
    return f"""
    <div class="ring">
      {svg_image(svg, f"Nota média {format_number(rating, 2)} de 5", "ring-img")}
      <div class="ring-text"><b>Nota média</b><br>de 5 pontos<br>{format_number(count)} avaliações</div>
    </div>"""


def comment_card(date_text: str, product: str, category: str, rating: int, comment: str) -> str:
    stars = "★" * rating + "☆" * (5 - rating)
    return f"""
    <div class="comment">
      <span class="stars" aria-label="Nota {rating} de 5">{stars}</span>
      <p>{escape(comment)}</p>
      <small>{escape(date_text)} · {escape(product)} · <span class="chip">{escape(category)}</span></small>
    </div>"""
