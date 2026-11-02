"""Integration fixtures: an isolated schema, never `public`."""

from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import Engine, text
from sqlalchemy.exc import OperationalError

from src.db import MissingConfigError, create_db_engine
from src.prepare_data import INIT_SQL, _execute_script

ZONE = ZoneInfo("America/Sao_Paulo")
SCHEMA_PREFIX = "test_dashboard_"


@pytest.fixture(scope="session")
def admin_engine() -> Engine:
    try:
        engine = create_db_engine()
        with engine.connect():
            pass
    except (OperationalError, MissingConfigError) as exc:
        pytest.skip(f"Postgres indisponível: {exc}")
    return engine


def _schema_engine(admin_engine: Engine) -> Iterator[Engine]:
    schema = f"{SCHEMA_PREFIX}{uuid4().hex}"
    with admin_engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_db_engine(schema=schema)
    try:
        yield engine
    finally:
        engine.dispose()
        with admin_engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))


@pytest.fixture
def empty_schema(admin_engine: Engine) -> Iterator[Engine]:
    yield from _schema_engine(admin_engine)


@pytest.fixture(scope="module")
def seeded(admin_engine: Engine) -> Iterator[Engine]:
    """Known rows: every expected KPI below is computed by hand."""
    for engine in _schema_engine(admin_engine):
        with engine.begin() as conn:
            _execute_script(conn, INIT_SQL)
            conn.execute(text("""
                INSERT INTO customers VALUES
                ('00000000-0000-0000-0000-00000000000a','Ana','a@x','X','SP','premium'),
                ('00000000-0000-0000-0000-00000000000b','Bia','b@x','Y','RJ','basic');
                INSERT INTO products VALUES
                ('00000000-0000-0000-0000-0000000000a1','Tenis','Shoes','Moda',100,'M'),
                ('00000000-0000-0000-0000-0000000000a2','Mouse','Computers','Tecnologia',50,'N');
            """))
            orders = [
                ("1", "a", "a1", 2, 200, "delivered", "pix", datetime(2026, 3, 10, 12, tzinfo=ZONE)),
                ("2", "a", "a2", 1, 50, "shipped", "boleto", datetime(2026, 3, 11, 12, tzinfo=ZONE)),
                ("3", "b", "a1", 1, 100, "cancelled", "pix", datetime(2026, 3, 12, 12, tzinfo=ZONE)),
                ("4", "b", "a2", 3, 150, "processing", "credit_card", datetime(2026, 3, 31, 23, 30, tzinfo=ZONE)),
                ("5", "b", "a2", 2, 100, "delivered", "pix", datetime(2026, 4, 1, 0, 30, tzinfo=ZONE)),
                ("6", "a", "a1", 1, 100, "delivered", "pix", datetime(2026, 2, 26, 12, tzinfo=ZONE)),
            ]
            conn.execute(
                text("""
                    INSERT INTO orders VALUES (CAST(:o AS uuid), CAST(:c AS uuid), CAST(:p AS uuid),
                                               :q, :t, :s, :m, :at)
                """),
                [
                    {
                        "o": f"00000000-0000-0000-0000-{int(oid):012d}",
                        "c": f"00000000-0000-0000-0000-00000000000{cust}",
                        "p": f"00000000-0000-0000-0000-0000000000{prod}",
                        "q": qty, "t": total, "s": status, "m": payment, "at": at,
                    }
                    for oid, cust, prod, qty, total, status, payment, at in orders
                ],
            )
            conn.execute(text("""
                INSERT INTO reviews VALUES
                ('00000000-0000-0000-0000-0000000000f1','00000000-0000-0000-0000-000000000001',5,'Bom','positive'),
                ('00000000-0000-0000-0000-0000000000f2','00000000-0000-0000-0000-000000000004',1,'Ruim','negative');
            """))
        yield engine


@pytest.fixture
def tmp_reviews(tmp_path: Path) -> Path:
    return tmp_path / "reviews.jsonl"
