import json
import random
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text

from src import prepare_data
from src.prepare_data import (
    MACRO_CATEGORIES,
    _execute_script,
    PERIOD_END,
    PERIOD_START,
    day_weight,
    link_reviews,
    load_reviews,
    macro_category,
    prepare,
    simulated_dates,
)

ALL_TERMS = [term for terms in MACRO_CATEGORIES.values() for term in terms]


def review_line(**overrides) -> str:
    row = {
        "review_id": str(uuid4()),
        "order_id": str(uuid4()),
        "rating": 4,
        "comment": "Bom",
        "sentiment": "positive",
    }
    return json.dumps({**row, **overrides})


def test_mapping_covers_22_terms_in_8_groups():
    assert len(MACRO_CATEGORIES) == 8
    assert len(set(ALL_TERMS)) == 22


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        ("Games", "Entretenimento"),
        ("Games, Shoes & Tools", "Entretenimento"),
        ("Automotive & Shoes", "Automotivo e Indústria"),
        ("Clothing & Kids", "Moda"),
    ],
)
def test_macro_category_uses_first_term(category, expected):
    assert macro_category(category) == expected


def test_unmapped_category_fails():
    with pytest.raises(ValueError, match="sem mapeamento"):
        macro_category("Unknown")


def test_day_weights():
    assert day_weight(date(2025, 11, 26)) == 3.0  # Black Friday week, weekday
    assert day_weight(date(2025, 12, 10)) == 1.6
    assert day_weight(date(2026, 1, 14)) == 0.8
    assert day_weight(date(2026, 5, 6)) == 1.0
    assert day_weight(date(2026, 5, 9)) == 0.85  # Saturday


def test_simulated_dates_are_deterministic_and_in_period():
    first = simulated_dates(2000, random.Random(1))
    assert first == simulated_dates(2000, random.Random(1))
    assert min(first).date() >= PERIOD_START
    assert max(first).date() <= PERIOD_END
    assert {at.hour for at in first} <= set(range(8, 24))
    assert len({(at.year, at.month) for at in first}) == 12


def test_load_reviews_reports_the_bad_line(tmp_reviews: Path):
    tmp_reviews.write_text(review_line() + "\n" + review_line(rating=9) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="linha 2"):
        load_reviews(tmp_reviews)


def test_link_reviews_uses_distinct_orders(tmp_reviews: Path):
    tmp_reviews.write_text("\n".join(review_line() for _ in range(3)), encoding="utf-8")
    reviews = load_reviews(tmp_reviews)
    orders = [str(uuid4()) for _ in range(10)]
    linked = link_reviews(reviews, orders, random.Random(1))
    assert len({row["order_id"] for row in linked}) == 3
    assert {row["order_id"] for row in linked} <= set(orders)
    assert linked == link_reviews(list(reversed(reviews)), orders, random.Random(1))


