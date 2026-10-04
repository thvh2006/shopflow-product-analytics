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

The public event source has no treatment assignment. The repository therefore generates a labelled synthetic experiment population by bootstrapping eligible-user covariates and simulating post-assignment outcomes with a fixed seed. It must not be described as a real ShopFlow experiment.

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

The observed eligible-user baseline is 42.94%. Detecting a 5% relative lift (2.15 percentage points) with 80% power, two-sided alpha 0.05, and equal allocation requires approximately 8,391 users per arm. The synthetic run uses 20,000 assigned users, above this floor.

No peeking-based early stop is allowed. The primary metric is evaluated once after the runtime and sample-size requirements are met.

## Trust checks before effect interpretation

1. Sample ratio mismatch must have `p >= 0.001`.
2. Absolute standardised mean difference must be below 0.10 for preregistered pre-period covariates.
3. Assignment and outcome telemetry must reconcile to one row per eligible user.
4. Guardrails and daily effects must be reviewed even if the primary metric is significant.

If SRM fails, the experiment is invalid until the loss mechanism is found; a significant outcome does not rescue it.

## Decision rule

Recommend a staged launch only when the primary confidence interval excludes zero in the favourable direction, the observed lift is practically meaningful, SRM and balance checks pass, and no guardrail crosses its threshold. Secondary metrics support interpretation but cannot override a failed primary or trust check.
