# Data Dictionary

## Canonical event layer

| Field | Meaning | Important caveat |
|---|---|---|
| `event_time` | Event timestamp from the source | No timezone contract is provided |
| `event_type` | `view`, `cart`, or `purchase` | Purchase is an item event, not an order |
| `product_id` | Anonymised product identifier | Product catalogue attributes are limited |
| `category_code` | Hierarchical product category | Missing values become `unknown` |
| `brand` | Product brand | Missing values become `unknown` |
| `price` | Source price/value field | Currency, tax, discounts, and refunds are not documented |
| `user_id` | Persistent anonymised user identifier | Identity stitching quality is unknown |
| `source_session_id` | Session string supplied by source | Retained for audit; unsafe as the canonical key |
| `analytics_session_id` | User plus reconstructed session sequence | New session after more than 30 minutes inactivity |

## Session funnel mart

Grain: one reconstructed analytics session.

| Field | Definition |
|---|---|
| `qualified_session` | Session has at least one view |
| `reached_cart` | Session has both a view and cart event |
| `reached_purchase` | Session has both a view and purchase event |
| `reached_purchase_after_cart` | Session has view, cart, and purchase events; this session-level flag does not guarantee same-product order |
| `purchase_item_value` | Sum of purchase-row prices in the session; not audited revenue |
| `is_first_observed_session` | First reconstructed session for that user inside the data window |

## Session-product mart

Grain: one product inside one reconstructed session.

| Field | Definition |
|---|---|
| `ordered_view_to_cart` | First cart occurs at or after the first view for the same product/session |
| `ordered_full_funnel` | First purchase occurs at or after the first cart, which occurs at or after first view |
| `purchase_without_cart` | Purchase exists without any same-product cart in the session |
| `cart_without_view` | Cart exists without any same-product view in the session |
| `representative_price` | Price associated with the latest event for that session-product |
| `category_level_1` | First segment of hierarchical category code |

## Experiment mart

`mart_experiment_eligible_users` contains real observational covariates for a user's first qualifying high-price computer-cart session. It is used only to calibrate the generated experiment.

The `experiment_*.parquet` files are synthetic and excluded from Git. Their fields include assignment, experiment day, post-assignment conversion/value, latency/error guardrails, and strictly pre-period covariates. Generated JSON summaries are committed for review.
