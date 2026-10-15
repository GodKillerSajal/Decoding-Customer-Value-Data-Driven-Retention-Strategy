"""
Fix: Regenerate all SQL output CSVs as clean data-only files (no embedded SQL text).
Each output file contains ONLY the CSV data for the respective queries.
"""
import sqlite3
import pandas as pd

conn = sqlite3.connect(':memory:')
df = pd.read_csv('project_output/python/customer_features.csv')
df.to_sql('customers', conn, index=False)

# ---- Q1: Loyalty Tiers ----
q1a = pd.read_sql_query("""
-- How is customer value distributed? Is it top-heavy?
SELECT 
    value_tier,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_base,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_spend,
    ROUND(AVG(previous_purchases), 1) AS avg_prev_purchases,
    ROUND(AVG(promo_dependency_score), 2) AS avg_promo_score,
    ROUND(AVG(review_rating), 2) AS avg_rating
FROM customers
GROUP BY value_tier
ORDER BY CASE value_tier 
    WHEN 'Diamond' THEN 1 WHEN 'Gold' THEN 2 
    WHEN 'Silver' THEN 3 WHEN 'Bronze' THEN 4 END
""", conn)

q1b = pd.read_sql_query("""
-- Do high-value customers need discounts? Core loyalty vs promo dependency question.
SELECT
    value_tier,
    SUM(CASE WHEN discount_applied = 'Yes' THEN 1 ELSE 0 END) AS used_discount,
    SUM(CASE WHEN promo_code_used = 'Yes' THEN 1 ELSE 0 END) AS used_promo,
    ROUND(AVG(promo_dependency_score), 2) AS avg_promo_score,
    COUNT(*) AS total,
    ROUND(SUM(CASE WHEN discount_applied = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS discount_rate_pct
FROM customers
GROUP BY value_tier
ORDER BY CASE value_tier 
    WHEN 'Diamond' THEN 1 WHEN 'Gold' THEN 2 
    WHEN 'Silver' THEN 3 WHEN 'Bronze' THEN 4 END
""", conn)

q1c = pd.read_sql_query("""
-- Which loyalty definition captures more revenue?
SELECT
    CASE 
        WHEN loyalty_a = 1 AND loyalty_b = 1 THEN 'Both definitions'
        WHEN loyalty_a = 1 AND loyalty_b = 0 THEN 'Only Definition A'
        WHEN loyalty_a = 0 AND loyalty_b = 1 THEN 'Only Definition B'
        ELSE 'Neither'
    END AS loyalty_segment,
    COUNT(*) AS customer_count,
    ROUND(SUM(purchase_amount_usd), 2) AS total_revenue,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_spend,
    ROUND(AVG(previous_purchases), 1) AS avg_prev_purchases,
    ROUND(AVG(promo_dependency_score), 2) AS avg_promo_score
FROM customers
GROUP BY loyalty_segment
ORDER BY total_revenue DESC
""", conn)

with open('project_output/sql/q1_loyalty_tiers.csv', 'w', newline='', encoding='utf-8') as f:
    f.write('-- Q1a: Value Tier Distribution\n')
    q1a.to_csv(f, index=False)
    f.write('\n-- Q1b: Promo Dependency by Value Tier\n')
    q1b.to_csv(f, index=False)
    f.write('\n-- Q1c: Loyalty Definition A vs B Overlap\n')
    q1c.to_csv(f, index=False)

# ---- Q2: Category & Season ----
q2a = pd.read_sql_query("""
SELECT
    category,
    ROUND(AVG(previous_purchases), 2) AS avg_prev_purchases,
    COUNT(*) AS transaction_count,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_spend,
    ROUND(AVG(review_rating), 2) AS avg_rating,
    ROUND(AVG(promo_dependency_score), 2) AS avg_promo_score,
    SUM(CASE WHEN loyalty_a = 1 THEN 1 ELSE 0 END) AS loyal_a_customers,
    ROUND(SUM(CASE WHEN loyalty_a = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS loyal_rate_pct
FROM customers
GROUP BY category
ORDER BY avg_prev_purchases DESC
""", conn)

q2b = pd.read_sql_query("""
SELECT
    season,
    ROUND(AVG(previous_purchases), 2) AS avg_prev_purchases,
    COUNT(*) AS transaction_count,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_spend,
    ROUND(AVG(promo_dependency_score), 2) AS avg_promo_score,
    SUM(CASE WHEN discount_applied = 'Yes' THEN 1 ELSE 0 END) AS discount_count,
    ROUND(SUM(CASE WHEN discount_applied = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS discount_rate_pct
FROM customers
GROUP BY season
ORDER BY avg_prev_purchases DESC
""", conn)

q2c = pd.read_sql_query("""
SELECT
    category,
    season,
    COUNT(*) AS count,
    ROUND(AVG(previous_purchases), 1) AS avg_prev_purchases,
    ROUND(AVG(promo_dependency_score), 2) AS avg_promo_score
FROM customers
GROUP BY category, season
ORDER BY category, avg_prev_purchases ASC
""", conn)

with open('project_output/sql/q2_category_season.csv', 'w', newline='', encoding='utf-8') as f:
    f.write('-- Q2a: Category vs Purchase History (Entry vs Retention Categories)\n')
    q2a.to_csv(f, index=False)
    f.write('\n-- Q2b: Season vs Buyer Profile\n')
    q2b.to_csv(f, index=False)
    f.write('\n-- Q2c: Category x Season Cross-tab\n')
    q2c.to_csv(f, index=False)

