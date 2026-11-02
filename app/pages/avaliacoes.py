import streamlit as st

import charts
from components import html
from components.filters import current_filters
from components.ui import MIN_REVIEWS, card, chart, html_block, page_header, stop_if_empty
from data import (
    load_negative_comments,
    load_rating_by_category,
    load_rating_distribution,
    load_review_summary,
    load_sentiment,
    load_sentiment_by_category,
)
from src.formatting import SENTIMENT_LABELS, format_date, format_number

COMMENTS_SHOWN = 8

filters = current_filters()
page_header("Avaliações", filters)

summary = load_review_summary(*filters.args())
stop_if_empty(summary["avaliacoes"] == 0)

sentiment = load_sentiment(*filters.args())
parts = [
    (SENTIMENT_LABELS[name], int(sentiment.loc[sentiment["sentimento"] == name, "avaliacoes"].sum()), color)
    for name, color in charts.SENTIMENT_SEGMENTS.items()
]

left, middle, right = st.columns([1, 1.3, 1.2])
with left:
    with card("rating", "Satisfação geral"):
        html_block(html.rating_ring(summary["nota_media"], summary["avaliacoes"]))
with middle:
    with card("sentiment", "Sentimento das avaliações"):
        html_block(html.segmented_bar(parts))
with right:
    with card("distribution", "Distribuição das notas"):
        chart(charts.rating_columns(load_rating_distribution(*filters.args())).update_layout(height=150), "reviews_notes")

ratings = load_rating_by_category(*filters.args())
small = int((ratings["avaliacoes"] < MIN_REVIEWS).sum())

left, right = st.columns([1.25, 1])
with left:
    with card("categories", "Sentimento por macrocategoria", "Centrado no neutro: esquerda negativa, direita positiva"):
        table = ratings.rename(columns={"macro_categoria": "Macrocategoria", "avaliacoes": "Avaliações", "nota_media": "Nota média"})
        chart(charts.sentiment_diverging(load_sentiment_by_category(*filters.args()), MIN_REVIEWS), "reviews_categories", table)
        if small:
            st.warning(f"Amostra pequena: {small} de {len(ratings)} macrocategorias têm menos de {MIN_REVIEWS} avaliações.", icon="⚠️")
with right:
    with card("comments", "Comentários negativos recentes"):
        comments = load_negative_comments(*filters.args())
        if comments.empty:
            st.info("Nenhum comentário negativo para os filtros selecionados.")
        else:
            html_block("".join(
                html.comment_card(format_date(row.data), row.produto, row.macro_categoria, int(row.nota), row.comentario)
                for row in comments.head(COMMENTS_SHOWN).itertuples()
            ))
            st.caption(f"Mostrando {min(COMMENTS_SHOWN, len(comments))} de {format_number(len(comments))} comentários carregados.")
