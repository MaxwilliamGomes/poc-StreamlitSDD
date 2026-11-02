import streamlit as st

import charts
from components import html
from components.filters import current_filters
from components.ui import card, chart, html_block, page_header, stop_if_empty
from data import (
    load_customers_by_segment,
    load_order_frequency,
    load_previous_segments,
    load_state_scorecard,
)
from src import metrics
from src.formatting import SEGMENT_LABELS, format_currency, format_number, format_percent

filters = current_filters()
page_header("Clientes", filters)

segments = load_customers_by_segment(*filters.args())
stop_if_empty(segments.empty)
previous = load_previous_segments(*filters.args())

active, frequency = metrics.active_and_frequency(segments)
previous_active, previous_frequency = metrics.active_and_frequency(previous)
ticket = segments["faturamento"].sum() / segments["pedidos"].sum() if segments["pedidos"].sum() else None
previous_orders = previous["pedidos"].sum()
previous_ticket = previous["faturamento"].sum() / previous_orders if previous_orders else None

columns = st.columns(3)
with columns[0]:
    html_block(html.stat_tile("Clientes ativos", format_number(active),
                              metrics.growth(active, previous_active), format_number(previous_active), hero=True))
with columns[1]:
    html_block(html.stat_tile("Pedidos por cliente", format_number(frequency, 1),
                              metrics.growth(frequency, previous_frequency), format_number(previous_frequency, 1)))
with columns[2]:
    html_block(html.stat_tile("Ticket médio", format_currency(ticket), metrics.growth(ticket, previous_ticket),
                              format_currency(previous_ticket)))

left, right = st.columns(2)
with left:
    with card("frequency", "Frequência de compra", "Quantos clientes fizeram N pedidos no período"):
        frequency_frame = load_order_frequency(*filters.args())
        table = frequency_frame.rename(columns={"pedidos_cliente": "Pedidos", "clientes": "Clientes"})
        chart(charts.frequency_columns(frequency_frame), "customers_frequency", table)
with right:
    with card("segments", "Faturamento por segmento"):
        labeled = segments.assign(rotulo=segments["segmento"].map(SEGMENT_LABELS))
        chart(charts.segment_bars(labeled), "customers_segment")
        top_ticket = labeled["ticket_medio"].max()
        html_block(html.conditional_table(labeled, [
            html.Column("Segmento", lambda row: row["rotulo"]),
            html.Column("Ticket médio", lambda row: html.data_bar(format_currency(row["ticket_medio"]), row["ticket_medio"], top_ticket)),
            html.Column("Ativos", lambda row: format_number(row["clientes_ativos"])),
            html.Column("Frequência", lambda row: format_number(row["frequencia"], 1)),
        ]))

scorecard = load_state_scorecard(*filters.args())
top_active = scorecard["clientes_ativos"].max()
rated = scorecard[scorecard["avaliacoes"] > 0]["nota_media"]
with card("states", "Clientes por estado", "Tons mais fortes destacam melhores notas; * indica menos de 30 avaliações"):
    html_block(html.conditional_table(scorecard, [
        html.Column("Estado", lambda row: row["estado"]),
        html.Column("Clientes ativos", lambda row: html.data_bar(format_number(row["clientes_ativos"]), row["clientes_ativos"], top_active)),
        html.Column("Faturamento", lambda row: format_currency(row["faturamento"])),
        html.Column("Ticket médio", lambda row: format_currency(row["ticket_medio"])),
        html.Column("Cancelamento", lambda row: format_percent(row["taxa_cancelamento"])),
        html.Column("Nota média", lambda row: html.heat_cell(
            format_number(row["nota_media"], 2) + ("*" if row["avaliacoes"] < 30 else ""),
            row["nota_media"], rated.min() if len(rated) else 0, rated.max() if len(rated) else 0)),
    ]))
