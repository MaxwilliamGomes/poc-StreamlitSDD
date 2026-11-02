"""Database engine configured from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, Engine, create_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_VARIABLES = (
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
)


class MissingConfigError(RuntimeError):
    """A required environment variable is not set."""


def create_db_engine(schema: str | None = None) -> Engine:
    """Create a pooled engine; `schema` isolates integration tests from `public`."""
    load_dotenv(PROJECT_ROOT / ".env")
    missing = [name for name in REQUIRED_VARIABLES if not os.environ.get(name)]
    if missing:
        raise MissingConfigError(f"Variáveis ausentes no .env: {', '.join(missing)}")

    url = URL.create(
        "postgresql+psycopg2",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        database=os.environ["POSTGRES_DB"],
    )
    connect_args: dict[str, str | int] = {"connect_timeout": 3}
    if schema:
        connect_args["options"] = f"-csearch_path={schema}"
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)
