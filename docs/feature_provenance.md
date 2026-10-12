# Feature provenance and decision-time policy

This register explains where portfolio-facing features come from and what was known at the decision point. The machine-readable source is [`reports/feature_provenance.csv`](../reports/feature_provenance.csv).

| Feature | Family | Raw source | Transformation | Cutoff | Fit scope | Role | Main risk |
|---|---|---|---|---|---|---|---|
| prior_sessions | history | mart_session_funnel | Count sessions before first_eligible_at | strictly before eligible session | none | experiment covariate | low |
| prior_cart_sessions | history | mart_session_funnel.reached_cart | Count prior sessions reaching cart | strictly before eligible session | none | audit | low |
| prior_purchase_sessions | history | mart_session_funnel.reached_purchase | Count prior sessions reaching purchase | strictly before eligible session | none | experiment covariate | low |
| prior_purchase_item_value | history | mart_session_funnel.purchase_item_value | Sum prior purchase item value | strictly before eligible session | none | CUPED covariate | low |
| prior_purchase_rate | history | prior purchase and session counts | prior_purchase_sessions / prior_sessions | strictly before eligible session | none | experiment covariate | low |
| returning_user | history | prior_sessions | 1 when prior_sessions > 0 | strictly before eligible session | none | heterogeneity slice | low |
| price_quartile | product context | representative_price | Portfolio quantile bucket Q1-Q4 | current viewed/carted product | analysis population | association model | medium: conditions on carted products |
| category_level_1 | product context | category_code | Top-level category parsed from taxonomy | current product | none | association model | low |
| activity_month | time control | session_started_at | YYYY-MM calendar month | current session | none | association control | medium if used across future periods |
| converted_same_product | outcome | ordered full-funnel events | Any ordered full-funnel product in eligible session | after assignment | none | target only | high if used as predictor |

## Governance rules

1. Outcomes and post-decision events are targets or evaluation evidence, never predictors.
2. Learned bins, imputers, encoders, cutoffs, and feature eligibility are fitted before locked evaluation.
3. Anonymous fields are described by source and statistical behavior; business meanings are not invented.
4. Proxy and fairness risks remain explicit even when protected attributes are unavailable.
5. The notebook is explanatory; reusable code and tests remain the implementation source of truth.
