# Robustness, Alternative Explanations, and Model Check

## Conclusion

The high-price post-cart gap survives changes in session threshold, funnel definition, broad product controls, calendar month, and user status. That makes it a strong prioritisation signal. It remains observational and does not reveal the underlying mechanism.

## Session-boundary sensitivity

| Inactivity threshold | Sessions | View→cart | View→purchase | P95 session duration |
|---|---:|---:|---:|---:|
| 15 minutes | 518,944 | 8.26% | 4.47% | 537 sec |
| 30 minutes | 504,679 | 8.42% | 4.61% | 762 sec |
| 60 minutes | 494,301 | 8.55% | 4.70% | 1,049 sec |

Longer boundaries merge more events and mechanically raise conversion slightly. The main purchase rate moves only 0.23 percentage points from the strictest to loosest definition, so the overall diagnosis is not an artefact of choosing 30 minutes.

The median reconstructed session duration is zero under every threshold because most sessions contain one event. Duration is therefore a poor “engagement” metric in this source and is not used as a primary KPI.

## Funnel-definition sensitivity

| Definition | Viewed units | Carted units | Purchased units | Cart→purchase |
|---|---:|---:|---:|---:|
| Session, any event order | 503,168 | 42,374 | 21,794 | 51.43% |
| Session, ordered events | 503,168 | 42,059 | 21,601 | 51.36% |
| Session-product, ordered events | 644,699 | 49,502 | 23,595 | 47.66% |

Event ordering barely changes the session-level rate, while enforcing same-product identity reduces completion by 3.7 points. The looser session funnel is valid for visit-level conversion; the stricter grain is more appropriate for diagnosing a product intervention.

## Observation-window correction

Naive observed return is 8.90% within 7 days and 10.47% within 30 days. Restricting denominators to users whose first session leaves a complete follow-up window gives:

- 7-day return: 8.96% among 390,930 mature users.
- 30-day return: 10.73% among 331,649 mature users.

The correction is modest but directionally important. These rates still measure return within the dataset window, not acquisition retention.

## Time trend

Full-month view-to-purchase rises from 3.97% in October to 5.20% in January, then stays at 5.13% in February. September is partial and excluded from trend conclusions. Possible explanations include seasonality, assortment, marketing mix, instrumentation, or customer learning; the event source cannot distinguish them.

Calendar month is included in the adjusted completion model so the price result is not merely a later-month mix shift.

## Adjusted cart-completion model

Population: 49,502 already-carted session-products from 36,406 users. Outcome: strict same-product purchase after cart. Standard errors are clustered by user.

Relative to Q1 and controlling for broad category, calendar month, and first/returning status:

| Price quartile | Adjusted odds ratio | 95% CI | p-value |
|---|---:|---:|---:|
| Q2 | 0.90 | 0.84–0.95 | <0.001 |
| Q3 | 0.69 | 0.65–0.74 | <0.001 |
| Q4 | 0.62 | 0.58–0.67 | <0.001 |

Q4's adjusted odds are approximately 37.7% lower than Q1's. The model's Cox–Snell pseudo-R² is only 0.016, meaning the available fields explain little of individual completion. This weak predictive fit is a reason to add checkout and qualitative data—not a reason to overstate the price coefficient.

The model is associational and conditioned on cart behaviour. It must not be interpreted as the causal effect of changing price.

## Journey timing contradicts a simple low-intent story

Q4 users reach cart faster than Q1 users: median 41 versus 49 seconds from first same-product view. Among purchasers, median cart-to-purchase is also faster (78 versus 96 seconds). Yet Q4 completes less often.

This combination is consistent with a polarised journey: decisive buyers move quickly, while a larger remainder exits after demonstrating intent. It makes post-cart uncertainty plausible, but checkout errors, stock, financing, delivery, and cart-as-wishlist behaviour remain alternatives.

## Scenario-based opportunity ranking

If each qualifying subcategory merely reached the portfolio's strict 47.66% cart-completion benchmark, video cards have the largest mathematical gap: approximately 885 additional item purchases and 351,935 source-value units on the observed cart volume. CPUs rank second at roughly 259 purchases and 52,860 value units.

This is a prioritisation scenario, not a forecast. It assumes the benchmark is attainable and ignores substitution, capacity, refunds, margins, and causal intervention effectiveness.
