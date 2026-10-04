"""Build the local DuckDB event foundation from the REES46 archive."""

from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ARCHIVE = PROJECT_ROOT / "data" / "raw" / "electronics-events.csv.gz"
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "shopflow.duckdb"
FOUNDATION_SQL = PROJECT_ROOT / "sql" / "01_event_foundation.sql"


def main() -> None:
    if not RAW_ARCHIVE.exists():
        raise FileNotFoundError(
            "Missing REES46 archive. Follow data/README.md before building the database."
        )

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    source_path = RAW_ARCHIVE.as_posix().replace("'", "''")

    with duckdb.connect(DATABASE_PATH) as connection:
        connection.execute(
            f"""
            CREATE OR REPLACE TABLE raw_events AS
            SELECT *
            FROM read_csv_auto('{source_path}', header = true)
            """
        )
        connection.execute(FOUNDATION_SQL.read_text(encoding="utf-8"))

        profile = connection.execute("SELECT * FROM data_quality_profile").fetchone()
        columns = [item[0] for item in connection.description]

    print("Built", DATABASE_PATH)
    for name, value in zip(columns, profile, strict=True):
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()
