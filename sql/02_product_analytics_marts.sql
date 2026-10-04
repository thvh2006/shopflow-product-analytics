CREATE OR REPLACE TABLE mart_session_funnel AS
WITH sequenced AS (
    SELECT
        *,
        row_number() OVER (
            PARTITION BY user_id ORDER BY session_started_at, analytics_session_id
        ) AS observed_session_number,
        lag(session_started_at) OVER (
            PARTITION BY user_id ORDER BY session_started_at, analytics_session_id
        ) AS previous_session_started_at
    FROM sessions
)
SELECT
    *,
    observed_session_number = 1 AS is_first_observed_session,
    date_diff('day', previous_session_started_at, session_started_at) AS days_since_previous_session,
    viewed AS qualified_session,
    carted AND viewed AS reached_cart,
    purchased AND viewed AS reached_purchase,
    purchased AND carted AND viewed AS reached_purchase_after_cart
FROM sequenced;

CREATE OR REPLACE TABLE mart_session_product AS
WITH product_path AS (
    SELECT
        analytics_session_id,
        user_id,
        product_id,
        max_by(category_code, event_time) AS category_code,
        max_by(brand, event_time) AS brand,
        max_by(price, event_time) AS representative_price,
        min(event_time) FILTER (WHERE event_type = 'view') AS first_view_at,
        min(event_time) FILTER (WHERE event_type = 'cart') AS first_cart_at,
        min(event_time) FILTER (WHERE event_type = 'purchase') AS first_purchase_at,
        count(*) FILTER (WHERE event_type = 'view') AS view_events,
        count(*) FILTER (WHERE event_type = 'cart') AS cart_events,
        count(*) FILTER (WHERE event_type = 'purchase') AS purchase_events
    FROM event_stream
    GROUP BY analytics_session_id, user_id, product_id
)
SELECT
    *,
    first_view_at IS NOT NULL AS viewed,
    first_cart_at IS NOT NULL AS carted,
    first_purchase_at IS NOT NULL AS purchased,
    coalesce(
        first_view_at IS NOT NULL AND first_cart_at >= first_view_at,
        false
    ) AS ordered_view_to_cart,
    coalesce(
        first_view_at IS NOT NULL
            AND first_cart_at >= first_view_at
            AND first_purchase_at >= first_cart_at,
        false
    ) AS ordered_full_funnel,
    coalesce(
        first_purchase_at IS NOT NULL AND first_cart_at IS NULL,
        false
    ) AS purchase_without_cart,
    coalesce(
        first_cart_at IS NOT NULL AND first_view_at IS NULL,
        false
    ) AS cart_without_view,
    CASE
        WHEN category_code = 'unknown' THEN 'unknown'
        ELSE split_part(category_code, '.', 1)
    END AS category_level_1
FROM product_path;

CREATE OR REPLACE TABLE mart_daily_product_metrics AS
SELECT
    cast(session_started_at AS DATE) AS activity_date,
    count(*) AS analytics_sessions,
    count(*) FILTER (WHERE qualified_session) AS qualified_sessions,
    count(*) FILTER (WHERE reached_cart) AS cart_sessions,
    count(*) FILTER (WHERE reached_purchase) AS purchase_sessions,
    count(*) FILTER (WHERE reached_purchase_after_cart) AS purchase_after_cart_sessions,
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
    round(
        count(*) FILTER (WHERE reached_purchase_after_cart)
        / nullif(count(*) FILTER (WHERE reached_cart), 0),
        4
    ) AS cart_to_purchase_rate,
    round(sum(purchase_item_value), 2) AS observed_purchase_item_value
FROM mart_session_funnel
GROUP BY activity_date
ORDER BY activity_date;

