-- Q1a: Distribution of Value Tiers
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
    WHEN 'Silver' THEN 3 WHEN 'Bronze' THEN 4 END;

-- Q1b: Promo Dependency by Value Tier
-- Core question: Do high-value customers need discounts?
-- If Diamond tier has low avg promo score, that is proof organic loyalty exists.
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
    WHEN 'Silver' THEN 3 WHEN 'Bronze' THEN 4 END;

-- Q1c: Loyalty Definition A vs B Comparison
-- Which definition captures more of the revenue?
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
ORDER BY total_revenue DESC;

-- Q2a: Category vs Purchase History (Entry vs Retention Categories)
-- Which categories are bought by customers with few previous purchases (entry points)?
-- Which are bought by customers with many previous purchases (retention / loyalty categories)?
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
ORDER BY avg_prev_purchases DESC;

-- Q2b: Season vs Buyer Profile
-- Does the brand attract lower-tenure customers in particular seasons?
-- This matters for seasonal campaigns.
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
ORDER BY avg_prev_purchases DESC;

-- Q2c: Category × Season Matrix (Cross-tab)
-- Where do entry-point categories peak? Useful for targeted seasonal promotion strategy.
SELECT
    category,
    season,
    COUNT(*) AS count,
    ROUND(AVG(previous_purchases), 1) AS avg_prev_purchases,
    ROUND(AVG(promo_dependency_score), 2) AS avg_promo_score
FROM customers
GROUP BY category, season
ORDER BY category, avg_prev_purchases ASC;

-- Q3a: State-Level Revenue and Promo Analysis
-- Identify states with high spend but LOW promo dependency = genuine brand pull.
-- Flag states with fewer than 10 customers as low-confidence and exclude from Q3b.
SELECT
    location AS state,
    COUNT(*) AS customer_count,
    ROUND(SUM(purchase_amount_usd), 2) AS total_revenue,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_spend_per_customer,
    ROUND(AVG(promo_dependency_score), 2) AS avg_promo_score,
    ROUND(AVG(previous_purchases), 1) AS avg_prev_purchases,
    ROUND(SUM(CASE WHEN discount_applied = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS discount_rate_pct,
    ROUND(SUM(CASE WHEN loyalty_a = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS loyal_rate_pct,
    CASE WHEN COUNT(*) < 10 THEN 'Low confidence — exclude from tier analysis' ELSE 'OK' END AS data_quality_flag
FROM customers
GROUP BY location
ORDER BY avg_spend_per_customer DESC, avg_promo_score ASC;

-- Q3b: Geographic Opportunity Tiers
-- Classify each state into a 2x2: High/Low Spend vs High/Low Promo Dependency.
-- Only include states with >= 10 customers to avoid noisy conclusions.
-- NOTE: SQLite has no native MEDIAN() function. The thresholds below use AVG of
-- state-level averages as an approximation (mean of means). This is directionally
-- valid but may differ from a true population median in skewed distributions.
WITH geo_stats AS (
    SELECT
        location,
        AVG(purchase_amount_usd) AS avg_spend,
        AVG(promo_dependency_score) AS avg_promo,
        COUNT(*) AS customers
    FROM customers
    GROUP BY location
    HAVING COUNT(*) >= 10   -- exclude low-confidence states
),
thresholds AS (
    -- Mean of state-level averages used as median approximation (SQLite limitation)
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
            THEN 'Priority Expand — High spend, organic demand'
        WHEN g.avg_spend >= t.threshold_spend AND g.avg_promo > t.threshold_promo 
            THEN 'Promo-Dependent Stronghold — review discount strategy'
        WHEN g.avg_spend < t.threshold_spend AND g.avg_promo <= t.threshold_promo 
            THEN 'Emerging Organic — low volume but loyal'
        ELSE 'Low Priority — low spend, high promo'
    END AS geo_tier
FROM geo_stats g, thresholds t
ORDER BY g.avg_spend DESC;

-- Q4a: Payment Method Distribution by Tier
-- Do Diamond customers prefer specific payment methods?
-- This informs checkout optimization and loyalty program design.
SELECT
    value_tier,
    payment_method,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY value_tier), 1) AS pct_within_tier
FROM customers
GROUP BY value_tier, payment_method
ORDER BY CASE value_tier 
    WHEN 'Diamond' THEN 1 WHEN 'Gold' THEN 2 
    WHEN 'Silver' THEN 3 WHEN 'Bronze' THEN 4 END, count DESC;

-- Q4b: Shipping Type Preference Among Loyal vs Non-Loyal
-- Do loyal customers (Definition A) prefer different shipping types?
-- This informs fulfillment investment priorities.
SELECT
    CASE WHEN loyalty_a = 1 THEN 'Loyal (Definition A)' ELSE 'Non-Loyal' END AS loyalty_status,
    shipping_type,
    COUNT(*) AS count,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_spend,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY loyalty_a), 1) AS pct_within_group
FROM customers
GROUP BY loyalty_a, shipping_type
ORDER BY loyalty_status, count DESC;

-- Q5: Full Profile of Diamond + Loyalty-A Customers
-- The "best" customer: Diamond tier AND behaviourally loyal (no promo needed).
-- This is the foundation for the Ideal Customer Profile in the playbook.
-- If result set is fewer than 20 rows, note this in the playbook as a data sparsity caveat.
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
LIMIT 30;
