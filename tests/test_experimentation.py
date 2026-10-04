import numpy as np
import pandas as pd

from src.experimentation.analyze_experiment import analyze
from src.experimentation.simulate_experiment import simulate_experiment


def calibration_population() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "user_id": np.arange(1, 101),
            "prior_sessions": np.tile(np.arange(5), 20),
            "prior_purchase_sessions": np.tile([0, 0, 1, 1, 2], 20),
            "prior_purchase_item_value": np.tile([0, 0, 100, 200, 400], 20),
            "prior_purchase_rate": np.tile([0, 0, 0.5, 0.33, 0.5], 20),
            "returning_user": np.tile([0, 1, 1, 1, 1], 20),
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
    data = simulate_experiment(calibration_population(), sample_size=10_000)
    assert analyze(data)["srm_p_value"] > 0.001


def test_broken_telemetry_triggers_srm() -> None:
    data = simulate_experiment(calibration_population(), sample_size=10_000, scenario="srm")
    assert analyze(data)["srm_p_value"] < 0.001
