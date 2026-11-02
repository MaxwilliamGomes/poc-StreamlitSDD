"""Prepare the dashboard database from the original tables and the reviews file.

Run with `python -m src.prepare_data`. The whole run is one transaction, and every
run rebuilds the final tables from `raw_*`, so repeated runs give the same result.
"""

import json
import random
import sys
from collections.abc import Iterable, Sequence
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import Connection, Engine, text

from src.db import PROJECT_ROOT, create_db_engine
from src.models import Review

INIT_SQL = PROJECT_ROOT / "gen" / "init.sql"
RAW_DUMP = PROJECT_ROOT / "gen" / "data" / "raw_dump.sql"
REVIEWS_FILE = PROJECT_ROOT / "gen" / "data" / "reviews" / "reviews.jsonl"

SEED = 20261102
TIMEZONE = ZoneInfo("America/Sao_Paulo")
PERIOD_START = date(2025, 11, 1)
PERIOD_END = date(2026, 10, 31)
RAW_TABLES = ("customers", "products", "orders")

MACRO_CATEGORIES = {
    "Moda": ("Clothing", "Shoes", "Jewelry"),
    "Beleza e Saúde": ("Beauty", "Health"),
    "Casa e Mercado": ("Home", "Garden", "Tools", "Grocery"),
    "Tecnologia": ("Computers", "Electronics"),
    "Entretenimento": ("Books", "Games", "Movies", "Music"),
    "Infantil": ("Baby", "Kids", "Toys"),
    "Esporte e Lazer": ("Sports", "Outdoors"),
    "Automotivo e Indústria": ("Automotive", "Industrial"),
}
TERM_TO_MACRO = {term: macro for macro, terms in MACRO_CATEGORIES.items() for term in terms}


def macro_category(category: str) -> str:
    """Map a raw category such as 'Games, Shoes & Tools' by its first term."""
    first_term = category.replace("&", ",").split(",")[0].strip()
    try:
        return TERM_TO_MACRO[first_term]
    except KeyError as exc:
        raise ValueError(f"Categoria sem mapeamento: {category!r}") from exc


def day_weight(day: date) -> float:
    """Relative order volume of a simulated day."""
    if date(2025, 11, 24) <= day <= date(2025, 11, 30):
        weight = 3.0
    elif date(2025, 12, 1) <= day <= date(2025, 12, 23):
        weight = 1.6
    elif date(2026, 1, 1) <= day <= date(2026, 2, 28):
        weight = 0.8
    else:
        weight = 1.0
    return weight * 0.85 if day.weekday() >= 5 else weight


def simulated_dates(count: int, rng: random.Random) -> list[datetime]:
    """Draw `count` timezone-aware timestamps across the simulated period."""
    days = [
        PERIOD_START + timedelta(days=offset)
        for offset in range((PERIOD_END - PERIOD_START).days + 1)
    ]
    chosen = rng.choices(days, weights=[day_weight(day) for day in days], k=count)
    return [
        datetime.combine(day, time(rng.randrange(8, 24), rng.randrange(60), rng.randrange(60)),
                         tzinfo=TIMEZONE)
        for day in chosen
    ]


def load_reviews(path: Path = REVIEWS_FILE) -> list[Review]:
    """Read and validate every line, so bad input fails before touching the database."""
    reviews = []
    with path.open(encoding="utf-8") as lines:
        for number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                reviews.append(Review(**json.loads(line)))
            except ValueError as exc:
                raise ValueError(f"{path.name}, linha {number}: {exc}") from exc
    return reviews


def link_reviews(
    reviews: Sequence[Review], delivered_ids: Iterable[str], rng: random.Random
) -> list[dict[str, object]]:
    """Attach each review to a distinct delivered order."""
    ordered = sorted(reviews, key=lambda review: str(review.review_id))
    picked = rng.sample(sorted(str(order_id) for order_id in delivered_ids), k=len(ordered))
    return [
        {
            "review_id": str(review.review_id),
            "order_id": order_id,
            "rating": review.rating,
            "comment": review.comment,
            "sentiment": review.sentiment,
        }
        for review, order_id in zip(ordered, picked, strict=True)
    ]


def _table_exists(conn: Connection, name: str) -> bool:
    query = text("SELECT to_regclass(current_schema() || '.' || :name) IS NOT NULL")
    return bool(conn.execute(query, {"name": name}).scalar())


def _execute_script(conn: Connection, path: Path) -> None:
    """Run a multi-statement SQL file, skipping psql meta-commands."""
    lines = path.read_text(encoding="utf-8").splitlines()
    script = "\n".join(line for line in lines if not line.startswith("\\"))
    # A raw cursor without parameters keeps any '%' in the file literal.
    with conn.connection.cursor() as cursor:
        cursor.execute(script)


def _row_count(conn: Connection, table: str) -> int | None:
    """Rows in a table, or None when it does not exist."""
    if not _table_exists(conn, table):
        return None
    return conn.execute(text(f"SELECT count(*) FROM {table}")).scalar()


