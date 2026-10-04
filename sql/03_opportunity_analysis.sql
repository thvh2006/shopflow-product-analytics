CREATE OR REPLACE TABLE mart_category_price_funnel AS
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
    category_level_1,
    price_band,
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
    ) AS cart_to_purchase_rate,
    round(
        sum(representative_price) FILTER (WHERE ordered_full_funnel),
        2
    ) AS observed_purchase_item_value
FROM banded
GROUP BY category_level_1, price_band
ORDER BY category_level_1, price_band;

CREATE OR REPLACE TABLE mart_computer_subcategory_funnel AS
SELECT
    category_code,
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
    ) AS observed_purchase_item_value
FROM mart_session_product
WHERE category_level_1 = 'computers'
GROUP BY category_code
ORDER BY viewed_session_products DESC;

CREATE OR REPLACE TABLE mart_experiment_eligible_users AS
WITH eligible_session_products AS (
    SELECT
        analytics_session_id,
        user_id,
        representative_price,
        ordered_full_funnel,
        first_cart_at
    FROM mart_session_product
    WHERE category_level_1 = 'computers'
        AND representative_price > 176.17
        AND ordered_view_to_cart
),
first_eligible_session AS (
    SELECT
        user_id,
        arg_min(analytics_session_id, first_cart_at) AS eligible_session_id,
        min(first_cart_at) AS first_eligible_at
    FROM eligible_session_products
    GROUP BY user_id
),
eligible_outcome AS (
    SELECT
        first.user_id,
        first.eligible_session_id,
        first.first_eligible_at,
        bool_or(product.ordered_full_funnel) AS converted_same_product,
        sum(product.representative_price) FILTER (
            WHERE product.ordered_full_funnel
        ) AS observed_purchase_item_value
    FROM first_eligible_session first
    JOIN eligible_session_products product
        ON first.user_id = product.user_id
        AND first.eligible_session_id = product.analytics_session_id
    GROUP BY first.user_id, first.eligible_session_id, first.first_eligible_at
),
pre_period AS (
    SELECT
        eligible.user_id,
        count(session.analytics_session_id) FILTER (
            WHERE session.session_started_at < eligible.first_eligible_at
                AND session.analytics_session_id <> eligible.eligible_session_id
        ) AS prior_sessions,
        count(session.analytics_session_id) FILTER (
            WHERE session.session_started_at < eligible.first_eligible_at
                AND session.analytics_session_id <> eligible.eligible_session_id
                AND session.reached_cart
        ) AS prior_cart_sessions,
        count(session.analytics_session_id) FILTER (
            WHERE session.session_started_at < eligible.first_eligible_at
                AND session.analytics_session_id <> eligible.eligible_session_id
                AND session.reached_purchase
        ) AS prior_purchase_sessions,
        coalesce(sum(session.purchase_item_value) FILTER (
            WHERE session.session_started_at < eligible.first_eligible_at
                AND session.analytics_session_id <> eligible.eligible_session_id
        ), 0) AS prior_purchase_item_value
    FROM eligible_outcome eligible
    LEFT JOIN mart_session_funnel session USING (user_id)
    GROUP BY eligible.user_id
)
SELECT
    eligible.*,
    pre.prior_sessions,
    pre.prior_cart_sessions,
    pre.prior_purchase_sessions,
    pre.prior_purchase_item_value,
    coalesce(pre.prior_purchase_sessions / nullif(pre.prior_sessions, 0), 0)
        AS prior_purchase_rate
FROM eligible_outcome eligible
JOIN pre_period pre USING (user_id);
