from datetime import date

import pandas as pd
import pytest

from src import queries

MARCH = (date(2026, 3, 1), date(2026, 3, 31))


def test_previous_period_has_same_length():
    assert queries.previous_period(date(2026, 3, 1), date(2026, 3, 31)) == (
        date(2026, 1, 29),
        date(2026, 2, 28),
    )
    assert queries.previous_period(date(2026, 3, 5), date(2026, 3, 5)) == (
        date(2026, 3, 4),
        date(2026, 3, 4),
    )


@pytest.mark.parametrize(
    ("current", "previous", "expected"),
    [(150, 100, 0.5), (50, 100, -0.5), (10, 0, None), (10, None, None), (None, 10, None)],
)
def test_safe_growth(current, previous, expected):
    assert queries.safe_growth(current, previous) == expected


def test_fill_time_gaps_adds_zero_periods():
    frame = pd.DataFrame(
        {
            "periodo": pd.to_datetime(["2026-03-01", "2026-05-01"]),
            "faturamento": [10.0, 20.0],
            "pedidos": [1, 2],
        }
    )
    filled = queries.fill_time_gaps(frame, "month")
    assert filled["faturamento"].tolist() == [10, 0, 20]
    assert queries.fill_time_gaps(frame.iloc[0:0], "month").empty


@pytest.mark.integration
class TestWithKnownRows:
    def test_overview_excludes_cancelled_from_revenue(self, seeded):
        kpis = queries.overview_kpis(seeded, *MARCH, ())
        assert kpis["faturamento"] == 400
        assert kpis["pedidos"] == 3
        assert kpis["ticket_medio"] == pytest.approx(400 / 3)
        assert kpis["cancelados"] == 1
        assert kpis["total_pedidos"] == 4
        assert kpis["taxa_cancelamento"] == 0.25

    def test_timezone_boundary_of_last_day(self, seeded):
        """23:30 on the last local day is in; 00:30 on the next day is out."""
        march_end = (date(2026, 3, 31), date(2026, 3, 31))
        assert queries.overview_kpis(seeded, *march_end, ())["faturamento"] == 150
        april = (date(2026, 4, 1), date(2026, 4, 1))
        assert queries.overview_kpis(seeded, *april, ())["faturamento"] == 100

    def test_previous_period_variation(self, seeded):
        current = queries.overview_kpis(seeded, *MARCH, ())
        previous = queries.overview_kpis(seeded, *queries.previous_period(*MARCH), ())
        assert previous["faturamento"] == 100
        assert queries.safe_growth(current["faturamento"], previous["faturamento"]) == 3

    def test_no_previous_data_has_no_variation(self, seeded):
        start = date(2026, 2, 26)
        previous = queries.overview_kpis(seeded, *queries.previous_period(start, start), ())
        assert previous["faturamento"] == 0
        assert previous["ticket_medio"] is None
        assert queries.safe_growth(100, previous["faturamento"]) is None

    def test_state_filter(self, seeded):
        assert queries.overview_kpis(seeded, *MARCH, ("SP",))["faturamento"] == 250
        assert queries.overview_kpis(seeded, *MARCH, ("RJ",))["faturamento"] == 150

    def test_empty_result(self, seeded):
        period = (date(2030, 1, 1), date(2030, 1, 2))
        kpis = queries.overview_kpis(seeded, *period, ())
        assert kpis["pedidos"] == 0
        assert kpis["taxa_cancelamento"] is None
        assert queries.revenue_by_state(seeded, *period, ()).empty
        assert queries.review_summary(seeded, *period, ())["nota_media"] is None

    def test_group_totals_match_overall_revenue(self, seeded):
        total = queries.overview_kpis(seeded, *MARCH, ())["faturamento"]
        for load in (
            queries.revenue_by_state,
            queries.category_summary,
            queries.customers_by_segment,
            queries.customers_by_state,
        ):
            assert load(seeded, *MARCH, ())["faturamento"].sum() == total

    def test_status_and_payment_include_cancelled(self, seeded):
        status = queries.orders_by_status(seeded, *MARCH, ()).set_index("status")["pedidos"]
        assert status["cancelled"] == 1
        assert status.sum() == 4
        assert queries.orders_by_payment(seeded, *MARCH, ())["pedidos"].sum() == 4

    @pytest.mark.parametrize(
        ("grain", "first"), [("day", "2026-03-10"), ("week", "2026-03-09"), ("month", "2026-03-01")]
    )
    def test_revenue_over_time_grains(self, seeded, grain, first):
        frame = queries.revenue_over_time(seeded, *MARCH, (), grain)
        assert str(frame["periodo"].iloc[0].date()) == first
        assert frame["faturamento"].sum() == 400

    def test_invalid_grain_is_rejected(self, seeded):
        with pytest.raises(ValueError, match="Granularidade"):
            queries.revenue_over_time(seeded, *MARCH, (), "1; DROP TABLE orders")

    def test_top_products_ranks_by_revenue(self, seeded):
        frame = queries.top_products(seeded, *MARCH, ())
        assert frame["produto"].tolist() == ["Mouse", "Tenis"]
        assert frame["faturamento"].tolist() == [200, 200]

    def test_category_cancel_rate(self, seeded):
        frame = queries.category_summary(seeded, *MARCH, ()).set_index("macro_categoria")
        assert frame.loc["Moda", "taxa_cancelamento"] == 0.5
        assert frame.loc["Tecnologia", "taxa_cancelamento"] == 0

    def test_segment_frequency_and_active_customers(self, seeded):
        frame = queries.customers_by_segment(seeded, *MARCH, ()).set_index("segmento")
        assert frame.loc["premium", "clientes_ativos"] == 1
        assert frame.loc["premium", "frequencia"] == 2
        assert frame["clientes_ativos"].sum() == 2

    def test_reviews(self, seeded):
        assert queries.review_summary(seeded, *MARCH, ()) == {"avaliacoes": 2, "nota_media": 3.0}
        sentiment = queries.sentiment_distribution(seeded, *MARCH, ()).set_index("sentimento")
        assert sentiment.loc["positive", "pct"] == 0.5
        rating = queries.rating_by_category(seeded, *MARCH, ()).set_index("macro_categoria")
        assert rating.loc["Tecnologia", "avaliacoes"] == 1
        assert rating.loc["Tecnologia", "nota_media"] == 1
        negative = queries.negative_comments(seeded, *MARCH, ())
        assert negative["comentario"].tolist() == ["Ruim"]

    def test_filter_options(self, seeded):
        options = queries.filter_options(seeded)
        assert options["states"] == ["RJ", "SP"]
        assert options["min_date"] == date(2026, 2, 26)
        assert options["max_date"] == date(2026, 4, 1)


