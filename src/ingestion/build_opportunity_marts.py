from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "shopflow.duckdb"
SQL_PATH = PROJECT_ROOT / "sql" / "03_opportunity_analysis.sql"


def main() -> None:
    with duckdb.connect(str(DATABASE_PATH)) as connection:
        connection.execute(SQL_PATH.read_text())
        tables = connection.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name LIKE 'mart_%'
            ORDER BY table_name
            """
        ).fetchall()
    print(f"Built {len(tables)} analytics marts in {DATABASE_PATH}")


if __name__ == "__main__":
    main()
