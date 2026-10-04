# Root-Cause Hypothesis Matrix

The event stream locates a post-cart gap but cannot identify the user's reason. This matrix prevents the team from confusing a plausible story with an observed fact.

| Hypothesis | Existing evidence | Evidence against / ambiguity | New signal needed | Testable product response |
|---|---|---|---|---|
| Compatibility uncertainty | CPUs, motherboards, power supplies, and video cards all show low completion; these products have interdependent specifications | The source has no configuration or search-query data | Compatibility-check usage, incompatible-cart flags, support contacts, interviews | Inline compatibility status and explanation |
| Price/payment anxiety | Completion declines monotonically by global price quartile and within computers | High price proxies category, brand, promotion, and stock | Payment-method availability, financing eligibility, price changes, failed authorisations | Financing/payment reassurance, price-lock message |
| Delivery/returns uncertainty | Expensive items plausibly carry greater delivery and return risk | No shipping region, promise, or return event exists | Shipping quote, delivery promise, return-policy opens, cancellations | Upfront delivery and return summary |
| Stock or fulfilment failure | Cart may succeed even when downstream stock fails | No inventory snapshot or checkout-step event exists | Stock status at exposure, checkout errors, back-order state | Real-time stock confirmation |
| Cart as wishlist/comparison | High-value cart creation is unusually strong; cart may represent save-for-later intent | Same-session Q4 purchasers move quickly, suggesting at least some immediate purchase intent | Save-list events, cross-session cart persistence, price-alert use | Explicit save/compare flow rather than checkout persuasion |
| Promotion/brand mix | Completion differs substantially by high-price brand; month conversion also changes | Brand missingness is 24%; promotions are absent | Discount, campaign, acquisition source, brand margin | Segment-specific merchandising, not a universal UX change |
| Checkout performance/error | A drop after cart can be technical rather than psychological | No checkout start, page latency, payment error, or crash events | Step-level telemetry and client/server error codes | Performance/error remediation before persuasion |

## Current decision

The purchase-confidence panel is selected as a **bundle test** covering compatibility, returns, delivery, and payment protection. If it wins, a follow-up component test is needed to learn which message causes the effect. If it loses, the result does not falsify every root-cause hypothesis because treatment strength and message relevance may be insufficient.