# ---- Q3: Geography ----
q3a = pd.read_sql_query("""
SELECT
    location AS state,
    COUNT(*) AS customer_count,
    ROUND(SUM(purchase_amount_usd), 2) AS total_revenue,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_spend_per_customer,
    ROUND(AVG(promo_dependency_score), 2) AS avg_promo_score,
    ROUND(AVG(previous_purchases), 1) AS avg_prev_purchases,
    ROUND(SUM(CASE WHEN discount_applied = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS discount_rate_pct,
    ROUND(SUM(CASE WHEN loyalty_a = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS loyal_rate_pct,
    CASE WHEN COUNT(*) < 10 THEN 'Low confidence' ELSE 'OK' END AS data_quality_flag
FROM customers
GROUP BY location
ORDER BY avg_spend_per_customer DESC, avg_promo_score ASC
""", conn)

q3b = pd.read_sql_query("""
WITH geo_stats AS (
    SELECT
        location,
        AVG(purchase_amount_usd) AS avg_spend,
        AVG(promo_dependency_score) AS avg_promo,
        COUNT(*) AS customers
    FROM customers
    GROUP BY location
    HAVING COUNT(*) >= 10
),
thresholds AS (
    SELECT
        AVG(avg_spend) AS threshold_spend,
        AVG(avg_promo) AS threshold_promo
    FROM geo_stats
)
SELECT
    g.location,
    ROUND(g.avg_spend, 2) AS avg_spend,
    ROUND(g.avg_promo, 2) AS avg_promo_score,
    g.customers,
    CASE
        WHEN g.avg_spend >= t.threshold_spend AND g.avg_promo <= t.threshold_promo 
            THEN 'Priority Expand'
        WHEN g.avg_spend >= t.threshold_spend AND g.avg_promo > t.threshold_promo 
            THEN 'Promo-Dependent Stronghold'
        WHEN g.avg_spend < t.threshold_spend AND g.avg_promo <= t.threshold_promo 
            THEN 'Emerging Organic'
        ELSE 'Low Priority'
    END AS geo_tier
FROM geo_stats g, thresholds t
ORDER BY g.avg_spend DESC
""", conn)

with open('project_output/sql/q3_geography.csv', 'w', newline='', encoding='utf-8') as f:
    f.write('-- Q3a: State-Level Revenue and Promo Analysis\n')
    q3a.to_csv(f, index=False)
    f.write('\n-- Q3b: Geographic Opportunity Tiers (2x2: Spend x Promo Dependency)\n')
    q3b.to_csv(f, index=False)

# ---- Q4: Payment & Shipping ----
q4a = pd.read_sql_query("""
SELECT
    value_tier,
    payment_method,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY value_tier), 1) AS pct_within_tier
FROM customers
GROUP BY value_tier, payment_method
ORDER BY CASE value_tier 
    WHEN 'Diamond' THEN 1 WHEN 'Gold' THEN 2 
    WHEN 'Silver' THEN 3 WHEN 'Bronze' THEN 4 END, count DESC
""", conn)

q4b = pd.read_sql_query("""
SELECT
    CASE WHEN loyalty_a = 1 THEN 'Loyal (Definition A)' ELSE 'Non-Loyal' END AS loyalty_status,
    shipping_type,
    COUNT(*) AS count,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_spend,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY loyalty_a), 1) AS pct_within_group
FROM customers
GROUP BY loyalty_a, shipping_type
ORDER BY loyalty_status, count DESC
""", conn)

with open('project_output/sql/q4_payment_shipping.csv', 'w', newline='', encoding='utf-8') as f:
    f.write('-- Q4a: Payment Method Distribution by Tier\n')
    q4a.to_csv(f, index=False)
    f.write('\n-- Q4b: Shipping Type Preference - Loyal vs Non-Loyal\n')
    q4b.to_csv(f, index=False)

# ---- Q5: Ideal Customer ----
q5 = pd.read_sql_query("""
SELECT
    age_bracket,
    gender,
    category,
    season,
    payment_method,
    shipping_type,
    frequency_of_purchases,
    COUNT(*) AS count,
    ROUND(AVG(age), 1) AS avg_age,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_spend,
    ROUND(AVG(previous_purchases), 1) AS avg_prev_purchases,
    ROUND(AVG(review_rating), 2) AS avg_rating
FROM customers
WHERE value_tier = 'Diamond' AND loyalty_a = 1
GROUP BY age_bracket, gender, category, season, payment_method, shipping_type, frequency_of_purchases
ORDER BY count DESC
LIMIT 30
""", conn)

with open('project_output/sql/q5_ideal_customer.csv', 'w', newline='', encoding='utf-8') as f:
    f.write('-- Q5: Ideal Customer Profile (Diamond Tier + Behavioural Loyalty A)\n')
    q5.to_csv(f, index=False)

conn.close()
print("All 5 SQL output CSVs regenerated cleanly.")
print(f"Q1 rows: q1a={len(q1a)}, q1b={len(q1b)}, q1c={len(q1c)}")
print(f"Q2 rows: q2a={len(q2a)}, q2b={len(q2b)}, q2c={len(q2c)}")
print(f"Q3 rows: q3a={len(q3a)}, q3b={len(q3b)}")
print(f"Q4 rows: q4a={len(q4a)}, q4b={len(q4b)}")
print(f"Q5 rows: {len(q5)}")
