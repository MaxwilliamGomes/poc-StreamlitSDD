from datetime import date

from src.formatting import (
    format_currency,
    format_date,
    format_delta,
    format_number,
    format_percent,
)


def test_currency_uses_brazilian_separators():
    assert format_currency(1234.56) == "R$ 1.234,56"
    assert format_currency(11856768.69) == "R$ 11.856.768,69"
    assert format_currency(-5) == "-R$ 5,00"


def test_number_and_percent():
    assert format_number(4485) == "4.485"
    assert format_number(3.113, 2) == "3,11"
    assert format_percent(0.103) == "10,3%"


def test_date():
    assert format_date(date(2026, 12, 31)) == "31/12/2026"


def test_missing_values_show_a_dash():
    assert format_currency(None) == "—"
    assert format_percent(None) == "—"
    assert format_date(None) == "—"


def test_delta_has_sign_and_hides_without_base():
    assert format_delta(0.125) == "+12,5%"
    assert format_delta(-0.5) == "-50,0%"
    assert format_delta(None) is None
