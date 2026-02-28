-- ============================================================
-- FOOD DELIVERY MARKETPLACE — SQL ANALYSIS
-- Dataset: Food Delivery Cost and Profitability (Kaggle)
-- Author: Harshkumar Nilesh Patel
-- ============================================================

-- ============================================================
-- SECTION 1: AOV & ORDER VOLUME ANALYSIS
-- ============================================================

-- 1A. Average Order Value by Payment Method
SELECT
    payment_method,
    COUNT(order_id)                        AS total_orders,
    ROUND(AVG(order_value), 2)             AS avg_order_value,
    ROUND(SUM(order_value), 2)             AS total_gmv,
    ROUND(AVG(discounts_and_offers), 2)    AS avg_discount_applied
FROM food_delivery_orders
GROUP BY payment_method
ORDER BY avg_order_value DESC;

-- 1B. Monthly Order Volume & GMV Trend
SELECT
    DATE_TRUNC('month', order_date)   AS order_month,
    COUNT(order_id)                   AS total_orders,
    ROUND(AVG(order_value), 2)        AS avg_order_value,
    ROUND(SUM(order_value), 2)        AS monthly_gmv
FROM food_delivery_orders
GROUP BY 1 ORDER BY 1;

-- 1C. Orders by Discount Band (Promo vs Non-Promo)
SELECT
    CASE
        WHEN discounts_and_offers = 0      THEN 'No Discount'
        WHEN discounts_and_offers <= 5     THEN 'Low Discount (1-5)'
        WHEN discounts_and_offers <= 15    THEN 'Mid Discount (6-15)'
        ELSE 'High Discount (15+)'
    END AS discount_band,
    COUNT(order_id)                    AS total_orders,
    ROUND(AVG(order_value), 2)         AS avg_order_value,
    ROUND(AVG(commission_fee), 2)      AS avg_commission,
    ROUND(AVG(discounts_and_offers), 2) AS avg_discount
FROM food_delivery_orders
GROUP BY 1 ORDER BY avg_order_value DESC;


-- ============================================================
-- SECTION 2: REVENUE & PROFITABILITY ANALYSIS
-- ============================================================

-- 2A. Contribution Margin Per Order
SELECT
    order_id,
    order_value,
    delivery_fee,
    commission_fee,
    payment_processing_fee,
    discounts_and_offers,
    refunds_chargebacks,
    ROUND(
        commission_fee + delivery_fee
        - payment_processing_fee
        - discounts_and_offers
        - refunds_chargebacks, 2
    ) AS contribution_margin,
    CASE
        WHEN (commission_fee + delivery_fee - payment_processing_fee
              - discounts_and_offers  - refunds_chargebacks) > 0
        THEN 'Profitable' ELSE 'Loss-Making'
    END AS order_profitability
FROM food_delivery_orders;

-- 2B. Profitability Summary
SELECT
    order_profitability,
    COUNT(*)                                                     AS order_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1)           AS pct_of_orders,
    ROUND(AVG(order_value), 2)                                   AS avg_order_value,
    ROUND(SUM(contribution_margin), 2)                           AS total_contribution
FROM (
    SELECT order_id, order_value,
        ROUND(commission_fee + delivery_fee - payment_processing_fee
              - discounts_and_offers - refunds_chargebacks, 2) AS contribution_margin,
        CASE
            WHEN (commission_fee + delivery_fee - payment_processing_fee
                   - discounts_and_offers - refunds_chargebacks) > 0
             THEN 'Profitable' ELSE 'Loss-Making'
        END AS order_profitability
    FROM food_delivery_orders
) t
GROUP BY order_profitability;

-- 2C. Full Revenue & Cost Breakdown
SELECT
    ROUND(SUM(commission_fee), 2)            AS total_commission_revenue,
    ROUND(SUM(delivery_fee), 2)              AS total_delivery_fee_revenue,
    ROUND(SUM(payment_processing_fee), 2)    AS total_processing_costs,
    ROUND(SUM(discounts_and_offers), 2)      AS total_discount_cost,
    ROUND(SUM(refunds_chargebacks), 2)       AS total_refund_cost,
    ROUND(SUM(commission_fee + delivery_fee
              - payment_processing_fee
              - discounts_and_offers
              - refunds_chargebacks), 2)     AS net_platform_revenue
FROM food_delivery_orders;

-- 2D. Avg Contribution Margin by Discount Level
SELECT
    CASE
        WHEN discounts_and_offers = 0      THEN 'No Discount'
        WHEN discounts_and_offers <= 5     THEN 'Low Discount'
        WHEN discounts_and_offers <= 15    THEN 'Mid Discount'
        ELSE 'High Discount'
    END AS discount_band,
    COUNT(order_id)                    AS total_orders,
    ROUND(AVG(commission_fee + delivery_fee - payment_processing_fee
              - discounts_and_offers - refunds_chargebacks), 2) AS avg_contribution_margin,
    ROUND(AVG(order_value), 2)         AS avg_order_value
