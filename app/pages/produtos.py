import streamlit as st

import charts
from components import html
from components.filters import current_filters
from components.ui import card, chart, html_block, page_header, stop_if_empty
from data import (
    load_category_matrix,
    load_category_summary,
    load_overview,
    load_previous_products,
    load_product_performance,
)
from src.formatting import format_currency, format_number

VIEWS = {"top": "Top 10", "bottom": "Bottom 10"}

filters = current_filters()
page_header("Produtos", filters)

categories = load_category_summary(*filters.args())
stop_if_empty(categories.empty)

products = load_product_performance(*filters.args())
previous = load_previous_products(*filters.args()).set_index("product_id")["faturamento"]
products = products.assign(anterior=products["product_id"].map(previous))
products = products.assign(variacao=(products["faturamento"] - products["anterior"]) / products["anterior"])

left, right = st.columns([1.25, 1])
with left:
    with card("ranking", "Ranking de produtos"):
        view = st.segmented_control("Ranking", options=list(VIEWS), format_func=VIEWS.get, default="top",
                                    required=True, key="products_view", label_visibility="collapsed")
        selling = products[products["pedidos"] > 0]
        ranked = selling.head(10) if view == "top" else selling.tail(10).iloc[::-1]
        top_revenue = ranked["faturamento"].max()

        def _growth(row) -> str:
            value = row["variacao"]
            finite = value == value and abs(value) != float("inf")
            return html.trend_cell(float(value) if finite else None)

        columns = [
            html.Column("Produto", lambda row: html.escape(row["produto"])),
            html.Column("Macrocategoria", lambda row: f'<span class="chip">{html.escape(row["macro_categoria"])}</span>'),
            html.Column("Faturamento", lambda row: html.data_bar(format_currency(row["faturamento"]), row["faturamento"], top_revenue)),
            html.Column("Variação", _growth),
            html.Column("Pedidos", lambda row: format_number(row["pedidos"])),
        ]
        html_block(html.conditional_table(ranked, columns))
with right:
    with card("cancel", "Cancelamento por macrocategoria", "Laranja indica acima da média do período"):
        average = load_overview(*filters.args())["taxa_cancelamento"]
        table = categories[["macro_categoria", "taxa_cancelamento"]].rename(
            columns={"macro_categoria": "Macrocategoria", "taxa_cancelamento": "Cancelamento"})
        chart(charts.category_lollipop(categories, average), "products_cancel", table)

with card("matrix", "Faturamento por macrocategoria e estado", "Tons mais claros indicam maior faturamento"):
    chart(charts.category_matrix(load_category_matrix(*filters.args())), "products_matrix")
