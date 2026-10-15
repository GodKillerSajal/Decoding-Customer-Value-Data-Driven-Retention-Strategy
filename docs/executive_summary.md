# Executive Summary

## Finding

The supplied customer sample shows similar discount incidence among the highest and lowest constructed value tiers: **42.9% for Diamond** and **41.6% for Bronze**. This suggests the retailer may want to test whether its current promotion policy is differentiated enough by customer behavior.

The value tiers combine recorded purchase amount, previous-purchase count, review rating, and stated purchase cadence. A separate strict loyalty proxy identifies shoppers with higher purchase history and cadence who report no discount or promo use. These measures help structure the sample, but they do not observe repeat purchases over time.

## Recommended next step

Run a member-level randomized test before changing promotion access:

1. Randomize eligible high-value, low-promo shoppers between the existing offer policy and reduced promotional exposure.
2. Pre-register a follow-up window and primary outcome such as repeat purchase within 90 days.
3. Track contribution margin, order value, conversion, and opt-outs as guardrails.
4. Expand suppression only if the treatment-control results support it.

For other segments, test milestone rewards or category-specific offers against business-as-usual rather than assuming they improve retention.

## Data boundary

The 3,900-row source has one record per shopper, no transaction timestamps, and no campaign assignment, margin, or follow-up outcome. The reported $233,081 is the sum of recorded sample purchase amounts, not a time-series revenue total. Consequently, this analysis cannot establish churn, causal lift, or recovered margin. The earlier playbook's savings scenarios are hypothetical and require external assumptions.
