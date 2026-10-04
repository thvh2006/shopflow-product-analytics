import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIRECTORY = PROJECT_ROOT / "reports" / "generated"
SEED = 20_261_004
BASELINE = 0.4294


def build_power_curve() -> pd.DataFrame:
    analysis = NormalIndPower()
    rows = []
    for relative_lift in [0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10]:
        treatment_rate = BASELINE * (1 + relative_lift)
        effect_size = proportion_effectsize(BASELINE, treatment_rate)
        users_per_arm = analysis.solve_power(
            effect_size=effect_size,
            alpha=0.05,
            power=0.80,
            ratio=1,
            alternative="two-sided",
        )
        rows.append(
            {
                "relative_lift": relative_lift,
                "absolute_lift": treatment_rate - BASELINE,
                "users_per_arm": int(np.ceil(users_per_arm)),
                "total_users": int(np.ceil(users_per_arm) * 2),
            }
        )
    return pd.DataFrame(rows)


def run_aa_calibration(iterations: int = 5_000, users_per_arm: int = 5_000) -> dict:
    rng = np.random.default_rng(SEED)
    control = rng.binomial(users_per_arm, BASELINE, iterations)
    treatment = rng.binomial(users_per_arm, BASELINE, iterations)
    control_rate = control / users_per_arm
    treatment_rate = treatment / users_per_arm
    pooled = (control + treatment) / (2 * users_per_arm)
    standard_error = np.sqrt(pooled * (1 - pooled) * (2 / users_per_arm))
    z_score = np.divide(
        treatment_rate - control_rate,
        standard_error,
        out=np.zeros_like(treatment_rate),
        where=standard_error > 0,
    )
    p_values = 2 * stats.norm.sf(np.abs(z_score))
    return {
        "iterations": iterations,
        "users_per_arm": users_per_arm,
        "false_positive_rate_alpha_0_05": float(np.mean(p_values < 0.05)),
        "mean_estimated_effect": float(np.mean(treatment_rate - control_rate)),
        "effect_sd": float(np.std(treatment_rate - control_rate, ddof=1)),
        "p_value_deciles": np.quantile(p_values, np.arange(0.1, 1.0, 0.1)).tolist(),
    }


def build_srm_sensitivity(total_assigned: int = 20_000) -> pd.DataFrame:
    assigned_per_arm = total_assigned // 2
    rows = []
    for treatment_loss_rate in [0, 0.005, 0.01, 0.02, 0.05, 0.10]:
        control_observed = assigned_per_arm
        treatment_observed = round(assigned_per_arm * (1 - treatment_loss_rate))
        observed = np.array([control_observed, treatment_observed])
        expected = np.repeat(observed.sum() / 2, 2)
        rows.append(
            {
                "treatment_telemetry_loss_rate": treatment_loss_rate,
                "control_observed": control_observed,
                "treatment_observed": treatment_observed,
                "srm_p_value": float(stats.chisquare(observed, expected).pvalue),
                "fails_0_001_threshold": bool(
                    stats.chisquare(observed, expected).pvalue < 0.001
                ),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    power = build_power_curve()
    power.to_csv(OUTPUT_DIRECTORY / "power_curve.csv", index=False)
    srm = build_srm_sensitivity()
    srm.to_csv(OUTPUT_DIRECTORY / "srm_sensitivity.csv", index=False)
    calibration = run_aa_calibration()
    (OUTPUT_DIRECTORY / "aa_calibration.json").write_text(json.dumps(calibration, indent=2))
    print("Power curve")
    print(power.to_string(index=False))
    print("\nA/A calibration")
    print(json.dumps(calibration, indent=2))
    print("\nSRM sensitivity")
    print(srm.to_string(index=False))


if __name__ == "__main__":
    main()
