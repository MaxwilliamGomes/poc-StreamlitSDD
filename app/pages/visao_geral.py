import streamlit as st

import charts
from components import html
from components.filters import comparison_grain, current_filters
from components.ui import card, chart, clickable_state_chart, html_block, page_header, stop_if_empty
from data import (
    load_category_summary,
    load_kpi_series,
    load_orders_by_payment,
    load_orders_by_status,
    load_orders_heatmap,
    load_overview_comparison,
    load_previous_series,
    load_revenue_by_state,
)
from src.formatting import STATUS_LABELS, format_currency, format_number, format_percent
from src.insights import overview_insights

GRAIN_NOTES = {
    "day": "Por dia",
    "week": "Por semana; a primeira e a última semana podem estar incompletas",
    "month": "Por mês; o primeiro e o último mês podem estar incompletos",
}

filters = current_filters()
page_header("Visão geral", filters)

current, previous, growth = load_overview_comparison(*filters.args())
stop_if_empty(current["total_pedidos"] == 0)

grain = comparison_grain(filters)
series = load_kpi_series(*filters.args(), grain)
previous_series = load_previous_series(*filters.args(), grain)
by_state = load_revenue_by_state(*filters.args())
categories = load_category_summary(*filters.args())

columns = st.columns([1.5, 1, 1, 1])
with columns[0]:
    html_block(html.stat_tile("Faturamento", format_currency(current["faturamento"]), growth["faturamento"],
                              format_currency(previous["faturamento"]), series["faturamento"].tolist(), hero=True))
with columns[1]:
    html_block(html.stat_tile("Pedidos", format_number(current["pedidos"]), growth["pedidos"],
                              format_number(previous["pedidos"]), series["pedidos"].tolist()))
with columns[2]:
    html_block(html.stat_tile("Ticket médio", format_currency(current["ticket_medio"]), growth["ticket_medio"],
                              format_currency(previous["ticket_medio"]), series["ticket_medio"].tolist()))
with columns[3]:
    html_block(html.stat_tile("Taxa de cancelamento", format_percent(current["taxa_cancelamento"]),
                              growth["taxa_cancelamento"], format_percent(previous["taxa_cancelamento"]),
                              series["taxa_cancelamento"].tolist(), lower_is_better=True))

findings = overview_insights(growth, by_state.to_dict("records"), categories.to_dict("records"))
if findings:
    html_block(html.insights(findings))

left, right = st.columns([2.1, 1])
with left:
    with card("comparison", "Faturamento: atual vs. período anterior", GRAIN_NOTES[grain]):
        table = series[["periodo", "faturamento", "pedidos"]].rename(
            columns={"periodo": "Período", "faturamento": "Faturamento", "pedidos": "Pedidos"})
        chart(charts.revenue_comparison(series, previous_series, grain), "overview_comparison", table)
with right:
    with card("status", "Status dos pedidos", "Inclui cancelados"):
        status = load_orders_by_status(*filters.args())
        parts = [
            (STATUS_LABELS[name], int(status.loc[status["status"] == name, "pedidos"].sum()), color)
            for name, color in charts.STATUS_SEGMENTS.items()
        ]
        html_block(html.segmented_bar(parts))
    with card("payment", "Pedidos por pagamento"):
        chart(charts.payment_bars(load_orders_by_payment(*filters.args())), "overview_payment")

left, right = st.columns(2)
with left:
    with card("heatmap", "Quando os pedidos acontecem", "Pedidos por dia da semana e hora"):
        chart(charts.orders_heatmap(load_orders_heatmap(*filters.args())), "overview_heatmap")
with right:
    with card("states", "Faturamento por estado", "Clique em uma barra para filtrar o painel"):
        clickable_state_chart(charts.state_bars(by_state), "overview_states")
