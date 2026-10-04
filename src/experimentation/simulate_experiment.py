import argparse
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "shopflow.duckdb"
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "processed"
SEED = 20_261_004


def _sigmoid(value: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-value))


def load_calibration_population() -> pd.DataFrame:
    with duckdb.connect(str(DATABASE_PATH), read_only=True) as connection:
        return connection.execute(
            """
            SELECT
                user_id,
                prior_sessions,
                prior_purchase_sessions,
                prior_purchase_item_value,
                prior_purchase_rate,
                CASE WHEN prior_sessions > 0 THEN 1 ELSE 0 END AS returning_user
            FROM mart_experiment_eligible_users
            ORDER BY user_id
            """
        ).df()


def simulate_experiment(
    population: pd.DataFrame,
    sample_size: int = 20_000,
    scenario: str = "healthy",
) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    stable_population = population.sort_values("user_id").reset_index(drop=True)
    sampled = stable_population.sample(
        sample_size, replace=True, random_state=SEED
    ).reset_index(drop=True)
    sampled["experiment_user_id"] = np.arange(1, sample_size + 1)
    sampled["variant"] = np.where(rng.random(sample_size) < 0.5, "treatment", "control")
    sampled["experiment_day"] = rng.integers(1, 15, sample_size)

    prior_signal = np.log1p(sampled["prior_purchase_sessions"].to_numpy())
    returning = sampled["returning_user"].to_numpy()
    # The intercept is calibrated so the synthetic control is close to the
    # 42.9% conversion observed in the eligible user cohort.
    baseline_logit = -0.33 + (0.22 * returning) + (0.12 * prior_signal)
    treatment = (sampled["variant"] == "treatment").to_numpy()
    novelty_multiplier = np.where(sampled["experiment_day"].to_numpy() <= 2, 1.18, 1.0)
    treatment_log_odds = 0.12 * novelty_multiplier
    conversion_probability = _sigmoid(baseline_logit + treatment * treatment_log_odds)
    sampled["converted"] = rng.binomial(1, conversion_probability)

    pre_value = np.log1p(sampled["prior_purchase_item_value"].clip(lower=0).to_numpy())
    purchase_value = np.maximum(
        0,
        285 + (32 * pre_value) + rng.normal(0, 125, sample_size),
    )
    sampled["purchase_item_value"] = sampled["converted"] * purchase_value
    sampled["checkout_latency_ms"] = np.maximum(
        150,
        rng.normal(880 + (18 * treatment), 170, sample_size),
    )
    sampled["error_event"] = rng.binomial(1, 0.006 + (0.0005 * treatment))

    if scenario == "srm":
        # A deliberately broken telemetry scenario: treatment rows are lost more often.
        keep_probability = np.where(treatment, 0.88, 0.995)
        sampled = sampled.loc[rng.random(sample_size) < keep_probability].copy()
    elif scenario != "healthy":
        raise ValueError("scenario must be 'healthy' or 'srm'")

    sampled["scenario"] = scenario
    return sampled


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["healthy", "srm"], default="healthy")
    parser.add_argument("--sample-size", type=int, default=20_000)
    arguments = parser.parse_args()

    population = load_calibration_population()
    result = simulate_experiment(population, arguments.sample_size, arguments.scenario)
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIRECTORY / f"experiment_{arguments.scenario}.parquet"
    result.to_parquet(output_path, index=False)
    print(f"Wrote {len(result):,} synthetic rows to {output_path}")


if __name__ == "__main__":
    main()
