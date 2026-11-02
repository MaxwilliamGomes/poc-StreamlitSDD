"""pt-BR display formatting and domain labels."""

from datetime import date, datetime

EMPTY = "—"

STATUS_LABELS = {
    "delivered": "Entregue",
    "shipped": "Enviado",
    "processing": "Em processamento",
    "cancelled": "Cancelado",
}
PAYMENT_LABELS = {"pix": "Pix", "credit_card": "Cartão de crédito", "boleto": "Boleto"}
SEGMENT_LABELS = {"premium": "Premium", "standard": "Padrão", "basic": "Básico"}
SENTIMENT_LABELS = {"positive": "Positiva", "neutral": "Neutra", "negative": "Negativa"}


def _swap_separators(text: str) -> str:
    return text.replace(",", "\0").replace(".", ",").replace("\0", ".")


def format_number(value: float | None, decimals: int = 0) -> str:
    if value is None:
        return EMPTY
    return _swap_separators(f"{value:,.{decimals}f}")


def format_currency(value: float | None) -> str:
    if value is None:
        return EMPTY
    formatted = format_number(abs(value), 2)
    return f"-R$ {formatted}" if value < 0 else f"R$ {formatted}"


def format_percent(fraction: float | None, decimals: int = 1) -> str:
    if fraction is None:
        return EMPTY
    return f"{format_number(fraction * 100, decimals)}%"


def format_delta(fraction: float | None) -> str | None:
    """Signed variation for `st.metric`; None hides the delta."""
    if fraction is None:
        return None
    sign = "+" if fraction >= 0 else ""
    return f"{sign}{format_percent(fraction)}"


def format_date(value: date | datetime | None) -> str:
    if value is None:
        return EMPTY
    return value.strftime("%d/%m/%Y")