def _restore_dump(conn: Connection, dump: Path) -> None:
    search_path = conn.execute(text("SELECT current_setting('search_path')")).scalar()
    _execute_script(conn, dump)
    # pg_dump output empties search_path for the session.
    conn.execute(text("SELECT set_config('search_path', :value, false)"), {"value": search_path})


def ensure_raw_tables(conn: Connection, dump: Path = RAW_DUMP) -> None:
    """Keep the original tables as `raw_*`, restoring the dump when there is no source.

    Empty tables hold no source data, as on a volume initialized with the schema only.
    A partly filled source stops the run, because restoring would discard its rows.
    """
    if all(_table_exists(conn, f"raw_{table}") for table in RAW_TABLES):
        return
    counts = [_row_count(conn, table) for table in RAW_TABLES]
    if any(counts) and not all(counts):
        raise RuntimeError(f"Origem incompleta em {RAW_TABLES}: {counts}")
    if not all(counts):
        conn.execute(text("DROP TABLE IF EXISTS reviews, orders, products, customers"))
        _restore_dump(conn, dump)
    for table in RAW_TABLES:
        conn.execute(text(f"ALTER TABLE {table} RENAME TO raw_{table}"))


def _load_customers_products(conn: Connection) -> None:
    conn.execute(text("""
        INSERT INTO customers (customer_id, name, email, city, state, segment)
        SELECT customer_id::uuid, name, email, city, state, segment FROM raw_customers
    """))
    products = conn.execute(text("""
        SELECT product_id, name, category, price, brand FROM raw_products
    """)).mappings().all()
    conn.execute(
        text("""
            INSERT INTO products (product_id, name, category, macro_category, price, brand)
            VALUES (CAST(:product_id AS uuid), :name, :category, :macro_category,
                    ROUND(CAST(:price AS numeric), 2), :brand)
        """),
        [{**row, "macro_category": macro_category(row["category"])} for row in products],
    )


def _load_orders(conn: Connection, rng: random.Random) -> None:
    order_ids = conn.execute(
        text("SELECT order_id FROM raw_orders ORDER BY order_id")
    ).scalars().all()
    dates = simulated_dates(len(order_ids), rng)
    conn.execute(text("CREATE TEMP TABLE order_dates (order_id text, created_at timestamptz)"
                      " ON COMMIT DROP"))
    conn.execute(
        text("INSERT INTO order_dates VALUES (:order_id, :created_at)"),
        [{"order_id": oid, "created_at": at} for oid, at in zip(order_ids, dates, strict=True)],
    )
    conn.execute(text("""
        INSERT INTO orders (order_id, customer_id, product_id, qty, total, status, payment, created_at)
        SELECT o.order_id::uuid, o.customer_id::uuid, o.product_id::uuid, o.qty::integer,
               o.qty::integer * p.price, o.status, o.payment, d.created_at
        FROM raw_orders o
        JOIN products p ON p.product_id = o.product_id::uuid
        JOIN order_dates d ON d.order_id = o.order_id
    """))


def _load_reviews(conn: Connection, reviews: Sequence[Review], rng: random.Random) -> None:
    delivered = conn.execute(
        text("SELECT order_id FROM orders WHERE status = 'delivered'")
    ).scalars().all()
    conn.execute(
        text("""
            INSERT INTO reviews (review_id, order_id, rating, comment, sentiment)
            VALUES (CAST(:review_id AS uuid), CAST(:order_id AS uuid),
                    :rating, :comment, :sentiment)
        """),
        link_reviews(reviews, delivered, rng),
    )


def _validate(conn: Connection, expected_reviews: int) -> None:
    for table in RAW_TABLES:
        raw = conn.execute(text(f"SELECT count(*) FROM raw_{table}")).scalar()
        final = conn.execute(text(f"SELECT count(*) FROM {table}")).scalar()
        if raw != final:
            raise RuntimeError(f"{table}: {raw} linhas na origem, {final} no destino")
    loaded = conn.execute(text("SELECT count(*) FROM reviews")).scalar()
    if loaded != expected_reviews:
        raise RuntimeError(f"reviews: {expected_reviews} no arquivo, {loaded} no destino")


def prepare(engine: Engine, reviews_file: Path = REVIEWS_FILE) -> None:
    """Rebuild the final tables in one transaction."""
    reviews = load_reviews(reviews_file)
    rng = random.Random(SEED)
    with engine.begin() as conn:
        ensure_raw_tables(conn)
        conn.execute(text("DROP TABLE IF EXISTS reviews, orders, products, customers"))
        _execute_script(conn, INIT_SQL)
        _load_customers_products(conn)
        _load_orders(conn, rng)
        _load_reviews(conn, reviews, rng)
        _validate(conn, len(reviews))


def main() -> int:
    try:
        prepare(create_db_engine())
    except Exception as exc:  # noqa: BLE001 - CLI boundary reports any failure
        print(f"Falha na preparação; nada foi alterado: {exc}", file=sys.stderr)
        return 1
    print("Base preparada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
