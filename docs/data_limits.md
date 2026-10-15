# Data Limits and Claim Guide

## What the file contains

`Dataset.csv` has 3,900 unique shopper rows and one observed purchase record per shopper, along with demographic fields, purchase cadence, a previous-purchase count, discount/promo indicators, and review rating. It does not contain a transaction date, customer-level purchase sequence, campaign assignment, discount depth, cost of goods, or margin.

## Safe interpretations

- Describe the calculated tiers as **customer-value proxies**, not observed lifetime value.
- Describe `loyalty_a` and `loyalty_b` as **behavioral/value-based proxy definitions**, not verified retained-customer classes.
- Report discount-use and purchase-history comparisons as descriptive patterns in this sample.
- Present promo sunset, milestone rewards, and geographic targeting as hypotheses for testing.
- The sample's recorded purchase amounts sum to $233,081; do not treat this as historical revenue across a known period.

## Claims that require new data

The supplied file cannot establish churn or retention rates, whether promotions caused repeat buying, the causal impact of removing discounts, actual profit/margin, or savings from a proposed policy. A follow-up customer panel with dated orders, offer assignment, offer costs, and contribution margin would be needed to estimate those outcomes.

The source retention playbook contains illustrative dollar and revenue scenarios. They should not be represented as measured savings or experimental results.
