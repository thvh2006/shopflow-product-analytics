CREATE OR REPLACE TABLE events AS
SELECT DISTINCT
    event_time::TIMESTAMP AS event_time,
    event_type::VARCHAR AS event_type,
    product_id::BIGINT AS product_id,
    category_id::BIGINT AS category_id,
    category_code::VARCHAR AS category_code,
    brand::VARCHAR AS brand,
    price::DOUBLE AS price,
    user_id::BIGINT AS user_id,
    user_session::VARCHAR AS source_session_id
FROM raw_events;

CREATE OR REPLACE TABLE event_stream AS
WITH ordered AS (
    SELECT
        *,
        lag(event_time) OVER (
            PARTITION BY user_id
            ORDER BY event_time, event_type, product_id
        ) AS previous_event_time
    FROM events
),
session_boundaries AS (
    SELECT
        *,
        CASE
            WHEN previous_event_time IS NULL THEN 1
            WHEN date_diff('second', previous_event_time, event_time) > 1800 THEN 1
            ELSE 0
        END AS starts_new_session
    FROM ordered
),
numbered AS (
    SELECT
        *,
        sum(starts_new_session) OVER (
            PARTITION BY user_id
            ORDER BY event_time, event_type, product_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS analytics_session_number
    FROM session_boundaries
)
SELECT
    concat(user_id::VARCHAR, '-', analytics_session_number::VARCHAR) AS analytics_session_id,
    analytics_session_number,
    event_time,
    event_type,
    product_id,
    category_id,
    coalesce(category_code, 'unknown') AS category_code,
    coalesce(brand, 'unknown') AS brand,
    price,
    user_id,
    source_session_id,
    previous_event_time,
    starts_new_session
FROM numbered;

CREATE OR REPLACE TABLE sessions AS
SELECT
    analytics_session_id,
    user_id,
    min(event_time) AS session_started_at,
    max(event_time) AS session_ended_at,
    date_diff('second', min(event_time), max(event_time)) AS session_duration_seconds,
    count(*) AS event_count,
    count(DISTINCT product_id) AS products_seen,
    bool_or(event_type = 'view') AS viewed,
    bool_or(event_type = 'cart') AS carted,
    bool_or(event_type = 'purchase') AS purchased,
    count(*) FILTER (WHERE event_type = 'view') AS view_events,
    count(*) FILTER (WHERE event_type = 'cart') AS cart_events,
    count(*) FILTER (WHERE event_type = 'purchase') AS purchase_item_events,
    round(sum(price) FILTER (WHERE event_type = 'purchase'), 2) AS purchase_item_value
FROM event_stream
GROUP BY analytics_session_id, user_id;

CREATE OR REPLACE TABLE data_quality_profile AS
SELECT
    (SELECT count(*) FROM raw_events) AS raw_rows,
    (SELECT count(*) FROM events) AS canonical_rows,
    (SELECT count(*) FROM raw_events) - (SELECT count(*) FROM events) AS exact_duplicate_rows,
    count(*) FILTER (WHERE source_session_id IS NULL) AS missing_source_session_rows,
    count(*) FILTER (WHERE category_code = 'unknown') AS unknown_category_rows,
    count(*) FILTER (WHERE brand = 'unknown') AS unknown_brand_rows,
    count(DISTINCT user_id) AS users,
    count(DISTINCT analytics_session_id) AS analytics_sessions,
    min(event_time) AS first_event_at,
    max(event_time) AS last_event_at
FROM event_stream;
