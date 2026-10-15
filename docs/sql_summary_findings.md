SQL Segmentation Findings Summary

**Scope note:** These are descriptive results from a one-row-per-shopper snapshot. The loyalty labels are constructed proxies. Without timestamps, offer assignment, or margin data, the analysis does not measure retention, promotion lift, or profitability.

Query Block 1: Loyalty & Value Distribution
- Diamond tier customers (15% of base) drive an average spend of $83.79 and have remarkably high tenure (41.4 average previous purchases), compared to Bronze's $40.29 and 12.2 previous purchases.
- Discount usage is similar across the top and bottom constructed tiers: 42.9% of Diamond and 41.6% of Bronze records. This raises a testable question about promo targeting; it does not show that either group would buy without discounts.
- Loyalty Definition B captures more of the sample's recorded purchase amounts ($69,536 exclusively) than Definition A ($4,069 exclusively); both are constructed proxies, not verified retention groups.

Query Block 2: Category & Season Patterns
- Accessories (avg 25.73 previous purchases) and Footwear (25.23) are associated with higher reported previous-purchase counts; the snapshot cannot establish category-driven retention.
- Winter is the strongest retention season (highest avg previous purchases at 25.92), while Fall attracts the highest average spend ($61.56) despite having the lowest discount usage rate (40.7%).

Query Block 3: Geographic Segmentation
- Alaska ($67.60), Arizona ($66.55), and Virginia ($62.88) rank highly on sample average spend with lower promo-dependency scores. The geography labels are descriptive prioritization hypotheses, not evidence of incremental demand.
- Conversely, states like Pennsylvania ($66.57 spend, 1.31 promo score) and West Virginia ($63.88 spend, 1.42 promo score) represent "Promo-Dependent Strongholds" where high sales are driven heavily by discounts.

Query Block 4: Payment & Shipping
- Diamond customers heavily favor Credit Card (18.3%), Debit Card (17.8%), and Paypal (17.6%).
- The strict Definition A proxy over-indexes on Store Pickup (17.6% of group) and Free Shipping (17.4%), a pattern to investigate in a dated customer panel.

Query Block 5: Ideal Customer Profile
- The narrow Diamond + Loyalty A proxy skews toward the reported "Core Millennial" bracket and Clothing/Accessories records; it is a descriptive profile, not a verified retained cohort.
- Their purchase behavior is highly frequent (Weekly/Bi-Weekly) and they utilize diverse payment methods (Cash, Credit Card, Bank Transfer) across varying seasons.
