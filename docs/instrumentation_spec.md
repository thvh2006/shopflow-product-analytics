# Instrumentation and Data Contract

## Objective

Measure assignment, actual feature delivery, checkout progression, failure modes, and order outcomes without using post-treatment fields to redefine the primary population.

## Identity and clocks

- `experiment_user_id`: stable authenticated or first-party pseudonymous user key.
- `assignment_id`: immutable assignment record created before exposure.
- `analytics_session_id`: server-issued session ID with documented expiry.
- All event timestamps in UTC, with client timestamp, server receipt timestamp, and schema version.
- Retries carry an idempotency key so ingestion can deduplicate exact delivery attempts.

## Required events

| Event | Required fields | Purpose |
|---|---|---|
| `experiment_assigned` | user, assignment, variant, eligibility version, assigned_at | ITT denominator and SRM |
| `confidence_panel_requested` | assignment, session, product, request_at | Feature-service coverage |
| `confidence_panel_rendered` | assignment, session, product, render_at, component flags | Actual exposure and render latency |
| `confidence_panel_interacted` | assignment, component, action | Diagnostic engagement only |
| `checkout_started` | assignment, cart, product set, total value | Primary funnel diagnostic |
| `shipping_quote_shown` | assignment, quote, promise, region class | Delivery mechanism |
| `payment_attempted` | assignment, payment class, attempt number | Payment progression |
| `checkout_error` | assignment, step, stable error code, retryable | Technical guardrail/root cause |
| `order_created` | assignment, order, item IDs, value, currency | Primary outcome source |
| `order_cancelled` / `item_refunded` | assignment, order/item, reason, value | Long-term guardrail |

Sensitive payment credentials, raw addresses, and free-text error messages must never enter analytics events.

## Metric contracts

### Eligibility

The user enters the experiment at the first valid server-side add-to-cart for a qualifying computer product and high-price threshold. Eligibility is frozen at assignment; later behaviour cannot remove the user.

### Primary ITT conversion

Distinct assigned users with a qualifying product in a completed order during the session divided by all assigned eligible users. Variant is read from the assignment service, not reconstructed from exposure logs.

### Feature delivery

Rendered panels divided by treatment assignments. This is a diagnostic metric. Conditioning the primary analysis on successful render would break randomisation.

### Guardrails

- Render latency p50/p95 and checkout latency p50/p95.
- Checkout error users per assigned user.
- Payment failure users per payment-attempt user.
- Seven-day cancellation/refund value per order value.

## Automated quality checks

1. Assignment uniqueness: one active variant per user and experiment.
2. Allocation: SRM by overall sample, platform, country class, and experiment day.
3. Join rate: at least 99.5% of outcome events join to an assignment when eligible.
4. Schema completeness: required-field missingness below 0.1%.
5. Temporal validity: no exposure or outcome timestamp before assignment.
6. Cross-variant contamination: control render rate below 0.1%.
7. Idempotency: duplicate assignment and order-event rate reported separately.
8. A/A calibration: nominal false-positive and confidence-interval coverage monitored before launch.

## Ownership and incident response

- Experiment platform owns assignment and SRM alerts.
- Feature engineering owns request/render/error telemetry.
- Checkout team owns order, payment, and cancellation contracts.
- Analytics owns metric versioning and reconciliation.

Any unresolved SRM, cross-variant render, or assignment/outcome join failure blocks the decision memo regardless of outcome significance.