CREATE OR REPLACE TABLE mart_category_funnel AS
SELECT
    category_level_1,
    count(*) FILTER (WHERE viewed) AS viewed_session_products,
    count(*) FILTER (WHERE ordered_view_to_cart) AS ordered_cart_session_products,
    count(*) FILTER (WHERE ordered_full_funnel) AS ordered_purchase_session_products,
    round(
        count(*) FILTER (WHERE ordered_view_to_cart)
        / nullif(count(*) FILTER (WHERE viewed), 0),
        4
    ) AS view_to_cart_rate,
    round(
        count(*) FILTER (WHERE ordered_full_funnel)
        / nullif(count(*) FILTER (WHERE ordered_view_to_cart), 0),
        4
    ) AS cart_to_purchase_rate,
    round(
        sum(representative_price) FILTER (WHERE ordered_full_funnel),
        2
    ) AS ordered_purchase_item_value
FROM mart_session_product
GROUP BY category_level_1
ORDER BY viewed_session_products DESC;

CREATE OR REPLACE TABLE mart_price_band_funnel AS
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
    min(representative_price) AS minimum_price,
    max(representative_price) AS maximum_price,
    count(*) AS viewed_session_products,
    count(*) FILTER (WHERE ordered_view_to_cart) AS ordered_cart_session_products,
    count(*) FILTER (WHERE ordered_full_funnel) AS ordered_purchase_session_products,
    round(
        count(*) FILTER (WHERE ordered_view_to_cart) / count(*),
        4
    ) AS view_to_cart_rate,
    round(
        count(*) FILTER (WHERE ordered_full_funnel)
        / nullif(count(*) FILTER (WHERE ordered_view_to_cart), 0),
        4
    ) AS cart_to_purchase_rate
FROM banded
GROUP BY price_band
ORDER BY minimum_price;

CREATE OR REPLACE TABLE mart_user_lifecycle AS
WITH user_sessions AS (
    SELECT
        user_id,
        count(*) AS observed_sessions,
        count(*) FILTER (WHERE reached_purchase) AS purchase_sessions,
        min(session_started_at) AS first_observed_session_at,
        max(session_started_at) AS last_observed_session_at,
        round(sum(purchase_item_value), 2) AS observed_purchase_item_value,
        min(session_started_at) FILTER (
            WHERE observed_session_number > 1
        ) AS first_return_session_at
    FROM mart_session_funnel
    GROUP BY user_id
)
SELECT
    *,
    date_diff('day', first_observed_session_at, last_observed_session_at) AS observed_user_span_days,
    date_diff('day', first_observed_session_at, first_return_session_at) AS days_to_first_return,
    first_return_session_at IS NOT NULL
        AND first_return_session_at <= first_observed_session_at + INTERVAL 7 DAY
        AS returned_within_7d,
    first_return_session_at IS NOT NULL
        AND first_return_session_at <= first_observed_session_at + INTERVAL 30 DAY
        AS returned_within_30d
FROM user_sessions;

CREATE OR REPLACE TABLE mart_weekly_cohort_return AS
WITH user_weeks AS (
    SELECT DISTINCT
        user_id,
        date_trunc('week', session_started_at)::DATE AS activity_week
    FROM mart_session_funnel
),
cohorted AS (
    SELECT
        user_id,
        min(activity_week) OVER (PARTITION BY user_id) AS cohort_week,
        activity_week
    FROM user_weeks
),
cohort_size AS (
    SELECT cohort_week, count(DISTINCT user_id) AS cohort_users
    FROM cohorted
    GROUP BY cohort_week
)
SELECT
    activity.cohort_week,
    date_diff('week', activity.cohort_week, activity.activity_week) AS weeks_since_first_observed,
    size.cohort_users,
    count(DISTINCT activity.user_id) AS returning_users,
    round(count(DISTINCT activity.user_id) / size.cohort_users, 4) AS cohort_return_rate
FROM cohorted activity
JOIN cohort_size size USING (cohort_week)
GROUP BY activity.cohort_week, weeks_since_first_observed, size.cohort_users
ORDER BY activity.cohort_week, weeks_since_first_observed;
