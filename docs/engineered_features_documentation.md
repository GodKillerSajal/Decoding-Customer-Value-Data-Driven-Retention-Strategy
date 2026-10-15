# Engineered Features — Documentation

> **Scope:** The source is a one-row-per-shopper snapshot without event dates, randomized offer assignment, or margin. Names such as "loyalty" and "value" refer to descriptive proxies, not validated retention, lifetime-value, or causal measures.

**Project:** Decoding Customer Value: A SQL-Driven Retention Strategy  
**Script:** `feature_engineering.py`  
**Input:** `Dataset.csv` (3,900 rows, 18 raw columns)  
**Output:** `customer_features.csv` (3,900 rows, 34 columns)

> This document describes every new column added during feature engineering — what it measures, how it is constructed, and why it matters to the business question at hand.

---

## Data Cleaning Features (Pre-Engineering)

These flags are created during the cleaning phase to preserve information about data quality issues.

---

### `rating_was_null`
| Property | Detail |
|---|---|
| **Type** | Binary integer (0 / 1) |
| **Source column** | `Review Rating` |
| **Logic** | `1` if the original `Review Rating` was null, `0` otherwise |
| **Why it was created** | The dataset had missing values in `Review Rating`. Rather than silently imputing and losing the information that a rating was absent, we flag those rows. This allows downstream analysis to optionally filter or weight records differently based on whether the rating was real or imputed. |
| **Business meaning** | A customer with a null rating may represent a disengaged buyer who did not bother to leave feedback — a subtle churn signal. |

---

## Core Engineered Features

---

### `freq_promo_flag`
| Property | Detail |
|---|---|
| **Type** | Binary integer (0 / 1) |
| **Source column** | `frequency_of_purchases` |
| **Logic** | `1` if frequency is `Quarterly`, `Every 3 Months`, or `Annually`; `0` for higher-frequency buyers (Weekly, Bi-Weekly, Fortnightly, Monthly) |
| **Why it was created** | Customers who buy only once a quarter or once a year are unlikely to be organically loyal. Their infrequent visits suggest they return primarily when offered a deal. This flag is one of three inputs to the `promo_dependency_score`. |
| **Business meaning** | A high `freq_promo_flag` rate in a segment signals that the segment's purchase cadence is driven by promotional triggers, not genuine brand affinity. |

---

### `promo_dependency_score` ⭐ *PS Required Feature*
| Property | Detail |
|---|---|
| **Type** | Integer (0–3) |
| **Source columns** | `discount_applied`, `promo_code_used`, `frequency_of_purchases` |
| **Logic** | Sum of three binary signals: `(discount_applied == 'Yes') + (promo_code_used == 'Yes') + freq_promo_flag` |
| **Scale** | `0` = fully organic (no discount, no promo code, high-frequency buyer) → `3` = fully promo-dependent |
| **Why it was created** | The Problem Statement asks whether the brand is "building a loyal customer base or reliant on continuous promotional activity." A single column (`Discount Applied`) would only capture one dimension of promo reliance. By combining discount usage, promo code redemption, and purchase frequency pattern, we get a richer, multi-signal view of how much a customer depends on promotions to buy. |
| **Business meaning** | A score of `0` means no discount/promo was recorded and the frequency flag was not triggered in this row; a score of `3` means all three proxy signals are present. The score can guide a test hypothesis, but it does not show whether a customer would buy without an offer. |

---

### `frequency_score`
| Property | Detail |
|---|---|
| **Type** | Float (1–6) |
| **Source column** | `frequency_of_purchases` |
| **Logic** | Ordinal mapping: Weekly=6, Bi-Weekly=5, Fortnightly=4, Monthly=3, Every 3 Months=2, Quarterly=1.5, Annually=1 |
| **Why it was created** | `frequency_of_purchases` is a categorical variable. To use it in numeric computations (composite score, normalization), it must be mapped to an ordered numeric scale that preserves the relative purchasing intensity of each group. |
| **Business meaning** | Higher scores indicate customers who engage with the brand more regularly. Combined with spend and purchase depth, it is a strong proxy for lifetime engagement. |

---

### `norm_purchase_amount`, `norm_previous_purchases`, `norm_review_rating`, `norm_frequency_score`
| Property | Detail |
|---|---|
| **Type** | Float (0.0–1.0) |
| **Source columns** | `purchase_amount_usd`, `previous_purchases`, `review_rating`, `frequency_score` |
| **Logic** | MinMax normalization via `sklearn.preprocessing.MinMaxScaler`: `(x - min) / (max - min)` |
| **Why they were created** | The four input variables to `composite_score` are on completely different scales (e.g., purchase amount in tens of dollars vs. review rating on a 1–5 scale). Normalizing each to [0, 1] ensures that no single variable dominates the composite simply due to its scale magnitude. |
| **Business meaning** | These are intermediate calculation columns. They are not directly interpretable on their own, but ensure the composite score is a fair, balanced measure. |

