# Product Metric Tree — Draft

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
