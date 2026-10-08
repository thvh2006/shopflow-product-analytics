# Experiment Preregistration

## Decision and mechanism

Test a compact **purchase-confidence panel** after an eligible product is added to cart. The panel explains compatibility checks, return terms, delivery timing, and secure-payment protection without interrupting checkout.

The observational diagnosis is not evidence that this interface will work. It only identifies a plausible friction point: high-price computer items create carts frequently but complete less often. Random assignment is required to estimate the interface's causal effect.

## Population and assignment

- Unit of randomisation: user.
- Eligibility: first observed session in which the user views and then carts a computer product in the highest global price quartile (price above 176.17 in source units).
- Assignment: 50/50, stable by user, control versus purchase-confidence panel.
- Exposure: immediately after the qualifying add-to-cart event.
- Planned runtime: 14 complete days and at least 16,782 eligible users.
- Analysis: intention to treat; one row per assigned eligible user.

The public event source has no treatment assignment. The repository therefore
generates a labelled synthetic experiment population by sampling eligible users
without replacement and simulating post-assignment outcomes with a fixed seed. Each
source user may appear at most once. The injected base effect is 0.12 log-odds and is
stored in the generated data. This must not be described as a real ShopFlow experiment.

## Metrics

### Primary

Eligible-user same-product purchase conversion during the qualifying session.

### Secondary

- Purchase-item value per eligible user, including zero for non-purchasers.
- CUPED-adjusted purchase-item value using pre-experiment purchase-item value only.

### Guardrails

- Checkout latency: do not ship if the upper confidence bound exceeds +50 ms.
- Error-event rate: investigate a relative increase greater than 20% or an absolute increase greater than 0.2 percentage points.
- Daily effect stability: inspect for an effect limited to the first two days.

## Power and stopping

The observed eligible-user baseline is 42.94%. Detecting a 5% relative lift (2.15
percentage points) with 80% power, two-sided alpha 0.05, and equal allocation requires
approximately 8,391 users per arm. Only 9,742 unique eligible users are available in
the source, so the synthetic demonstration is below this planning floor. No resampling
is used to manufacture additional users.

No peeking-based early stop is allowed. The primary metric is evaluated once after the runtime and sample-size requirements are met.

## Trust checks before effect interpretation

1. Sample ratio mismatch must have `p >= 0.001`.
2. Absolute standardised mean difference must be below 0.10 for preregistered pre-period covariates.
3. Assignment and outcome telemetry must reconcile to one row per eligible user.
4. Guardrails and daily effects must be reviewed even if the primary metric is significant.

If SRM fails, the experiment is invalid until the loss mechanism is found; a significant outcome does not rescue it.

## Decision rule

For a **real** experiment, consider a staged launch only when the planned sample is
reached, the primary confidence interval excludes zero in the favourable direction,
the observed lift is practically meaningful, trust checks pass, and no guardrail
crosses its threshold. A synthetic run never receives launch authority regardless of
its p-value.

## Estimand and analysis details

- Estimand: average intention-to-treat effect among users assigned at their first qualifying high-price computer cart during the experiment window.
- Binary effect: difference in user-level conversion proportions with a two-sided z-test and Newcombe confidence interval.
- Continuous value: Welch difference in means. Zero is retained for non-purchasers; converter-only value is not a decision metric.
- CUPED: linear adjustment using only pre-assignment purchase-item value, centred on the pooled mean. Both adjusted and unadjusted estimates are reported.
- Standard error unit: user, matching randomisation. Product/item rows are aggregated before comparison.
- Alpha: 0.05 for the single primary outcome. Secondary and exploratory results do not receive launch authority.

## Missing data and non-compliance

- Missing assignment record: exclude from the experiment dataset and trigger reconciliation failure; never infer variant from page content.
- Assigned but panel not rendered: retain in assigned variant for ITT and report render coverage separately.
- Outcome telemetry unavailable differentially by variant: stop interpretation and investigate SRM/join-rate failures.
- User has multiple qualifying products: retain one user-level assignment and count conversion if any qualifying product is purchased under the prespecified definition.
- Cross-device identity failure: analyse by assignment identity and document expected dilution; do not stitch with post-outcome behaviour.

## Exploratory analyses

- First-observed versus returning status, defined before assignment.
- Days 1–2 versus days 3–14 for temporal stability.
- Component type and brand only if pre-period coverage and sample size are adequate.

Heterogeneity is evaluated with a treatment-by-segment interaction. “Significant in one subgroup and not significant in another” is not accepted as evidence that effects differ.

## Production readiness gate

Before the A/B test, run a live A/A using the same eligibility trigger, assignment service, event contracts, and scorecard. Confirm allocation, cross-variant exposure, assignment/outcome join rates, metric variance, and false-positive calibration. The repository's Monte Carlo A/A validates code behaviour only.