---

### `composite_score` ⭐ *Central value metric*
| Property | Detail |
|---|---|
| **Type** | Float (0.0–1.0) |
| **Source columns** | `norm_purchase_amount`, `norm_previous_purchases`, `norm_review_rating`, `norm_frequency_score` |
| **Logic** | Weighted sum: `(purchase_amount × 0.35) + (previous_purchases × 0.40) + (review_rating × 0.15) + (frequency_score × 0.10)` |
| **Weight rationale** | Previous-purchase count (0.40) is the heaviest weight as a proxy for purchase history. Purchase amount (0.35) is the amount recorded on this row, not observed customer lifetime revenue. Rating (0.15) reflects the recorded review; frequency (0.10) is the stated cadence. |
| **Why it was created** | The Problem Statement requires identifying "what the most valuable customers look like" using available data without any loyalty score, churn label, or timestamp. `composite_score` is our primary constructed measure of customer value — it aggregates four behavioural and transactional signals into a single comparable number. |
| **Business meaning** | A high composite score indicates a row with relatively higher recorded purchase amount, previous-purchase count, rating, and stated frequency under the chosen weights. It is a relative descriptive index, not a churn or profit estimate. |

---

### `value_tier` ⭐ *PS Required Feature*
| Property | Detail |
|---|---|
| **Type** | Categorical string |
| **Values** | `Diamond` / `Gold` / `Silver` / `Bronze` |
| **Source column** | `composite_score` |
| **Logic** | Percentile-based segmentation: Diamond ≥ p85 (top 15%), Gold = p50–p85, Silver = p25–p50, Bronze < p25 (bottom 25%) |
| **Why asymmetric thresholds?** | The Diamond tier uses p85 (not p75) deliberately. The "customer pyramid" concept requires a small, elite apex — representing the brand's most critical and irreplaceable customers. Using p75 would produce a too-large "top tier" that dilutes the strategic exclusivity of this group. |
| **Why it was created** | The Problem Statement requires a "customer pyramid showing how value is distributed." `value_tier` is the direct label powering the Customer Pyramid dashboard page and the Promo Sunset Playbook's segment-level action table. |
| **Business meaning** | Diamond and Bronze are the upper and lower sample percentiles of the constructed index. They are not verified customer profitability or lifecycle groups; any promotion changes should be evaluated in a randomized test. |
| **Actual distribution** | Diamond: 585 (15.0%) · Gold: 1,365 (35.0%) · Silver: 975 (25.0%) · Bronze: 975 (25.0%) |

---

### `satisfaction_flag` ⭐ *PS Required Feature*
| Property | Detail |
|---|---|
| **Type** | Binary integer (0 / 1) |
| **Source column** | `review_rating` |
| **Logic** | `1` if `review_rating >= 4.0`, else `0` |
| **Threshold rationale** | A rating of 4.0+ on a 1–5 scale is the standard "satisfied" threshold in retail NPS research. Ratings of 3 and below indicate neutral-to-dissatisfied experiences that warrant intervention. |
| **Why it was created** | The raw `review_rating` is a continuous float. For segmentation, filtering, and dashboard KPIs, a binary "was this customer satisfied?" flag is more actionable than a decimal score. It also enables simple SQL filtering without requiring aggregation. |
| **Business meaning** | The flag summarizes recorded ratings at a chosen threshold. It does not establish satisfaction beyond the supplied survey response or justify intentionally allowing a segment to churn. |
| **Actual value** | 1,634 customers (41.9%) have `satisfaction_flag = 1` |

---

### `loyalty_a` — Definition A: Strict Organic Loyalty
| Property | Detail |
|---|---|
| **Type** | Binary integer (0 / 1) |
| **Source columns** | `previous_purchases`, `frequency_of_purchases`, `promo_code_used`, `discount_applied` |
| **Logic** | `1` if ALL four conditions are met: (1) `previous_purchases ≥ median` AND (2) frequency in `{Weekly, Bi-Weekly, Fortnightly}` AND (3) `promo_code_used == 'No'` AND (4) `discount_applied == 'No'` |
| **Why it was created** | The Problem Statement mandates: *"build at least two competing definitions of loyalty using different variable combinations."* Loyalty A is the strictest definition — it requires purchase depth, high engagement frequency, AND zero promotional dependency. No single condition is sufficient; all four must hold simultaneously. |
| **Business meaning** | Loyalty A is the strictest proxy in this snapshot: a high previous-purchase count, high stated cadence, and no recorded discount or promo use on the row. It does not verify a customer's full purchase history or prove that future purchases would occur without offers. |
| **Actual value** | 461 customers (11.8% of base) |
| **Trade-off vs. Definition B** | Definition A is very strict — only 11.8% qualify. This limits its use for large-scale targeting but makes it a clean signal for the Ideal Customer Profile. |

