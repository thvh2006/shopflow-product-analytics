CREATE OR REPLACE TABLE mart_session_threshold_sensitivity AS
WITH threshold_values AS (
    SELECT * FROM (VALUES (900), (1800), (3600)) AS values_table(threshold_seconds)
),
ordered AS (
    SELECT
        threshold.threshold_seconds,
        event.*,
        lag(event.event_time) OVER (
            PARTITION BY threshold.threshold_seconds, event.user_id
            ORDER BY event.event_time, event.event_type, event.product_id
        ) AS prior_event_time
    FROM events event
    CROSS JOIN threshold_values threshold
),
bounded AS (
    SELECT
        *,
        CASE
            WHEN prior_event_time IS NULL THEN 1
            WHEN date_diff('second', prior_event_time, event_time) > threshold_seconds THEN 1
            ELSE 0
        END AS new_session
    FROM ordered
),
numbered AS (
    SELECT
        *,
        sum(new_session) OVER (
            PARTITION BY threshold_seconds, user_id
            ORDER BY event_time, event_type, product_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS session_number
    FROM bounded
),
threshold_sessions AS (
    SELECT
        threshold_seconds,
        user_id,
        session_number,
        min(event_time) AS started_at,
        max(event_time) AS ended_at,
        bool_or(event_type = 'view') AS viewed,
        bool_or(event_type = 'cart') AS carted,
        bool_or(event_type = 'purchase') AS purchased
    FROM numbered
    GROUP BY threshold_seconds, user_id, session_number
)
SELECT
    threshold_seconds / 60 AS inactivity_minutes,
    count(*) AS analytics_sessions,
    count(*) FILTER (WHERE viewed) AS qualified_sessions,
    count(*) FILTER (WHERE viewed AND carted) AS cart_sessions,
    count(*) FILTER (WHERE viewed AND purchased) AS purchase_sessions,
    round(
        count(*) FILTER (WHERE viewed AND carted)
        / nullif(count(*) FILTER (WHERE viewed), 0),
        4
    ) AS view_to_cart_rate,
    round(
        count(*) FILTER (WHERE viewed AND purchased)
        / nullif(count(*) FILTER (WHERE viewed), 0),
        4
    ) AS view_to_purchase_rate,
    round(median(date_diff('second', started_at, ended_at)), 1) AS median_duration_seconds,
    round(quantile_cont(date_diff('second', started_at, ended_at), 0.95), 1)
        AS p95_duration_seconds
FROM threshold_sessions
GROUP BY threshold_seconds
ORDER BY threshold_seconds;

CREATE OR REPLACE TABLE mart_funnel_definition_sensitivity AS
WITH sequenced_events AS (
    SELECT
        *,
        max(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) OVER (
            PARTITION BY analytics_session_id
            ORDER BY event_time, event_type, product_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prior_view
    FROM event_stream
),
cart_marked AS (
    SELECT
        *,
        CASE WHEN event_type = 'cart' AND prior_view = 1 THEN 1 ELSE 0 END
            AS ordered_cart_event
    FROM sequenced_events
),
purchase_marked AS (
    SELECT
        *,
        max(ordered_cart_event) OVER (
            PARTITION BY analytics_session_id
            ORDER BY event_time, event_type, product_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prior_ordered_cart
    FROM cart_marked
),
ordered_sessions AS (
    SELECT
        analytics_session_id,
        bool_or(event_type = 'view') AS viewed,
        bool_or(ordered_cart_event = 1) AS ordered_cart,
        bool_or(event_type = 'purchase' AND prior_ordered_cart = 1) AS ordered_purchase
    FROM purchase_marked
    GROUP BY analytics_session_id
),
definitions AS (
    SELECT
        '01 session: any event order' AS funnel_definition,
        count(*) FILTER (WHERE qualified_session) AS viewed_units,
        count(*) FILTER (WHERE reached_cart) AS carted_units,
        count(*) FILTER (WHERE reached_purchase_after_cart) AS purchased_units
    FROM mart_session_funnel

    UNION ALL

    SELECT
        '02 session: ordered events' AS funnel_definition,
        count(*) FILTER (WHERE viewed) AS viewed_units,
        count(*) FILTER (WHERE ordered_cart) AS carted_units,
        count(*) FILTER (WHERE ordered_purchase) AS purchased_units
    FROM ordered_sessions

    UNION ALL

    SELECT
        '03 session-product: ordered events' AS funnel_definition,
        count(*) FILTER (WHERE viewed) AS viewed_units,
        count(*) FILTER (WHERE ordered_view_to_cart) AS carted_units,
        count(*) FILTER (WHERE ordered_full_funnel) AS purchased_units
    FROM mart_session_product
)
SELECT
    *,
    round(carted_units / nullif(viewed_units, 0), 4) AS view_to_cart_rate,
    round(purchased_units / nullif(carted_units, 0), 4) AS cart_to_purchase_rate,
    round(purchased_units / nullif(viewed_units, 0), 4) AS view_to_purchase_rate
FROM definitions
ORDER BY funnel_definition;

CREATE OR REPLACE TABLE mart_mature_user_return AS
WITH bounds AS (
    SELECT max(event_time) AS observation_ends_at FROM events
),
labelled AS (
    SELECT
        lifecycle.*,
        lifecycle.first_observed_session_at
            <= bounds.observation_ends_at - INTERVAL 7 DAY AS has_7d_observation,
        lifecycle.first_observed_session_at
            <= bounds.observation_ends_at - INTERVAL 30 DAY AS has_30d_observation
    FROM mart_user_lifecycle lifecycle
    CROSS JOIN bounds
)
SELECT
    '7 day' AS horizon,
    count(*) FILTER (WHERE has_7d_observation) AS eligible_users,
    count(*) FILTER (WHERE has_7d_observation AND returned_within_7d) AS returning_users,
    round(
        count(*) FILTER (WHERE has_7d_observation AND returned_within_7d)
        / nullif(count(*) FILTER (WHERE has_7d_observation), 0),
        4
    ) AS mature_return_rate
FROM labelled

UNION ALL

SELECT
    '30 day' AS horizon,
    count(*) FILTER (WHERE has_30d_observation) AS eligible_users,
    count(*) FILTER (WHERE has_30d_observation AND returned_within_30d) AS returning_users,
    round(
        count(*) FILTER (WHERE has_30d_observation AND returned_within_30d)
        / nullif(count(*) FILTER (WHERE has_30d_observation), 0),
        4
    ) AS mature_return_rate
FROM labelled;

CREATE OR REPLACE TABLE mart_monthly_product_metrics AS
SELECT
    date_trunc('month', session_started_at)::DATE AS activity_month,
    count(*) AS analytics_sessions,
    count(*) FILTER (WHERE qualified_session) AS qualified_sessions,
    count(*) FILTER (WHERE reached_cart) AS cart_sessions,
    count(*) FILTER (WHERE reached_purchase) AS purchase_sessions,
    round(
        count(*) FILTER (WHERE reached_cart)
        / nullif(count(*) FILTER (WHERE qualified_session), 0),
        4
    ) AS view_to_cart_rate,
    round(
        count(*) FILTER (WHERE reached_purchase)
        / nullif(count(*) FILTER (WHERE qualified_session), 0),
        4
    ) AS view_to_purchase_rate,
    min(session_started_at)::DATE AS first_observed_date,
    max(session_started_at)::DATE AS last_observed_date
FROM mart_session_funnel
GROUP BY activity_month
ORDER BY activity_month;

CREATE OR REPLACE TABLE mart_common_session_paths AS
WITH transitions AS (
    SELECT
        analytics_session_id,
        event_time,
        event_type,
        lag(event_type) OVER (
            PARTITION BY analytics_session_id
            ORDER BY event_time, event_type, product_id
        ) AS prior_event_type
    FROM event_stream
),
compressed AS (
    SELECT
        *,
        row_number() OVER (
            PARTITION BY analytics_session_id ORDER BY event_time, event_type
        ) AS transition_number
    FROM transitions
    WHERE prior_event_type IS NULL OR prior_event_type <> event_type
),
paths AS (
    SELECT
        analytics_session_id,
        string_agg(event_type, ' > ' ORDER BY transition_number)
            FILTER (WHERE transition_number <= 6) AS first_six_transitions,
        max(transition_number) AS transition_count
    FROM compressed
    GROUP BY analytics_session_id
)
SELECT
    paths.first_six_transitions
        || CASE WHEN paths.transition_count > 6 THEN ' > …' ELSE '' END AS session_path,
    count(*) AS sessions,
    count(*) FILTER (WHERE funnel.reached_purchase) AS purchase_sessions,
    round(
        count(*) FILTER (WHERE funnel.reached_purchase) / count(*),
        4
    ) AS purchase_rate
FROM paths
JOIN mart_session_funnel funnel USING (analytics_session_id)
GROUP BY session_path
ORDER BY sessions DESC;

CREATE OR REPLACE TABLE mart_price_time_to_action AS
WITH thresholds AS (
    SELECT
        quantile_cont(representative_price, 0.25) FILTER (WHERE viewed) AS p25,
        quantile_cont(representative_price, 0.50) FILTER (WHERE viewed) AS p50,
        quantile_cont(representative_price, 0.75) FILTER (WHERE viewed) AS p75
    FROM mart_session_product
),
banded AS (
    SELECT
        product.*,
        CASE
            WHEN representative_price <= p25 THEN 'Q1 lowest price'
            WHEN representative_price <= p50 THEN 'Q2 lower-middle price'
            WHEN representative_price <= p75 THEN 'Q3 upper-middle price'
            ELSE 'Q4 highest price'
        END AS price_band
    FROM mart_session_product product
    CROSS JOIN thresholds
    WHERE viewed
)
SELECT
    price_band,
    count(*) FILTER (WHERE ordered_view_to_cart) AS ordered_carts,
    round(median(date_diff('second', first_view_at, first_cart_at)) FILTER (
        WHERE ordered_view_to_cart
    ), 1) AS median_view_to_cart_seconds,
    round(quantile_cont(date_diff('second', first_view_at, first_cart_at), 0.90) FILTER (
        WHERE ordered_view_to_cart
    ), 1) AS p90_view_to_cart_seconds,
    count(*) FILTER (WHERE ordered_full_funnel) AS ordered_purchases,
    round(median(date_diff('second', first_cart_at, first_purchase_at)) FILTER (
        WHERE ordered_full_funnel
    ), 1) AS median_cart_to_purchase_seconds,
    round(quantile_cont(date_diff('second', first_cart_at, first_purchase_at), 0.90) FILTER (
        WHERE ordered_full_funnel
    ), 1) AS p90_cart_to_purchase_seconds
FROM banded
GROUP BY price_band
ORDER BY min(representative_price);
