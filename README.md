# Decoding Customer Value: A SQL-Driven Retention Strategy

An end-to-end customer analytics project for a U.S. direct-to-consumer fashion retailer. It combines Python data preparation, SQLite analysis, customer value proxies, and a Power BI dashboard to examine discount use and shopper behavior.

## What the analysis covers

- 3,900 unique shopper records and 18 source fields; the sum of the sample's recorded purchase amounts is **$233,081**.
- Python cleaning and feature engineering for a composite customer value index, promotion-dependency score, behavioral loyalty proxies, and four value tiers.
- Five SQLite query groups covering customer tiers, discount use, category and season patterns, geography, payment/shipping, and a narrow ideal-customer profile.
- A four-page Power BI report with customer-value, promotion-use, category, and geography views.
- A segment-level promotion strategy and executive summary.

### Selected descriptive finding

The source analysis reports discount use for **42.9% of Diamond-tier records** and **41.6% of Bronze-tier records**. The similar rates raise a useful business question: test whether high-value shoppers need the same promotions as lower-value shoppers. These are descriptive associations from the supplied sample, not evidence that discounts caused repeat purchases or that withdrawing them will preserve sales.

## Stack

Python (`pandas`, `numpy`, `scikit-learn`), SQLite (CTEs and window functions), and Power BI Desktop (`.pbip` / `.pbir`).

## Run locally

1. Create a Python environment and install the requirements:

   ```bash
   pip install -r requirements.txt
   ```

2. Put the provided source file at the project root as `Dataset.csv`.
3. Run feature engineering and the SQL outputs from the project root:

   ```bash
   python src/feature_engineering.py
   python sql/run_queries.py
   ```

4. Prepare the local Power BI inputs and update its data paths:

   ```bash
   python powerbi/prepare_data.py
   python powerbi/fix_paths.py
   ```

5. Open `powerbi/dashboard.pbip` in Power BI Desktop and refresh the report.

The raw dataset, `powerbi/Data/*.csv`, and generated `project_output/` files are excluded from Git. The archive also contains duplicate submission/build outputs; the organized source files listed above are the working versions.

## Data source

The 3,900-row schema matches Sourav Banerjee's [Customer Shopping Trends dataset on Kaggle](https://www.kaggle.com/datasets/iamsouravbanerjee/customer-shopping-trends-dataset). The raw CSV is excluded from Git; download it from the source and follow the dataset's current terms before redistribution.

## Data limits and interpretation

Each row is one shopper record, not a timestamped transaction history. There is no observed churn outcome, intervention assignment, discount depth, gross margin, or follow-up period. Accordingly, `previous_purchases`, stated purchase frequency, and the derived loyalty flags are proxies. The project can describe the sample and propose a retention experiment; it cannot calculate a true retention rate, causal promotion effect, or measured margin recovery.

The original playbook includes hypothetical revenue and margin scenarios. They are not measured outcomes and should only be used with their assumptions clearly stated. See [the data limitations note](docs/data_limits.md).