FROM food_delivery_orders
GROUP BY 1 ORDER BY avg_contribution_margin DESC;


-- ============================================================
-- SECTION 3: DELIVERY OPTIMIZATION ANALYSIS
-- ============================================================

-- 3A. Delivery Cost-to-Serve by Order Value Band
SELECT
    CASE
        WHEN order_value < 15  THEN 'Low (< $15)'
        WHEN order_value < 30  THEN 'Mid ($15-30)'
        WHEN order_value < 50  THEN 'High ($30-50)'
        ELSE 'Premium (> $50)'
    END AS order_value_band,
    COUNT(order_id)                                               AS total_orders,
    ROUND(AVG(delivery_fee), 2)                                   AS avg_delivery_fee,
    ROUND(AVG(delivery_fee / NULLIF(order_value,0)) * 100, 1)    AS delivery_fee_pct_of_order,
    ROUND(AVG(commission_fee + delivery_fee - payment_processing_fee
              - discounts_and_offers - refunds_chargebacks), 2)   AS avg_contribution_margin
FROM food_delivery_orders
GROUP BY 1 ORDER BY avg_contribution_margin DESC;

-- 3B. Orders Below Break-Even Threshold
SELECT
    COUNT(*) AS total_loss_making_orders,
    ROUND(AVG(order_value), 2) AS avg_order_value_loss,
    ROUND(AVG(delivery_fee), 2) AS avg_delivery_fee_loss,
    ROUND(SUM(commission_fee + delivery_fee - payment_processing_fee
              - discounts_and_offers - refunds_chargebacks), 2) AS total_margin_loss
FROM food_delivery_orders
WHERE (commission_fee + delivery_fee - payment_processing_fee
       - discounts_and_offers - refunds_chargebacks) < 0;


-- ============================================================
-- SECTION 4: CUSTOMER EXPERIENCE ANALYSIS
-- ============================================================

-- 4A. Overall Refund & Chargeback Rate
SELECT
    ROUND(COUNT(CASE WHEN refunds_chargebacks > 0 THEN 1 END) * 100.0 / COUNT(*), 1)  AS refund_rate_pct,
    ROUND(AVG(CASE WHEN refunds_chargebacks > 0 THEN refunds_chargebacks END), 2)      AS avg_refund_amount,
    ROUND(SUM(refunds_chargebacks), 2)                                                  AS total_refund_cost,
    ROUND(SUM(refunds_chargebacks) / NULLIF(SUM(order_value), 0) * 100, 2)             AS refund_as_pct_gmv
FROM food_delivery_orders;

-- 4B. Top 10 Restaurants by Refund Rate (Merchant Quality Risk)
SELECT
    restaurant_id,
    COUNT(order_id)                                                                     AS total_orders,
    COUNT(CASE WHEN refunds_chargebacks > 0 THEN 1 END)                                AS refund_orders,
    ROUND(COUNT(CASE WHEN refunds_chargebacks > 0 THEN 1 END) * 100.0 / COUNT(*), 1)  AS refund_rate_pct,
    ROUND(SUM(refunds_chargebacks), 2)                                                  AS total_refund_cost,
    ROUND(AVG(order_value), 2)                                                          AS avg_order_value
FROM food_delivery_orders
GROUP BY restaurant_id
HAVING COUNT(order_id) >= 10
ORDER BY refund_rate_pct DESC
LIMIT 10;

-- 4C. Payment Method: AOV, Volume and Refund Risk
SELECT
    payment_method,
    COUNT(order_id)                                                                     AS total_orders,
    ROUND(AVG(order_value), 2)                                                          AS avg_order_value,
    ROUND(AVG(delivery_fee), 2)                                                         AS avg_delivery_fee,
    ROUND(COUNT(CASE WHEN refunds_chargebacks > 0 THEN 1 END) * 100.0 / COUNT(*), 1)  AS refund_rate_pct,
    ROUND(SUM(refunds_chargebacks), 2)                                                  AS total_refunds,
    ROUND(AVG(commission_fee + delivery_fee - payment_processing_fee
              - discounts_and_offers - refunds_chargebacks), 2)                         AS avg_contribution_margin
FROM food_delivery_orders
GROUP BY payment_method
ORDER BY total_orders DESC;

-- 4D. Customer Order Frequency & Repeat Behavior
SELECT
    customer_id,
    COUNT(order_id)                    AS total_orders,
    ROUND(AVG(order_value), 2)         AS avg_order_value,
    MIN(order_date)                    AS first_order_date,
    MAX(order_date)                    AS last_order_date,
    ROUND(SUM(order_value), 2)         AS lifetime_order_value,
    COUNT(CASE WHEN refunds_chargebacks > 0 THEN 1 END) AS refund_count
FROM food_delivery_orders
GROUP BY customer_id
ORDER BY total_orders DESC;
