"""Data-quality tests for the ShopFlow event foundation."""

from pathlib import Path

import duckdb
import pytest

DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "shopflow.duckdb"

pytestmark = pytest.mark.skipif(not DATABASE_PATH.exists(), reason="Local database not built")


@pytest.fixture(scope="module")
def connection():
    with duckdb.connect(DATABASE_PATH, read_only=True) as database:
        yield database


def test_source_scope(connection) -> None:
    raw_rows, users, first_event, last_event = connection.execute(
        """
        SELECT
            count(*),
            count(DISTINCT user_id),
            min(event_time),
            max(event_time)
        FROM raw_events
        """
    ).fetchone()
    assert raw_rows == 885_129
    assert users == 407_283
    assert first_event.isoformat(sep=" ") == "2020-09-24 11:57:06"
    assert last_event.isoformat(sep=" ") == "2021-02-28 23:59:09"


def test_event_taxonomy(connection) -> None:
    event_types = dict(
        connection.execute(
            "SELECT event_type, count(*) FROM raw_events GROUP BY event_type"
        ).fetchall()
    )
    assert event_types == {"view": 793_748, "cart": 54_035, "purchase": 37_346}


def test_exact_duplicates_are_removed(connection) -> None:
    raw_rows, canonical_rows = connection.execute(
        "SELECT (SELECT count(*) FROM raw_events), (SELECT count(*) FROM events)"
    ).fetchone()
    assert raw_rows - canonical_rows == 655


def test_analytics_session_key_is_unique(connection) -> None:
    rows, distinct_sessions = connection.execute(
        "SELECT count(*), count(DISTINCT analytics_session_id) FROM sessions"
    ).fetchone()
    assert rows == distinct_sessions == 504_679


def test_session_reconstruction_preserves_canonical_events(connection) -> None:
    canonical_rows, streamed_rows, session_event_rows = connection.execute(
        """
        SELECT
            (SELECT count(*) FROM events),
            (SELECT count(*) FROM event_stream),
            (SELECT sum(event_count) FROM sessions)
        """
    ).fetchone()
    assert canonical_rows == streamed_rows == session_event_rows


def test_every_event_has_an_analytics_session(connection) -> None:
    missing_sessions = connection.execute(
        "SELECT count(*) FROM event_stream WHERE analytics_session_id IS NULL"
    ).fetchone()[0]
    assert missing_sessions == 0


def test_product_marts_have_expected_grain(connection) -> None:
    sessions, session_products, users = connection.execute(
        """
        SELECT
            (SELECT count(*) FROM mart_session_funnel),
            (SELECT count(*) FROM mart_session_product),
            (SELECT count(*) FROM mart_user_lifecycle)
        """
    ).fetchone()
    assert sessions == 504_679
    assert session_products > sessions
    assert users == 407_283


def test_daily_metrics_reconcile_to_session_mart(connection) -> None:
    daily_sessions, total_sessions = connection.execute(
        """
        SELECT
            (SELECT sum(analytics_sessions) FROM mart_daily_product_metrics),
            (SELECT count(*) FROM mart_session_funnel)
        """
    ).fetchone()
    assert daily_sessions == total_sessions


def test_ordered_product_funnel_is_monotonic(connection) -> None:
    invalid_categories = connection.execute(
        """
        SELECT count(*)
        FROM mart_category_funnel
        WHERE ordered_purchase_session_products > ordered_cart_session_products
           OR ordered_cart_session_products > viewed_session_products
        """
    ).fetchone()[0]
    assert invalid_categories == 0


def test_cohort_return_rates_are_bounded(connection) -> None:
    invalid_rates = connection.execute(
        """
        SELECT count(*)
        FROM mart_weekly_cohort_return
        WHERE cohort_return_rate < 0 OR cohort_return_rate > 1
        """
    ).fetchone()[0]
    assert invalid_rates == 0
