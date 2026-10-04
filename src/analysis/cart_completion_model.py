import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.genmod.families import Binomial

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "shopflow.duckdb"
OUTPUT_DIRECTORY = PROJECT_ROOT / "reports" / "generated"


def load_cart_population() -> pd.DataFrame:
    with duckdb.connect(str(DATABASE_PATH), read_only=True) as connection:
        frame = connection.execute(
            """
            WITH thresholds AS (
                SELECT
                    quantile_cont(representative_price, 0.25) FILTER (WHERE viewed) AS p25,
                    quantile_cont(representative_price, 0.50) FILTER (WHERE viewed) AS p50,
                    quantile_cont(representative_price, 0.75) FILTER (WHERE viewed) AS p75
                FROM mart_session_product
            )
            SELECT
                product.user_id,
                coalesce(product.ordered_full_funnel, false)::INTEGER AS converted,
                product.category_level_1,
                CASE
                    WHEN product.representative_price <= threshold.p25 THEN 'Q1'
                    WHEN product.representative_price <= threshold.p50 THEN 'Q2'
                    WHEN product.representative_price <= threshold.p75 THEN 'Q3'
                    ELSE 'Q4'
                END AS price_quartile,
                CASE WHEN session.is_first_observed_session THEN 0 ELSE 1 END AS returning_user,
                strftime(session.session_started_at, '%Y-%m') AS activity_month
            FROM mart_session_product product
            JOIN mart_session_funnel session USING (analytics_session_id, user_id)
            CROSS JOIN thresholds threshold
            WHERE product.ordered_view_to_cart
            ORDER BY product.user_id, product.analytics_session_id, product.product_id
            """
        ).df()
    frame["converted"] = frame["converted"].astype("int64")
    frame["returning_user"] = frame["returning_user"].astype("int64")
    for column in ["category_level_1", "price_quartile", "activity_month"]:
        frame[column] = frame[column].fillna("unknown").astype(str)
    return frame


def fit_model(frame: pd.DataFrame):
    formula = (
        'converted ~ C(price_quartile, Treatment(reference="Q1")) '
        "+ returning_user + C(category_level_1) + C(activity_month)"
    )
    return smf.glm(formula=formula, data=frame, family=Binomial()).fit(
        cov_type="cluster", cov_kwds={"groups": frame["user_id"]}
    )


def coefficient_table(model) -> pd.DataFrame:
    confidence = model.conf_int()
    output = pd.DataFrame(
        {
            "term": model.params.index,
            "coefficient": model.params.values,
            "odds_ratio": np.exp(model.params.values),
            "ci_low": np.exp(confidence[0].to_numpy()),
            "ci_high": np.exp(confidence[1].to_numpy()),
            "p_value": model.pvalues.values,
        }
    )
    return output


def build_opportunity_ranking() -> pd.DataFrame:
    with duckdb.connect(str(DATABASE_PATH), read_only=True) as connection:
        return connection.execute(
            """
            WITH segment AS (
                SELECT
                    category_code,
                    count(*) FILTER (WHERE viewed) AS viewed_session_products,
                    count(*) FILTER (WHERE ordered_view_to_cart) AS ordered_carts,
                    count(*) FILTER (WHERE ordered_full_funnel) AS ordered_purchases,
                    median(representative_price) FILTER (
                        WHERE ordered_view_to_cart
                    ) AS median_cart_price
                FROM mart_session_product
                GROUP BY category_code
            ),
            scored AS (
                SELECT
                    *,
                    ordered_purchases / nullif(ordered_carts, 0) AS cart_completion_rate,
                    greatest(0, 0.4766 - ordered_purchases / nullif(ordered_carts, 0))
                        AS gap_to_portfolio_benchmark
                FROM segment
                WHERE viewed_session_products >= 1000 AND ordered_carts >= 100
            )
            SELECT
                *,
                round(ordered_carts * gap_to_portfolio_benchmark, 1)
                    AS scenario_incremental_purchases,
                round(
                    ordered_carts * gap_to_portfolio_benchmark * median_cart_price,
                    2
                ) AS scenario_incremental_item_value
            FROM scored
            ORDER BY scenario_incremental_item_value DESC
            """
        ).df()


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    frame = load_cart_population()
    model = fit_model(frame)
    coefficients = coefficient_table(model)
    coefficients.to_csv(OUTPUT_DIRECTORY / "cart_completion_model.csv", index=False)

    price_terms = coefficients.loc[coefficients["term"].str.contains("price_quartile")]
    diagnostics = {
        "analysis_population": len(frame),
        "unique_users": int(frame["user_id"].nunique()),
        "outcome_rate": float(frame["converted"].mean()),
        "pseudo_r_squared_cs": float(model.pseudo_rsquared(kind="cs")),
        "price_quartile_adjusted_odds_ratios": price_terms.to_dict(orient="records"),
        "interpretation": (
            "Conditional association among already-carted session-products; not a causal "
            "price effect because the analysis conditions on post-view cart behaviour."
        ),
    }
    (OUTPUT_DIRECTORY / "cart_completion_model.json").write_text(
        json.dumps(diagnostics, indent=2)
    )

    ranking = build_opportunity_ranking()
    ranking.to_csv(OUTPUT_DIRECTORY / "opportunity_ranking.csv", index=False)
    print(json.dumps(diagnostics, indent=2))
    print("\nTop opportunity scenarios")
    print(ranking.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
