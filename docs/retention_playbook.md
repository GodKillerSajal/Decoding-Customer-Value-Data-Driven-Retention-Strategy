# Retention Test Plan

The analysis suggests possible segments for a promotion experiment. The source is a one-row-per-shopper snapshot, so none of the proposed policies below has been deployed or shown to improve retention or margin. Keep the current policy as the control until a properly measured experiment supports a change.

## Proposed randomized test

| Hypothesis cohort | Test arm | Control arm | Primary outcome | Guardrails |
|---|---|---|---|---|
| Diamond tier with promo-dependency score 0 | Reduce promotional exposure for 90 days | Existing communication and offer policy | Repeat purchase within 90 days | Contribution margin, order value, opt-outs |
| Gold tier with low promo-dependency score | Reduce message frequency by a pre-set amount | Existing communication cadence | Repeat purchase within 90 days | Conversion, contribution margin, unsubscribes |
| Gold/Silver tier with higher promo-dependency score | Replace a percentage-off offer with a milestone reward | Existing offer policy | Repeat purchase and order value within 90 days | Reward cost, contribution margin, opt-outs |
| Geographic groups with different observed spend/promo scores | Test localized messaging | Existing geographic campaign | Repeat purchase and contribution margin | Sample size by state, acquisition cost |

## Experiment rules

1. Define eligibility and exclusions before randomization. Assign each shopper to one arm and keep assignment stable across channels.
2. Randomize at the shopper level, preferably stratifying by the constructed value tier and prior-purchase count.
3. Use an intent-to-treat comparison. Do not remove customers because they did not open a message or redeem an offer.
4. Pre-register the 90-day outcome, guardrails, minimum detectable effect, and stopping date.
5. Roll out only if the treatment improves the primary outcome without breaching margin or customer-experience guardrails.

## Descriptive profile (hypothesis-generating only)

The source analysis identifies a small Diamond + Loyalty A group using recorded purchase amount, previous-purchase count, stated purchase cadence, and discount/promo fields. Its observed sample profile can guide creative or service ideas, but it does not prove organic demand or predict lookalike performance. Validate customer attributes and consent before using any audience data in an advertising platform.

## What this dataset cannot answer

There are no dated purchases, offer assignments, discount depths, costs, or follow-up outcomes. It cannot calculate a true retention rate, treatment effect, causal margin lift, or realized savings. The sample-size and test rules must be recalculated when a dated customer-level panel and campaign data are available.
