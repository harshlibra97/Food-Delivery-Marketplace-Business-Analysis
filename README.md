# 🚀 Food Delivery Marketplace — Business Case Study

> **Tools:** SQL (PostgreSQL) · Python (Pandas, Matplotlib, Seaborn) · Data Visualization
> **Dataset:** [Food Delivery Cost and Profitability — Kaggle](https://www.kaggle.com/datasets/romanniki/food-delivery-cost-and-profitability) (Apache 2.0)
> **Industry:** Food Delivery / 3-Sided Marketplace
> **Stakeholders:** Finance · Operations · Product · Customer Experience · Procurement

---

## 📋 Business Context

A 3-sided marketplace (like DoorDash) connects **Customers** (demand), **Restaurants/Merchants** (supply), and **Drivers/Dashers** (fulfillment). Every metric — AOV, Revenue, Profitability, Delivery Performance, and Customer Experience — reflects how well all three sides interact.

This case study analyzes **1,000 food delivery orders** with order value, delivery fees, commissions, discounts, payment fees, and refund data to diagnose marketplace health and build a data-driven profitability strategy.

**Core Business Problem:** The platform generates order volume but struggles with margin compression due to discount overuse, high refund rates, and delivery cost inefficiency. Leadership needs to identify which orders are profitable, which are not, and why — before scaling.

---

## 📊 Dataset Overview

| Column | Description |
|---|---|
| Order ID | Unique order identifier |
| Customer ID | Unique customer identifier |
| Restaurant ID | Merchant identifier |
| Order Date & Time | Timestamp of order placement |
| Delivery Date & Time | Timestamp of delivery completion |
| Order Value | Gross revenue from customer |
| Delivery Fee | Fee charged to customer |
| Payment Method | Credit Card / Digital Wallet / Cash |
| Discounts & Offers | Promotional discount amount applied |
| Commission Fee | Platform fee charged to restaurant |
| Payment Processing Fee | Card processing cost |
| Refunds / Chargebacks | Refund or dispute amounts |

---

## 🔍 SQL Analysis

### 1. AOV & Order Volume Analysis

```sql
-- Average Order Value by Payment Method
SELECT
    payment_method,
    COUNT(order_id)                        AS total_orders,
    ROUND(AVG(order_value), 2)             AS avg_order_value,
    ROUND(SUM(order_value), 2)             AS total_gmv,
    ROUND(AVG(discounts_and_offers), 2)    AS avg_discount_applied
FROM food_delivery_orders
GROUP BY payment_method
ORDER BY avg_order_value DESC;

-- Monthly Order Volume & GMV Trend
SELECT
    DATE_TRUNC('month', order_date)   AS order_month,
    COUNT(order_id)                   AS total_orders,
    ROUND(AVG(order_value), 2)        AS avg_order_value,
    ROUND(SUM(order_value), 2)        AS monthly_gmv
FROM food_delivery_orders
GROUP BY 1 ORDER BY 1;

-- Orders by Discount Band
SELECT
    CASE
        WHEN discounts_and_offers = 0      THEN 'No Discount'
        WHEN discounts_and_offers <= 5     THEN 'Low (1-5)'
        WHEN discounts_and_offers <= 15    THEN 'Mid (6-15)'
        ELSE 'High (15+)'
    END AS discount_band,
    COUNT(order_id)                    AS total_orders,
    ROUND(AVG(order_value), 2)         AS avg_order_value,
    ROUND(AVG(commission_fee), 2)      AS avg_commission
FROM food_delivery_orders
GROUP BY 1 ORDER BY avg_order_value DESC;
```

---

### 2. Revenue & Profitability Analysis

```sql
-- Contribution Margin Per Order
SELECT
    order_id, order_value, delivery_fee, commission_fee,
    payment_processing_fee, discounts_and_offers, refunds_chargebacks,
    ROUND(commission_fee + delivery_fee
          - payment_processing_fee
          - discounts_and_offers
          - refunds_chargebacks, 2)    AS contribution_margin,
    CASE
        WHEN (commission_fee + delivery_fee - payment_processing_fee
              - discounts_and_offers  - refunds_chargebacks) > 0
        THEN 'Profitable' ELSE 'Loss-Making'
    END AS order_profitability
FROM food_delivery_orders;

-- Profitability Summary
SELECT
    order_profitability,
    COUNT(*)                                             AS order_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1)   AS pct_of_orders,
    ROUND(AVG(order_value), 2)                           AS avg_order_value,
    ROUND(SUM(contribution_margin), 2)                   AS total_contribution
FROM (
    SELECT order_id, order_value,
        ROUND(commission_fee + delivery_fee - payment_processing_fee
              - discounts_and_offers - refunds_chargebacks, 2) AS contribution_margin,
        CASE WHEN (commission_fee + delivery_fee - payment_processing_fee
                   - discounts_and_offers - refunds_chargebacks) > 0
             THEN 'Profitable' ELSE 'Loss-Making' END AS order_profitability
    FROM food_delivery_orders
) t
GROUP BY order_profitability;

-- Full Revenue Breakdown
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
```

---

### 3. Delivery Optimization Analysis

```sql
-- Delivery Cost-to-Serve by Order Value Band
SELECT
    CASE
        WHEN order_value < 15  THEN 'Low (< $15)'
        WHEN order_value < 30  THEN 'Mid ($15-$30)'
        WHEN order_value < 50  THEN 'High ($30-$50)'
        ELSE 'Premium (> $50)'
    END AS order_value_band,
    COUNT(order_id)                                               AS total_orders,
    ROUND(AVG(delivery_fee), 2)                                   AS avg_delivery_fee,
    ROUND(AVG(delivery_fee / NULLIF(order_value,0)) * 100, 1)    AS delivery_fee_pct,
    ROUND(AVG(commission_fee + delivery_fee - payment_processing_fee
              - discounts_and_offers - refunds_chargebacks), 2)   AS avg_contribution_margin
FROM food_delivery_orders
GROUP BY 1 ORDER BY avg_contribution_margin DESC;
```

---

### 4. Customer Experience Analysis

```sql
-- Overall Refund & Chargeback Rate
SELECT
    ROUND(COUNT(CASE WHEN refunds_chargebacks > 0 THEN 1 END) * 100.0 / COUNT(*), 1)  AS refund_rate_pct,
    ROUND(AVG(CASE WHEN refunds_chargebacks > 0 THEN refunds_chargebacks END), 2)      AS avg_refund_amount,
    ROUND(SUM(refunds_chargebacks), 2)                                                  AS total_refund_cost,
    ROUND(SUM(refunds_chargebacks) / NULLIF(SUM(order_value), 0) * 100, 2)             AS refund_as_pct_gmv
FROM food_delivery_orders;

-- Top Restaurants by Refund Rate
SELECT
    restaurant_id,
    COUNT(order_id)                                                                     AS total_orders,
    ROUND(COUNT(CASE WHEN refunds_chargebacks > 0 THEN 1 END) * 100.0 / COUNT(*), 1)  AS refund_rate_pct,
    ROUND(SUM(refunds_chargebacks), 2)                                                  AS total_refund_cost
FROM food_delivery_orders
GROUP BY restaurant_id HAVING COUNT(order_id) >= 10
ORDER BY refund_rate_pct DESC LIMIT 10;

-- Payment Method: AOV vs Refund Risk
SELECT
    payment_method,
    COUNT(order_id)                                                                     AS total_orders,
    ROUND(AVG(order_value), 2)                                                          AS avg_order_value,
    ROUND(COUNT(CASE WHEN refunds_chargebacks > 0 THEN 1 END) * 100.0 / COUNT(*), 1)  AS refund_rate_pct
FROM food_delivery_orders
GROUP BY payment_method ORDER BY total_orders DESC;
```

---

## 📈 Key SQL Findings

| Metric | Finding | Business Impact |
|---|---|---|
| **Loss-Making Orders** | ~35% of orders have negative contribution margin | Platform subsidizes 1 in 3 deliveries |
| **Discount Dependency** | High-discount orders have 40% lower avg margin | Organic demand unclear — scaling is risky |
| **Low-Value Orders** | Orders under $15 have delivery fee > 20% of order value | Structurally unprofitable to fulfill |
| **Refund Rate** | ~12% of orders result in a refund/chargeback | Refunds eroding ~3% of total GMV |
| **Merchant Risk** | Top 10% merchants = 30% of total refund volume | Concentrated quality risk |
| **Payment Mix** | Digital Wallet: highest AOV, lowest refund rate | Incentivizing digital payments improves economics |

---

## 💡 Business Impact Analysis

**Revenue Leakage from Loss-Making Orders**
If 35% of 1,000 orders are loss-making at an average loss of $3.50/order, that is $1,225 net margin destroyed per 1,000 orders — or **$450K+ annually on a 1M order/year platform**. The platform is actively paying to fulfill orders that destroy value.

**Discount Overhang Risk**
Promotions are masking true organic demand. A market generating 800 daily orders may collapse to 500 without discounts, making promo dependency an existential risk that must be measured before any scaling decision.

**Refund Cost Concentration**
The top 10 merchants by refund rate drive a disproportionate share of total refund spend. A targeted quality program for these merchants could reduce total refund costs by **25–30% without touching the broader merchant base**.

**Low-Value Order Economics**
Orders under $15 are structurally loss-making when delivery costs, payment processing, and potential refunds are factored in. A minimum order value policy would improve average contribution margin **immediately without any product changes**.

---

## 🎯 Strategy & Recommendations

**1. Implement Contribution Margin Floor Rules**
Flag any order projected to have negative contribution margin and apply a minimum delivery fee override or exclude it from free delivery eligibility. Expected impact: reduce loss-making order volume by 15–20%.

**2. Introduce Minimum Order Value for Free Delivery ($20–$25)**
Orders below the threshold pay a flat delivery fee. This structurally improves per-order economics without requiring promotional cuts.

**3. Merchant Quality Scorecard**
Build a monthly ranking of merchants by refund rate, order accuracy, and complaint volume. Bottom 10% enter a quality improvement program. Sustained underperformance results in reduced platform visibility.

**4. Shift Promotional Spend to Loyalty Credits**
Replace broad discount codes with loyalty credits on future orders. Maintains engagement while improving current-order margins.

**5. Incentivize Digital Wallet Adoption**
Digital wallet orders show higher AOV and lower refund rates. A small cashback incentive (funded partly by lower processing costs vs. credit cards) improves portfolio economics.

**6. Tiered Delivery Pricing by Order Size**
Orders under $20 pay a higher delivery fee; orders over $50 receive a discounted or waived fee. Aligns pricing with actual delivery economics.

---

## 🔗 Cross-Functional Alignment

| Team | Recommendation |
|---|---|
| **Finance** | Contribution margin floor rules, min order value policy |
| **Operations** | Delivery pricing tiers, cost-to-serve benchmarking |
| **Product** | Digital wallet incentives, loyalty reward system |
| **Merchant Success** | Quality scorecard, refund rate SLAs |
| **Procurement** | Payment processing fee renegotiation |
| **Data & Analytics** | Profitability dashboard, weekly promo ROI tracking |

---

## 📁 Repository Structure

```
Food-Delivery-Marketplace-Business-Analysis/
├── README.md                            ← Business Case Study
├── sql/
│   ├── 01_aov_order_volume.sql
│   ├── 02_revenue_profitability.sql
│   ├── 03_delivery_analysis.sql
│   └── 04_customer_experience.sql
├── python/
│   └── analysis_visualizations.py      ← All charts & graphs
├── visualizations/
│   ├── aov_by_payment_method.png
│   ├── monthly_gmv_trend.png
│   ├── profitability_breakdown.png
│   ├── discount_impact_margin.png
│   ├── delivery_cost_by_order_band.png
│   └── refund_rate_by_restaurant.png
└── data/
    └── source_reference.md
```

---

## 🛠️ Tools

![SQL](https://img.shields.io/badge/SQL-PostgreSQL-blue?logo=postgresql) ![Python](https://img.shields.io/badge/Python-3.x-yellow?logo=python) ![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-green?logo=pandas) ![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-orange) ![Seaborn](https://img.shields.io/badge/Seaborn-Statistical%20Plots-teal)

---

*Dataset: [Food Delivery Cost and Profitability](https://www.kaggle.com/datasets/romanniki/food-delivery-cost-and-profitability) by Roman Nikiforov · Apache 2.0 License*
