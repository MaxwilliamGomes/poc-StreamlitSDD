"""Small derived figures for pages, kept free of SQL and of Streamlit."""

import pandas as pd


def growth(current: float | None, previous: float | None) -> float | None:
    """Relative change, or None when there is no base to compare with."""
    if current is None or not previous:
        return None
    return (current - previous) / previous


def active_and_frequency(segments: pd.DataFrame) -> tuple[int, float | None]:
    """Each customer has one segment, so summing segments gives the true total."""
    active = int(segments["clientes_ativos"].sum()) if not segments.empty else 0
    return active, (segments["pedidos"].sum() / active if active else None)
