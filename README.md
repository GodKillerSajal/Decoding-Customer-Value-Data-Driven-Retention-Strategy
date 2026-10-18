# Decoding Customer Value: A SQL-Driven Retention Strategy

An end-to-end customer analytics and retention intelligence project for a direct-to-consumer fashion retailer. The project integrates Python data pipelines, SQLite analytical queries, customer value segmentation, and a multi-page Power BI dashboard to optimize promotional strategies and increase customer lifetime value.

---

## 1. What the Analysis Covers

- **Customer Portfolio**: 3,900 unique shopper records across 18 transaction attributes representing **$233,081** in aggregate spend.
- **Feature Engineering & Segmentation**: Python data preparation generating composite customer value indices, promotion-dependency scores, behavioral loyalty flags, and 4 value tiers (Diamond, Gold, Silver, Bronze).
- **Relational SQL Analytics**: Modular SQLite analytical queries (CTEs and window functions) investigating tier distribution, discount elasticity, category/seasonal purchase cycles, and geographic concentrations.
- **Interactive Power BI Reporting**: 4-page Power BI report visualising customer lifetime value distributions, promotion sensitivity, product categories, and regional demand.
- **Strategic Retention Framework**: Targeted promotional recommendations designed to protect margins and reduce discount reliance among high-value tiers.

### Key Analytical Insight
The analysis revealed that promotional discounts were applied to **42.9% of Diamond-tier purchases** and **41.6% of Bronze-tier purchases**. The near-identical discount exposure across tiers indicates significant margin leakage, highlighting an immediate opportunity to substitute broad discounting with targeted loyalty perks for high-value shoppers.

---

## 2. Tech Stack

- **Data Processing**: Python (`pandas`, `numpy`, `scikit-learn`)
- **Database & Querying**: SQLite (Common Table Expressions, Window Functions)
- **Business Intelligence**: Power BI Desktop (`.pbip` / `.pbir`)

---

## 3. How to Run Locally

### Environment Setup
```bash
pip install -r requirements.txt
```

### Feature Engineering & SQL Analytics
Place `Dataset.csv` at the project root and execute:
```bash
python src/feature_engineering.py
python sql/run_queries.py
```

### Power BI Report Setup
```bash
python powerbi/prepare_data.py
python powerbi/fix_paths.py
```
Open `powerbi/dashboard.pbip` in Power BI Desktop and refresh the data connections.

---

## 4. Analytical Methodology & Data Scope

The analysis leverages customer transaction profiles to model customer lifetime value proxies and segment behaviors. Financial scenario models provide projected impact estimates based on stated promotional elasticity parameters.
