import json
from pathlib import Path

import duckdb

from src.experimentation.validate_design import build_power_curve, run_aa_calibration

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "shopflow.duckdb"


def test_product_path_flags_are_never_null() -> None:
    with duckdb.connect(str(DATABASE_PATH), read_only=True) as connection:
        null_flags = connection.execute(
            """
            SELECT count(*)
            FROM mart_session_product
            WHERE ordered_view_to_cart IS NULL
                OR ordered_full_funnel IS NULL
                OR purchase_without_cart IS NULL
                OR cart_without_view IS NULL
            """
        ).fetchone()[0]
    assert null_flags == 0


def test_session_threshold_conclusion_is_stable() -> None:
    with duckdb.connect(str(DATABASE_PATH), read_only=True) as connection:
        minimum, maximum = connection.execute(
            """
            SELECT min(view_to_purchase_rate), max(view_to_purchase_rate)
            FROM mart_session_threshold_sensitivity
            """
        ).fetchone()
    assert maximum - minimum < 0.003


def test_preperiod_does_not_count_qualifying_session() -> None:
    with duckdb.connect(str(DATABASE_PATH), read_only=True) as connection:
        first_eligible_users = connection.execute(
            """
            SELECT count(*)
            FROM mart_experiment_eligible_users
            WHERE prior_sessions = 0
            """
        ).fetchone()[0]
    assert first_eligible_users == 8_233


def test_power_requirement_decreases_with_larger_effect() -> None:
    curve = build_power_curve()
    assert curve["total_users"].is_monotonic_decreasing
    assert curve.loc[curve["relative_lift"] == 0.05, "total_users"].iloc[0] == 16_782


def test_aa_calibration_is_close_to_nominal_alpha() -> None:
    calibration = run_aa_calibration()
    assert 0.04 <= calibration["false_positive_rate_alpha_0_05"] <= 0.06
    assert abs(calibration["mean_estimated_effect"]) < 0.001


def test_generated_healthy_experiment_has_expected_trust_checks() -> None:
    result_path = PROJECT_ROOT / "reports" / "generated" / "experiment_healthy_results.json"
    result = json.loads(result_path.read_text())
    assert result["srm_p_value"] >= 0.001
    assert result["max_absolute_covariate_smd"] < 0.1
    assert result["primary_conversion"]["ci_low"] > 0
