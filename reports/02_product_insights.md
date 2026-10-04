# Product Insights and Prioritisation

## Executive finding

ShopFlow's clearest testable opportunity is not generic traffic growth. It is the post-cart decision for expensive computer products: users show strong intent by adding these products, but completion falls as price increases. The evidence justifies an experiment about purchase confidence; it does not prove the cause is trust, compatibility, delivery, or payment friction.

## 1. Overall funnel

Of 503,168 qualified sessions, 42,374 reached cart and 23,218 reached purchase. That is 8.42% view-to-cart, 4.61% view-to-purchase, and 51.43% purchase-after-cart among cart sessions.

This identifies both cart creation and cart completion as opportunities, but aggregate rates hide materially different behaviour by product and price.

## 2. Price reveals high intent followed by lower completion

At the strict session-product grain:

| Global price band | Viewed | Ordered carts | Purchases | View→cart | Cart→purchase |
|---|---:|---:|---:|---:|---:|
| Q1, up to 25.29 | 161,470 | 10,189 | 5,621 | 6.31% | 55.17% |
| Q2, 25.30–63.92 | 161,060 | 11,359 | 5,970 | 7.05% | 52.56% |
| Q3, 63.94–176.17 | 161,130 | 11,136 | 5,052 | 6.91% | 45.37% |
| Q4, at least 176.21 | 161,039 | 16,818 | 6,952 | 10.44% | 41.34% |

The highest-price quartile creates carts 65% more often than Q1 but completes them 13.8 percentage points less often. This is consistent with high purchase intent plus greater decision friction.

## 3. The price pattern persists inside computers

Product mix explains some of the aggregate pattern, so the analysis compares price bands within the largest category:

| Computer price band | Viewed | Ordered carts | Cart→purchase |
|---|---:|---:|---:|
| Q1 | 29,451 | 1,859 | 55.24% |
| Q2 | 36,437 | 3,204 | 48.69% |
| Q3 | 51,690 | 5,539 | 43.18% |
| Q4 | 96,947 | 14,255 | 41.16% |

The monotonic decline remains within one broad category, reducing—but not eliminating—the product-mix explanation.

Video cards dominate the opportunity: 72,108 viewed session-products, 11,713 ordered carts, 4,697 purchases, and 40.10% cart completion. They account for approximately 1.80 million in observed ordered purchase-item value. CPUs (35.11%), motherboards (39.27%), and power supplies (38.20%) show a similar post-cart gap, which is consistent with a compatibility/consideration mechanism worth testing.

## 4. Alternative explanations remain live

- Price may proxy stock, promotion, delivery, financing, or brand mix.
- A cart event may be a wishlist-like behaviour rather than immediate checkout intent.
- Missing category and brand data can distort segment comparisons.
- Session reconstruction can split long consideration journeys.
- The event source does not include checkout steps, payment failures, delivery promises, or qualitative reasons.

Accordingly, the proposed mechanism should be validated with checkout instrumentation and user research. The current data ranks an opportunity; it does not diagnose the user's internal reason.

## 5. Behavioural context

Returning observed sessions convert at 6.82% versus 4.07% for first-observed sessions, but this is selection, not a treatment effect. Users who return already differ in intent and familiarity.

Only 45,800 of 407,283 users have more than one reconstructed session. Observed return is 8.90% within 7 days and 10.47% within 30 days. These are lower-bound windowed behaviours, not true customer retention.

## 6. Prioritised hypothesis

**If** eligible users see concise compatibility, return, delivery, and payment reassurance immediately after adding a high-price computer product, **then** same-product purchase conversion will increase because the intervention reduces decision uncertainty at the point of demonstrated intent.

The target population contains 9,742 observed eligible users at their first qualifying session, with a 42.94% same-product conversion baseline. The proposed experiment is defined in `docs/experiment_preregistration.md`.

## Product recommendation before launch

1. Instrument checkout-start, payment failure, shipping quote, stock status, and panel exposure.
2. Validate the four reassurance messages with five to eight qualitative sessions.
3. Run the user-randomised test only for the preregistered eligible population.
4. Do not generalise a win to cheap products, non-computer categories, or revenue without a follow-up test.