@pytest.mark.integration
class TestDesignQueries:
    def test_kpi_series_matches_overview(self, seeded):
        frame = queries.kpi_series(seeded, *MARCH, (), "month")
        assert frame["faturamento"].tolist() == [400]
        assert frame["taxa_cancelamento"].tolist() == [0.25]

    def test_heatmap_uses_local_time(self, seeded):
        frame = queries.orders_heatmap(seeded, *MARCH, ())
        last = frame[frame["hora"] == 23]
        assert last["pedidos"].sum() == 1
        assert last["dia_semana"].iloc[0] == 2  # 31/03/2026 is a Tuesday in Sao Paulo
        assert frame["pedidos"].sum() == 3

    def test_scorecard_combines_sales_and_reviews(self, seeded):
        frame = queries.state_scorecard(seeded, *MARCH, ()).set_index("estado")
        assert frame.loc["SP", "faturamento"] == 250
        assert frame.loc["SP", "nota_media"] == 5
        assert frame.loc["RJ", "taxa_cancelamento"] == 0.5
        assert frame["avaliacoes"].sum() == 2

    def test_product_performance_totals_match(self, seeded):
        assert queries.product_performance(seeded, *MARCH, ())["faturamento"].sum() == 400

    def test_matrix_totals_match(self, seeded):
        assert queries.category_state_matrix(seeded, *MARCH, ())["faturamento"].sum() == 400

    def test_payment_over_time_includes_cancelled(self, seeded):
        assert queries.payment_over_time(seeded, *MARCH, ())["pedidos"].sum() == 4

    def test_order_frequency_ignores_cancelled(self, seeded):
        frame = queries.order_frequency(seeded, *MARCH, ()).set_index("pedidos_cliente")
        assert frame.loc[2, "clientes"] == 1
        assert frame.loc[1, "clientes"] == 1

    def test_review_breakdowns(self, seeded):
        ratings = queries.rating_distribution(seeded, *MARCH, ()).set_index("nota")
        assert ratings["avaliacoes"].to_dict() == {1: 1, 5: 1}
        sentiment = queries.sentiment_by_category(seeded, *MARCH, ())
        assert sentiment["avaliacoes"].sum() == 2