def _seed_raw(engine, orders: int = 30) -> None:
    categories = ["Games, Shoes & Tools", "Baby"]
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE raw_customers (customer_id text, name text, email text,
                                        city text, state text, segment text);
            CREATE TABLE raw_products (product_id text, name text, category text,
                                       price double precision, brand text);
            CREATE TABLE raw_orders (order_id text, customer_id text, product_id text,
                                     qty double precision, total double precision,
                                     status text, payment text, created_at bigint);
        """))
        customer, products = str(uuid4()), [str(uuid4()), str(uuid4())]
        conn.execute(
            text("INSERT INTO raw_customers VALUES (:id, 'A', 'a@x', 'C', 'SP', 'basic')"),
            {"id": customer},
        )
        for product, category in zip(products, categories, strict=True):
            conn.execute(
                text("INSERT INTO raw_products VALUES (:id, 'P', :category, 10.5, 'B')"),
                {"id": product, "category": category},
            )
        for index in range(orders):
            conn.execute(
                text("""
                    INSERT INTO raw_orders VALUES (:id, :customer, :product, 3, 999.0,
                                                   :status, 'pix', 1776133560779)
                """),
                {
                    "id": str(uuid4()),
                    "customer": customer,
                    "product": products[index % 2],
                    "status": "delivered" if index % 3 else "cancelled",
                },
            )


def _snapshot(engine) -> tuple:
    with engine.connect() as conn:
        return (
            conn.execute(text("""
                SELECT count(*), sum(total), min(created_at), max(created_at), sum(qty)
                FROM orders
            """)).one(),
            conn.execute(text("SELECT count(*) FROM products")).scalar(),
            conn.execute(text("""
                SELECT string_agg(r.review_id::text || o.order_id::text, ',' ORDER BY r.review_id)
                FROM reviews r JOIN orders o USING (order_id)
            """)).scalar(),
        )


@pytest.mark.integration
class TestPrepare:
    @pytest.fixture
    def prepared(self, empty_schema, tmp_reviews):
        _seed_raw(empty_schema)
        tmp_reviews.write_text("\n".join(review_line() for _ in range(5)), encoding="utf-8")
        prepare(empty_schema, tmp_reviews)
        return empty_schema

    def test_is_idempotent(self, prepared, tmp_reviews):
        first = _snapshot(prepared)
        prepare(prepared, tmp_reviews)
        assert _snapshot(prepared) == first

    def test_total_is_qty_times_price(self, prepared):
        with prepared.connect() as conn:
            wrong = conn.execute(text("""
                SELECT count(*) FROM orders o JOIN products p USING (product_id)
                WHERE o.total <> o.qty * p.price
            """)).scalar()
        assert wrong == 0

    def test_macro_categories(self, prepared):
        with prepared.connect() as conn:
            values = conn.execute(text("SELECT DISTINCT macro_category FROM products")).scalars().all()
        assert set(values) == {"Entretenimento", "Infantil"}

    def test_reviews_only_on_delivered_orders(self, prepared):
        with prepared.connect() as conn:
            statuses = conn.execute(text("""
                SELECT DISTINCT o.status FROM reviews r JOIN orders o USING (order_id)
            """)).scalars().all()
            count = conn.execute(text("SELECT count(*) FROM reviews")).scalar()
        assert statuses == ["delivered"]
        assert count == 5

    def test_schema_matches_contract(self, prepared):
        with prepared.connect() as conn:
            types = dict(conn.execute(text("""
                SELECT table_name || '.' || column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = current_schema()
            """)).all())
            kinds = conn.execute(text("""
                SELECT contype, count(*) FROM pg_constraint
                WHERE connamespace = current_schema()::text::regnamespace
                  AND conrelid::regclass::text NOT LIKE 'raw_%'
                GROUP BY contype
            """)).all()
            indexes = conn.execute(text("""
                SELECT count(*) FROM pg_indexes
                WHERE schemaname = current_schema() AND indexname LIKE 'idx_%'
            """)).scalar()
        assert types["orders.created_at"] == "timestamp with time zone"
        assert types["orders.total"] == "numeric"
        assert types["orders.qty"] == "integer"
        assert types["orders.order_id"] == "uuid"
        assert types["reviews.rating"] == "smallint"
        assert types["products.macro_category"] == "character varying"
        constraints = {kind: count for kind, count in kinds}
        assert constraints["p"] == 4
        assert constraints["f"] == 3
        assert constraints["u"] == 1
        assert indexes == 6

    def test_failure_rolls_back(self, prepared, tmp_reviews, monkeypatch):
        before = _snapshot(prepared)

        def boom(*_args):
            raise RuntimeError("falha simulada")

        monkeypatch.setattr(prepare_data, "_validate", boom)
        with pytest.raises(RuntimeError, match="falha simulada"):
            prepare(prepared, tmp_reviews)
        assert _snapshot(prepared) == before

    def test_restores_dump_when_no_source_exists(self, empty_schema, tmp_path):
        dump = tmp_path / "dump.sql"
        dump.write_text(
            "SELECT pg_catalog.set_config('search_path', '', false);\n"
            "\\restrict abc\n"
            + "".join(
                f"CREATE TABLE {{schema}}.{table} (id text);\n" for table in ("customers", "products", "orders")
            ),
            encoding="utf-8",
        )
        with empty_schema.begin() as conn:
            schema = conn.execute(text("SELECT current_schema()")).scalar()
            dump.write_text(dump.read_text(encoding="utf-8").replace("{schema}", f'"{schema}"'),
                            encoding="utf-8")
            before = conn.execute(text("SELECT current_setting('search_path')")).scalar()
            prepare_data.ensure_raw_tables(conn, dump)
            assert conn.execute(text("SELECT current_setting('search_path')")).scalar() == before
            assert conn.execute(text("SELECT to_regclass('raw_orders') IS NOT NULL")).scalar()

    def _dump(self, conn, tmp_path):
        schema = conn.execute(text("SELECT current_schema()")).scalar()
        dump = tmp_path / "dump.sql"
        tables = "".join(
            f"""CREATE TABLE "{schema}".{name} (id text);
                INSERT INTO "{schema}".{name} VALUES ('x');\n"""
            for name in ("customers", "products", "orders")
        )
        dump.write_text(tables, encoding="utf-8")
        return dump

    def test_empty_schema_only_tables_are_replaced_by_the_dump(self, empty_schema, tmp_path):
        with empty_schema.begin() as conn:
            _execute_script(conn, prepare_data.INIT_SQL)
            prepare_data.ensure_raw_tables(conn, self._dump(conn, tmp_path))
            assert conn.execute(text("SELECT count(*) FROM raw_orders")).scalar() == 1
            assert conn.execute(text("SELECT to_regclass('reviews')")).scalar() is None

    def test_partial_source_stops_the_run(self, empty_schema, tmp_path):
        with empty_schema.begin() as conn:
            for name in ("customers", "products", "orders"):
                conn.execute(text(f"CREATE TABLE {name} (id text)"))
            conn.execute(text("INSERT INTO customers VALUES ('x')"))
            with pytest.raises(RuntimeError, match="Origem incompleta"):
                prepare_data.ensure_raw_tables(conn, self._dump(conn, tmp_path))


def test_period_has_365_days():
    assert PERIOD_START + timedelta(days=364) == PERIOD_END
