# Solution Prioritisation

## Decision principle

The first experiment should maximise learning about the post-cart mechanism while remaining small enough to isolate, instrument, and reverse. Scores below are decision aids, not measured facts.

Scales:

- Reach: 1 (narrow) to 5 (most eligible users).
- Expected impact: 1 (weak mechanism) to 5 (directly addresses observed gap).
- Evidence confidence: 1 (speculative) to 5 (supported by current and external evidence).
- Effort/risk: 1 (small/reversible) to 5 (large, operationally risky).
- Priority score: `reach × impact × confidence ÷ effort`.

| Option | Reach | Impact | Confidence | Effort/risk | Score | Decision |
|---|---:|---:|---:|---:|---:|---|
| Purchase-confidence panel | 5 | 3 | 3 | 2 | 22.5 | Test first |
| Compatibility checker | 3 | 5 | 3 | 5 | 9.0 | Instrument and prototype next |
| Financing/payment message | 4 | 3 | 2 | 3 | 8.0 | Needs payment eligibility data |
| Checkout performance remediation | 5 | 5 | 1 | 4 | 6.3 | Diagnose errors before scoping |
| Saved-cart reminder | 4 | 2 | 2 | 3 | 5.3 | Different session-level hypothesis |
| Broad discount | 5 | 4 | 1 | 5 | 4.0 | Reject as first test; margin and causality risk |

## Why the panel wins the first-test slot

- It reaches the full eligible group without needing a complete product-compatibility graph.
- It can expose separate component interactions for compatibility, delivery, returns, and payment, creating diagnostic evidence.
- It is reversible and has explicit latency/error guardrails.
- It does not change price or inventory, which would introduce commercial and supply-side mechanisms.

## Treatment definition

After a qualifying add-to-cart, treatment shows a compact panel with four independently instrumented elements:

1. compatibility status or a neutral “check compatibility” path;
2. expected delivery range;
3. concise return coverage;
4. secure-payment and eligible instalment information.

Control retains the existing cart experience. The experiment tests the bundle. It does not support claiming that any individual message caused the effect.

## Kill criteria before launch

- Checkout instrumentation cannot reconcile assignment to order outcomes.
- Panel render adds more than 50 ms to the preregistered checkout latency metric.
- Eligibility requires client-side fields with material missingness or variant-dependent availability.
- Legal/commercial owners cannot verify the return, delivery, or payment claims.
