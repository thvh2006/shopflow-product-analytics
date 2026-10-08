import numpy as np
import pandas as pd
import pytest

from src.experimentation.analyze_experiment import analyze
from src.experimentation.simulate_experiment import simulate_experiment


def calibration_population(size: int = 2_000) -> pd.DataFrame:
    repeats = size // 5
    return pd.DataFrame(
        {
            "user_id": np.arange(1, repeats * 5 + 1),
            "prior_sessions": np.tile(np.arange(5), repeats),
            "prior_purchase_sessions": np.tile([0, 0, 1, 1, 2], repeats),
            "prior_purchase_item_value": np.tile([0, 0, 100, 200, 400], repeats),
            "prior_purchase_rate": np.tile([0, 0, 0.5, 0.33, 0.5], repeats),
            "returning_user": np.tile([0, 1, 1, 1, 1], repeats),
        }
    )


def test_simulation_is_reproducible() -> None:
    first = simulate_experiment(calibration_population(), sample_size=1_000)
    second = simulate_experiment(calibration_population(), sample_size=1_000)
    pd.testing.assert_frame_equal(first, second)


def test_simulation_is_independent_of_input_row_order() -> None:
    population = calibration_population()
    shuffled = population.sample(frac=1, random_state=42)
    expected = simulate_experiment(population, sample_size=1_000)
    actual = simulate_experiment(shuffled, sample_size=1_000)
    pd.testing.assert_frame_equal(expected, actual)


def test_healthy_assignment_has_no_srm() -> None:
    data = simulate_experiment(calibration_population(12_000), sample_size=10_000)
    result = analyze(data)
    assert result["srm_p_value"] > 0.001
    assert result["evidence_class"] == "simulation_only"
    assert result["duplicate_source_users"] == 0
    assert result["injected_treatment_log_odds"]["base"] == 0.12


def test_broken_telemetry_triggers_srm() -> None:
    data = simulate_experiment(
        calibration_population(12_000), sample_size=10_000, scenario="srm"
    )
    assert analyze(data)["srm_p_value"] < 0.001


def test_simulation_never_duplicates_calibration_users() -> None:
    data = simulate_experiment(calibration_population(), sample_size=1_500)
    assert data["user_id"].is_unique
    assert data["outcome_provenance"].eq("synthetic_injected_effect").all()


def test_simulation_rejects_resampling_beyond_unique_population() -> None:
    with pytest.raises(ValueError, match="exceeds the unique eligible-user population"):
        simulate_experiment(calibration_population(100), sample_size=101)
