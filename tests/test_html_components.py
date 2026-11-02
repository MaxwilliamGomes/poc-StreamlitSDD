"""HTML builders: data must never reach the page as markup."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

import pandas as pd  # noqa: E402

from components import html  # noqa: E402

ATTACK = "<script>alert(1)</script>"


def test_comment_text_is_escaped():
    markup = html.comment_card("01/01/2026", ATTACK, ATTACK, 2, ATTACK)
    assert "<script>" not in markup
    assert "★★☆☆☆" in markup


def test_table_cells_can_escape_data():
    frame = pd.DataFrame({"produto": [ATTACK]})
    markup = html.conditional_table(frame, [html.Column("Produto", lambda row: html.escape(row["produto"]))])
    assert "<script>" not in markup


def test_segmented_bar_hides_label_on_small_parts():
    markup = html.segmented_bar([("Grande", 95, "#000"), ("Pequeno", 5, "#111")])
    assert ">95%<" in markup
    assert ">5%<" not in markup
    assert "Pequeno · 5" in markup


def test_delta_badge_direction_and_meaning():
    assert "▼" in html.delta_badge(-0.1, lower_is_better=True) and "good" in html.delta_badge(-0.1, lower_is_better=True)
    assert "▲" in html.delta_badge(0.1, lower_is_better=True) and "bad" in html.delta_badge(0.1, lower_is_better=True)
    assert "—" in html.delta_badge(None)


def test_sparkline_needs_a_trend():
    assert html.sparkline([1.0]) == ""
    assert "image/svg+xml" in html.sparkline([1.0, 2.0, 1.5])
