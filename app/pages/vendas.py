import streamlit as st

import charts
from components import html
from components.filters import current_filters
from components.ui import card, chart, html_block, page_header, stop_if_empty
from data import (
    load_payment_over_time,
    load_previous_revenue_by_state,
    load_previous_scorecard,
    load_revenue_by_state,
    load_revenue_over_time,
    load_state_scorecard,
)
from src.formatting import format_currency, format_number, format_percent

GRAINS = {"day": "Dia", "week": "Semana", "month": "Mês"}

filters = current_filters()
page_header("Vendas", filters)

by_state = load_revenue_by_state(*filters.args())
stop_if_empty(by_state.empty)

with card("trend", "Evolução do faturamento"):
    grain = st.segmented_control("Granularidade", options=list(GRAINS), format_func=GRAINS.get,
                                 default="week", required=True, key="sales_grain", label_visibility="collapsed")
    series = load_revenue_over_time(*filters.args(), grain)
    table = series.rename(columns={"periodo": "Período", "faturamento": "Faturamento", "pedidos": "Pedidos"})
    chart(charts.revenue_trend(series, grain), "sales_trend", table)

left, right = st.columns(2)
previous_states = load_previous_revenue_by_state(*filters.args())
with left:
    with card("bridge", "O que mudou no faturamento", "Ganho ou perda de cada estado sobre o período anterior"):
        if previous_states.empty:
            st.info("Sem período anterior para comparar. Escolha uma visão mais curta.")
        else:
            chart(charts.revenue_change(by_state, previous_states), "sales_change")
with right:
    with card("mix", "Formas de pagamento por mês", "Participação nos pedidos, incluindo cancelados"):
        chart(charts.payment_mix(load_payment_over_time(*filters.args())), "sales_mix")

scorecard = load_state_scorecard(*filters.args())
previous_card = load_previous_scorecard(*filters.args()).set_index("estado")["faturamento"]
scorecard = scorecard.assign(
    variacao=[
        (row.faturamento - previous_card[row.estado]) / previous_card[row.estado]
        if previous_card.get(row.estado) else None
        for row in scorecard.itertuples()
    ]
)
top_revenue = scorecard["faturamento"].max()
rates = scorecard["taxa_cancelamento"]
tickets = scorecard["ticket_medio"]


def _growth(row) -> str:
    return html.trend_cell(None if row["variacao"] != row["variacao"] else row["variacao"])


columns = [
    html.Column("Estado", lambda row: row["estado"]),
    html.Column("Faturamento", lambda row: html.data_bar(format_currency(row["faturamento"]), row["faturamento"], top_revenue)),
    html.Column("Variação", _growth),
    html.Column("Pedidos", lambda row: format_number(row["pedidos"])),
    html.Column("Ticket médio", lambda row: html.heat_cell(format_currency(row["ticket_medio"]), row["ticket_medio"], tickets.min(), tickets.max())),
    html.Column("Cancelamento", lambda row: html.heat_cell(format_percent(row["taxa_cancelamento"]), row["taxa_cancelamento"], rates.min(), rates.max(), invert=True)),
]
with card("scorecard", "Painel por estado", "Barras indicam faturamento; vermelho mais forte indica mais cancelamento"):
    html_block(html.conditional_table(scorecard, columns))
