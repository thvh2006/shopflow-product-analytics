"""Build product analytics marts after the event foundation exists."""

from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "shopflow.duckdb"
MART_SQL = PROJECT_ROOT / "sql" / "02_product_analytics_marts.sql"


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("Run src/ingestion/build_event_database.py first.")

    with duckdb.connect(DATABASE_PATH) as connection:
        connection.execute(MART_SQL.read_text(encoding="utf-8"))
        mart_counts = connection.execute(
            """
            SELECT 'mart_session_funnel', count(*) FROM mart_session_funnel
            UNION ALL
            SELECT 'mart_session_product', count(*) FROM mart_session_product
            UNION ALL
            SELECT 'mart_user_lifecycle', count(*) FROM mart_user_lifecycle
            """
        ).fetchall()

    for table_name, row_count in mart_counts:
        print(f"Built {table_name}: {row_count:,} rows")


if __name__ == "__main__":
    main()
