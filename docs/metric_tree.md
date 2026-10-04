# Product Metric Tree

## Goal

Increase completed purchases from qualified shopping sessions while protecting purchase value and experience quality.

## North-star outcome

**Qualified-session purchase conversion**

Numerator: analytics sessions with at least one purchase event.  
Denominator: analytics sessions with at least one product view.

This is a behavioural proxy, not company-wide revenue conversion.

## Diagnostic metrics

- View-to-cart session conversion.
- Cart-to-purchase session conversion.
- Ordered product-level view → cart → purchase completion.
- Median time from first view to first cart and first purchase.
- Products viewed, carted, and purchased per session.
- Return within 7 and 30 days after a user's first observed session.
- Purchase-item value per purchasing session.

## Segmentation dimensions

- New versus returning user at session start.
- Category and brand coverage.
- Price band defined from observed quantiles.
- Session depth and session duration.
- Day of week and hour, with coverage caveats.

## Experiment framework

- Primary: qualified-session purchase conversion.
- Secondary: cart-to-purchase conversion and purchase-item value per eligible user.
- Guardrails: synthetic error rate, checkout latency, cancellation proxy, and extreme item-value movement.
- Trust checks: sample ratio mismatch, assignment balance, missing telemetry, novelty/primacy, and multiple-metric interpretation.

## Goal → signal → metric mapping

| Product goal | Behavioural signal | Decision metric | Role |
|---|---|---|---|
| Help qualified shoppers complete a purchase | Eligible user purchases the same qualifying product | Same-product purchase users / assigned eligible users | Primary OEC proxy |
| Move users through checkout | Checkout start and step completion after assignment | Step conversion per assigned user | Diagnostic |
| Protect commercial value | Purchase-item value including zero for non-purchasers | Mean value per assigned eligible user | Secondary |
| Avoid slowing checkout | Assignment-to-checkout latency | Mean plus p50/p95 latency difference | Guardrail |
| Avoid technical harm | Stable error events after assignment | Error users / assigned users | Guardrail |
| Trust the comparison | Assignment and telemetry remain balanced | SRM, join rate, missingness, cross-variant exposure | Data quality |

## Denominator rules

- Primary and guardrail denominators are frozen at assignment.
- Failed treatment render does not remove a treatment user from intention-to-treat.
- Post-assignment clicks never define eligibility or analysis segments.
- Value includes zero for eligible non-purchasers; converter-only value is diagnostic because treatment can change who converts.
- User is the randomisation and inference unit; item rows are aggregated before the experiment comparison.

## HEART coverage and gaps

- **Task success:** ordered cart/purchase and experiment conversion are supported.
- **Engagement:** product/cart activity is supported but session depth contains post-outcome events and is descriptive only.
- **Retention:** observed return is supported with censoring caveats.
- **Adoption:** unsupported because acquisition and feature-eligible population before launch are not observed.
- **Happiness:** unsupported because no attitudinal or satisfaction measure exists.