---

### `loyalty_b` — Definition B: Value-Based Loyalty
| Property | Detail |
|---|---|
| **Type** | Binary integer (0 / 1) |
| **Source columns** | `composite_score`, `previous_purchases` |
| **Logic** | `1` if BOTH conditions hold: (1) `composite_score ≥ 60th percentile` AND (2) `previous_purchases ≥ median` |
| **Why it was created** | The second required loyalty definition. Definition B is more inclusive — it captures customers who are high-value by the composite measure and have demonstrated purchase depth, but does not penalize occasional promo usage. This reflects the real-world reality that even genuinely loyal customers sometimes use discount codes. |
| **Business meaning** | Loyalty B (33.5% of the sample) is a broader proxy based on the composite score and previous-purchase count. A promotion change would need to be tested before claiming that it converts customers into Loyalty A. |
| **Actual value** | 1,307 customers (33.5% of base) |
| **Key difference from A** | Definition B captures 33.5% vs 11.8% for A. Revenue share: B contributes ~40% of total revenue vs A's ~12%. B is better for broad segmentation; A is better for strict profiling. |

---

### `frequency_numeric`
| Property | Detail |
|---|---|
| **Type** | Float (1–6) |
| **Source column** | `frequency_score` |
| **Logic** | Direct alias of `frequency_score` |
| **Why it was created** | Retained as a named alias for clarity in SQL queries and dashboard bindings where the intent (a numeric frequency value) is clearer than the intermediate processing name `frequency_score`. |

---

### `is_subscriber`
| Property | Detail |
|---|---|
| **Type** | Binary integer (0 / 1) |
| **Source column** | `subscription_status` |
| **Logic** | `1` if `subscription_status == 'Yes'`, else `0` |
| **Why it was created** | `subscription_status` is a text field (`Yes`/`No`). Converting it to a binary integer enables direct arithmetic operations: counting subscribers, computing subscription rates, and using it as a filter in composite analyses without string comparison overhead. |
| **Business meaning** | Subscription is a strong indicator of brand commitment. Subscribers who still require heavy discounts (high `promo_dependency_score`) represent a particularly interesting segment — they have committed to the brand structurally but are still incentive-driven in their actual purchase behaviour. |

---

### `age_bracket`
| Property | Detail |
|---|---|
| **Type** | Categorical string |
| **Values** | `Young Adult` / `Core Millennial` / `Older Millennial` / `Gen X` / `Senior` |
| **Source column** | `age` |
| **Logic** | Rule-based bucketing: ≤25 → Young Adult · 26–35 → Core Millennial · 36–45 → Older Millennial · 46–59 → Gen X · 60+ → Senior |
| **Why it was created** | Raw `age` (integer) is too granular for segment-level analysis and dashboarding. Generational brackets are the industry-standard demographic segmentation unit in retail and D2C marketing, making them immediately interpretable to a non-technical founding team. |
| **Business meaning** | Age brackets reveal which life-stage cohorts drive organic loyalty vs. promo dependency. The Ideal Customer Profile identifies Core Millennials (26–35) as the brand's highest-value organic segment — a finding that directly informs lookalike audience creation on Meta/TikTok. |

---

## Feature Summary Table

| Feature | Type | PS Required | Role in Analysis |
|---|---|---|---|
| `rating_was_null` | Binary | No | Data quality flag |
| `freq_promo_flag` | Binary | No | Input to promo score |
| `promo_dependency_score` | Integer 0–3 | **Yes** | Core promo analysis metric |
| `frequency_score` | Float | No | Input to composite score |
| `norm_purchase_amount` | Float 0–1 | No | Normalization intermediate |
| `norm_previous_purchases` | Float 0–1 | No | Normalization intermediate |
| `norm_review_rating` | Float 0–1 | No | Normalization intermediate |
| `norm_frequency_score` | Float 0–1 | No | Normalization intermediate |
| `composite_score` | Float 0–1 | No | Customer value index |
| `value_tier` | Categorical | **Yes** | Customer pyramid segmentation |
| `satisfaction_flag` | Binary | **Yes** | Satisfaction segmentation |
| `loyalty_a` | Binary | No | Strict organic loyalty definition |
| `loyalty_b` | Binary | No | Broad value-based loyalty definition |
| `frequency_numeric` | Float | No | Alias for frequency_score |
| `is_subscriber` | Binary | No | Subscription status as numeric |
| `age_bracket` | Categorical | No | Generational demographic segment |

> **Note:** "PS Required" marks the three features explicitly called out in the Problem Statement deliverables table: *dependency score, value tier, satisfaction flag.*
