"""Layer boundaries: no SQL in the UI, no Streamlit in `src/`."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL = re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE)\b\s|sqlalchemy\.text|\btext\(|read_sql")


def _python_files(*folders: str) -> list[Path]:
    return [path for folder in folders for path in (ROOT / folder).rglob("*.py")]


def test_app_has_files_to_check():
    assert _python_files("app")


def test_no_sql_in_app():
    offenders = [str(path) for path in _python_files("app") if SQL.search(path.read_text(encoding="utf-8"))]
    assert offenders == []


def test_pages_do_not_call_queries_directly():
    files = [*(ROOT / "app" / "pages").glob("*.py"), ROOT / "app" / "Home.py"]
    offenders = [
        str(path)
        for path in files
        if "src.queries" in (text := path.read_text(encoding="utf-8")) or "import queries" in text
    ]
    assert offenders == []


def test_src_does_not_import_streamlit():
    offenders = [
        str(path)
        for path in _python_files("src")
        if re.search(r"^\s*(import|from)\s+streamlit", path.read_text(encoding="utf-8"), re.M)
    ]
    assert offenders == []
