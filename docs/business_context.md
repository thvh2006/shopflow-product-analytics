# Business Context

ShopFlow is a fictional e-commerce product team used to frame the analysis. The team wants to improve qualified-session purchase conversion without degrading order value or user trust.

## Stakeholders

- Product Manager: prioritise the next funnel intervention.
- Product Analyst: define trustworthy metrics and diagnose behaviour.
- Design and Engineering: understand the affected journey and instrumentation.
- Commercial team: protect purchase value and category mix.

## Decision sequence

1. Audit event and identity quality.
2. Reconstruct defensible sessions.
3. Locate funnel and retention opportunities.
4. Select one testable product hypothesis.
5. Specify assignment, eligibility, primary metric, guardrails, MDE, and duration.
6. Analyze a transparent synthetic experiment and issue a launch decision.

## Boundaries

- Observational associations will not be called causal effects.
- `purchase` rows represent purchased items; they do not expose a reliable order identifier.
- Source-session IDs are retained for audit but are not trusted as unique analytics sessions.
- ShopFlow is not REES46 and does not claim ownership of the source records.
