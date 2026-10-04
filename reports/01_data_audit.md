# Data Audit

## Scope

The source contains 885,129 raw events from 407,283 anonymised users between 2020-09-24 11:57:06 and 2021-02-28 23:59:09. The taxonomy is limited to 793,748 views, 54,035 cart events, and 37,346 purchase-item events.

After removing 655 exact duplicates, the canonical event stream contains 884,474 rows. No behavioural deduplication is imposed because repeated events may be genuine activity.

## Identity and session audit

The supplied `user_session` field is unsafe as a primary session key:

- 214 source-session strings map to more than one user.
- 14,070 user/session pairs cross a calendar date.
- The maximum source-session duration exceeds 150 days.
- 162 canonical events have no source-session ID.

The project reconstructs sessions per user using a 30-minute inactivity boundary and retains the source field for traceability. This produces 504,679 analytics sessions and preserves all 884,474 canonical events.

The 30-minute rule is a defensible product-analytics convention, not ground truth. Sensitivity to other thresholds remains a useful extension.

## Missing dimensions

- 236,047 canonical events have unknown category code (26.7%).
- 212,232 canonical events have unknown brand (24.0%).

Unknown values are retained as explicit segments. Dropping them would overstate coverage and could change the apparent category mix.

## Monetary interpretation

Purchase events appear item-grained and provide no audited order identifier, currency contract, tax, discount, shipping, refund, or cancellation fields. The summed price on purchase rows is therefore named **observed purchase-item value**, never revenue or GMV.

## Journey exceptions

At the session-product grain, the ordered path contains 644,699 viewed combinations, 49,502 ordered view-to-cart combinations, and 23,595 ordered full funnels. There are also 2,969 purchase-without-cart and 645 cart-without-view combinations.

These exceptions are exposed instead of deleted. They may represent cross-session journeys, incomplete telemetry, direct-buy flows, or session-boundary artefacts. Ordered-funnel metrics deliberately use strict timestamps and do not force every purchase into a monotonic path.

## Lifecycle limitation

The first record in the dataset is not necessarily a user's acquisition date. “New” means first observed in this window, and 7/30-day metrics are labelled observed return rather than true retention. Cohorts near the end of the window are right-censored.

## Audit conclusion

The data is suitable for event-funnel diagnosis, segmentation, and hypothesis generation after reconstruction. It is not suitable for audited revenue reporting, causal product claims, or true customer-lifetime measurement without additional order, assignment, and acquisition data.
