"""Shared filter row and saved views (bookmarks), drawn once by the router."""

from collections.abc import Callable
from dataclasses import astuple, dataclass
from datetime import date, timedelta

import streamlit as st

from data import load_filter_options

SESSION_KEY = "filters"
PERIOD_KEY = "filter_period"
STATES_KEY = "filter_states"
BOOKMARK_KEY = "bookmark"
DEFAULT_BOOKMARK = "Último trimestre"

Bookmark = Callable[[date, date], tuple[date, date, list[str]]]


def _months_back(end: date, months: int) -> date:
    index = end.year * 12 + end.month - 1 - months
    return date(index // 12, index % 12 + 1, 1)


BOOKMARKS: dict[str, Bookmark] = {
    "Último mês": lambda low, high: (_months_back(high, 0), high, []),
    "Último trimestre": lambda low, high: (_months_back(high, 2), high, []),
    "Ano completo": lambda low, high: (low, high, []),
    "Black Friday": lambda low, high: (date(2025, 11, 24), date(2025, 11, 30), []),
    "Natal": lambda low, high: (date(2025, 12, 1), date(2025, 12, 23), []),
    "Sudeste": lambda low, high: (low, high, ["MG", "RJ", "SP"]),
    "Sul": lambda low, high: (low, high, ["PR", "RS", "SC"]),
    "Nordeste": lambda low, high: (low, high, ["BA", "PE"]),
}


@dataclass(frozen=True)
class Filters:
    start: date
    end: date
    states: tuple[str, ...]

    def args(self) -> tuple[date, date, tuple[str, ...]]:
        return astuple(self)


def _apply_view(name: str, low: date, high: date) -> None:
    start, end, states = BOOKMARKS[name](low, high)
    st.session_state[PERIOD_KEY] = (start, end)
    st.session_state[STATES_KEY] = states


def _on_bookmark(low: date, high: date) -> None:
    name = st.session_state.get(BOOKMARK_KEY)
    if name:
        _apply_view(name, low, high)


def _clear_bookmark() -> None:
    st.session_state[BOOKMARK_KEY] = None


def filter_by_state(state: str) -> None:
    """Cross-filter from a chart click; a second click on the same state clears it."""
    current = st.session_state.get(STATES_KEY, [])
    st.session_state[STATES_KEY] = [] if current == [state] else [state]
    _clear_bookmark()


def render_filters() -> None:
    """Draw one filter row above every page and publish the selection."""
    options = load_filter_options()
    low, high = options["min_date"], options["max_date"]
    if low is None or high is None:
        st.info("Ainda não há pedidos. Rode `python -m src.prepare_data`.")
        st.stop()

    if PERIOD_KEY not in st.session_state:
        st.session_state[BOOKMARK_KEY] = DEFAULT_BOOKMARK
        _apply_view(DEFAULT_BOOKMARK, low, high)

    with st.container(key="filterbar"):
        views, period_column, states_column = st.columns([3.2, 1.05, 1.15], vertical_alignment="bottom")
        with views:
            st.pills("Visões salvas", options=list(BOOKMARKS), key=BOOKMARK_KEY,
                     on_change=_on_bookmark, args=(low, high))
        with period_column:
            period = st.date_input("Período", format="DD/MM/YYYY", key=PERIOD_KEY, on_change=_clear_bookmark)
        with states_column:
            states = st.multiselect("Estados", options=options["states"], placeholder="Todos",
                                    key=STATES_KEY, on_change=_clear_bookmark)

    if not isinstance(period, tuple) or len(period) != 2:
        st.info("Selecione a data final do período.")
        st.stop()

    st.session_state[SESSION_KEY] = Filters(period[0], period[1], tuple(sorted(states)))


def current_filters() -> Filters:
    return st.session_state[SESSION_KEY]


def comparison_grain(filters: Filters) -> str:
    days = (filters.end - filters.start).days + 1
    if days <= 45:
        return "day"
    return "week" if days <= 200 else "month"


def days_in(filters: Filters) -> timedelta:
    return filters.end - filters.start + timedelta(days=1)
