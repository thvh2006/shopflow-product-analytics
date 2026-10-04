from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "shopflow.duckdb"
SQL_PATH = PROJECT_ROOT / "sql" / "04_robustness_and_journeys.sql"


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("Build the event foundation and product marts first.")
    with duckdb.connect(str(DATABASE_PATH)) as connection:
        connection.execute(SQL_PATH.read_text(encoding="utf-8"))
        tables = connection.execute(
            """
            SELECT table_name, estimated_size
            FROM duckdb_tables()
            WHERE table_name IN (
                'mart_session_threshold_sensitivity',
                'mart_funnel_definition_sensitivity',
                'mart_mature_user_return',
                'mart_monthly_product_metrics',
                'mart_common_session_paths',
                'mart_price_time_to_action'
            )
            ORDER BY table_name
            """
        ).fetchall()
    for table_name, row_count in tables:
        print(f"Built {table_name}: {row_count:,} rows")


if __name__ == "__main__":
    main()
