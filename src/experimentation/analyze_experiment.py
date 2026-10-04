import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.genmod.families import Binomial
from statsmodels.stats.proportion import confint_proportions_2indep, proportions_ztest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIRECTORY = PROJECT_ROOT / "data" / "processed"
REPORT_DIRECTORY = PROJECT_ROOT / "reports" / "generated"


def _difference_in_means(
    treatment: pd.Series, control: pd.Series, confidence: float = 0.95
) -> dict[str, float]:
    difference = treatment.mean() - control.mean()
    standard_error = np.sqrt(treatment.var(ddof=1) / len(treatment) + control.var(ddof=1) / len(control))
    critical_value = stats.norm.ppf(1 - (1 - confidence) / 2)
    return {
        "difference": float(difference),
        "ci_low": float(difference - critical_value * standard_error),
        "ci_high": float(difference + critical_value * standard_error),
        "p_value": float(stats.ttest_ind(treatment, control, equal_var=False).pvalue),
    }


def _binary_effect(frame: pd.DataFrame) -> dict[str, float]:
    treatment = frame.loc[frame["variant"] == "treatment", "converted"]
    control = frame.loc[frame["variant"] == "control", "converted"]
    ci_low, ci_high = confint_proportions_2indep(
        int(treatment.sum()),
        len(treatment),
        int(control.sum()),
        len(control),
        method="newcomb",
        compare="diff",
    )
    return {
        "control_rate": float(control.mean()),
        "treatment_rate": float(treatment.mean()),
        "absolute_effect": float(treatment.mean() - control.mean()),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "control_n": len(control),
        "treatment_n": len(treatment),
    }


def analyze(data: pd.DataFrame) -> dict:
    treatment = data.loc[data["variant"] == "treatment"]
    control = data.loc[data["variant"] == "control"]
    observed = np.array([len(control), len(treatment)])
    expected = np.repeat(len(data) / 2, 2)
    srm_p_value = float(stats.chisquare(observed, expected).pvalue)

    successes = np.array([treatment["converted"].sum(), control["converted"].sum()])
    totals = np.array([len(treatment), len(control)])
    primary_p_value = float(proportions_ztest(successes, totals)[1])
    ci_low, ci_high = confint_proportions_2indep(
        successes[0], totals[0], successes[1], totals[1], method="newcomb", compare="diff"
    )
    treatment_rate = float(treatment["converted"].mean())
    control_rate = float(control["converted"].mean())

    pre_metric = data["prior_purchase_item_value"].astype(float)
    outcome = data["purchase_item_value"].astype(float)
    theta = float(np.cov(outcome, pre_metric, ddof=1)[0, 1] / np.var(pre_metric, ddof=1))
    adjusted = outcome - theta * (pre_metric - pre_metric.mean())
    adjusted_treatment = adjusted.loc[data["variant"] == "treatment"]
    adjusted_control = adjusted.loc[data["variant"] == "control"]

    daily = (
        data.groupby(["experiment_day", "variant"])["converted"]
        .mean()
        .unstack()
        .assign(absolute_effect=lambda frame: frame["treatment"] - frame["control"])
        .reset_index()
    )
    balance_columns = ["prior_sessions", "prior_purchase_rate", "prior_purchase_item_value"]
    balance = {}
    for column in balance_columns:
        pooled_sd = np.sqrt((treatment[column].var(ddof=1) + control[column].var(ddof=1)) / 2)
        balance[column] = float((treatment[column].mean() - control[column].mean()) / pooled_sd)

    model_frame = data.copy()
    model_frame["treatment"] = (model_frame["variant"] == "treatment").astype(int)
    model_frame["early_window"] = (model_frame["experiment_day"] <= 2).astype(int)
    returning_interaction = smf.glm(
        "converted ~ treatment * returning_user",
        data=model_frame,
        family=Binomial(),
    ).fit()
    novelty_interaction = smf.glm(
        "converted ~ treatment * early_window",
        data=model_frame,
        family=Binomial(),
    ).fit()
    heterogeneity = {
        "first_observed_users": _binary_effect(
            model_frame.loc[model_frame["returning_user"] == 0]
        ),
        "returning_users": _binary_effect(
            model_frame.loc[model_frame["returning_user"] == 1]
        ),
        "returning_interaction_p_value": float(
            returning_interaction.pvalues["treatment:returning_user"]
        ),
        "days_1_2": _binary_effect(model_frame.loc[model_frame["early_window"] == 1]),
        "days_3_14": _binary_effect(model_frame.loc[model_frame["early_window"] == 0]),
        "early_window_interaction_p_value": float(
            novelty_interaction.pvalues["treatment:early_window"]
        ),
        "warning": "Exploratory slices; interaction tests, not within-slice significance, assess heterogeneity.",
    }

    return {
        "scenario": str(data["scenario"].iloc[0]),
        "sample_size": len(data),
        "assignment": {"control": len(control), "treatment": len(treatment)},
        "srm_p_value": srm_p_value,
        "max_absolute_covariate_smd": float(max(abs(value) for value in balance.values())),
        "covariate_smd": balance,
        "primary_conversion": {
            "control_rate": control_rate,
            "treatment_rate": treatment_rate,
            "absolute_effect": treatment_rate - control_rate,
            "relative_lift": treatment_rate / control_rate - 1,
            "ci_low": float(ci_low),
            "ci_high": float(ci_high),
            "p_value": primary_p_value,
        },
        "purchase_value_per_eligible_user": _difference_in_means(
            treatment["purchase_item_value"], control["purchase_item_value"]
        ),
        "cuped_purchase_value_per_eligible_user": {
            **_difference_in_means(adjusted_treatment, adjusted_control),
            "theta": theta,
            "variance_reduction": float(1 - adjusted.var(ddof=1) / outcome.var(ddof=1)),
        },
        "guardrails": {
            "checkout_latency_ms": _difference_in_means(
                treatment["checkout_latency_ms"], control["checkout_latency_ms"]
            ),
            "error_rate": {
                "control": float(control["error_event"].mean()),
                "treatment": float(treatment["error_event"].mean()),
            },
        },
        "heterogeneity": heterogeneity,
        "daily_effect": daily.to_dict(orient="records"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["healthy", "srm"], default="healthy")
    arguments = parser.parse_args()
    data_path = PROCESSED_DIRECTORY / f"experiment_{arguments.scenario}.parquet"
    result = analyze(pd.read_parquet(data_path))
    REPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    output_path = REPORT_DIRECTORY / f"experiment_{arguments.scenario}_results.json"
    output_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
