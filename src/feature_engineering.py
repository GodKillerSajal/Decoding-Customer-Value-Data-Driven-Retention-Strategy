import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import MinMaxScaler
import os

# Create directories
os.makedirs('project_output/python', exist_ok=True)
os.makedirs('project_output/sql', exist_ok=True)
os.makedirs('project_output/powerbi', exist_ok=True)
os.makedirs('project_output/playbook', exist_ok=True)

# 1. Load data
df = pd.read_csv('Dataset.csv')

print("Starting Data Cleaning...")

# Step 1: Null audit & Imputation
review_nulls = df['Review Rating'].isnull().sum()
review_median = df['Review Rating'].median()
df['rating_was_null'] = df['Review Rating'].isnull().astype(int)
df['Review Rating'] = df['Review Rating'].fillna(review_median)

# Step 2: Type validation (Nothing to change, just confirm)
# Purchase Amount (USD) is int64 as confirmed

# Step 3: Duplicate detection
duplicates = df['Customer ID'].duplicated().sum()

# Step 4: Range validation
age_flags = ((df['Age'] < 18) | (df['Age'] > 75)).sum()
amount_flags = (df['Purchase Amount (USD)'] <= 0).sum()
rating_flags = ((df['Review Rating'] < 1.0) | (df['Review Rating'] > 5.0)).sum()
prev_purchases_flags = (df['Previous Purchases'] <= 0).sum()
total_flags = age_flags + amount_flags + rating_flags + prev_purchases_flags

# Step 5: Categorical standardization
cat_cols = ['Gender', 'Item Purchased', 'Category', 'Location', 'Size', 'Color', 'Season', 'Subscription Status', 'Shipping Type', 'Discount Applied', 'Promo Code Used', 'Payment Method', 'Frequency of Purchases']
for col in cat_cols:
    df[col] = df[col].astype(str).str.strip().str.title()
    
# Step 2 from Instructions: Column Renaming
def to_snake(col):
    col = col.strip().lower()
    col = re.sub(r'[^\w\s]', '', col)   # remove parentheses, special chars
    col = re.sub(r'\s+', '_', col)       # spaces to underscores
    return col

df.columns = [to_snake(c) for c in df.columns]

# Save cleaned data
df.to_csv('project_output/python/cleaned_data.csv', index=False)
print("Cleaned data saved.")

# Feature 1: Promo Dependency Score
def freq_to_promo_flag(freq):
    if freq in ['Weekly', 'Bi-Weekly', 'Fortnightly']:
        return 0
    elif freq == 'Monthly':
        return 0
    elif freq in ['Quarterly', 'Every 3 Months', 'Annually']:
        return 1
    else:
        return 0

df['freq_promo_flag'] = df['frequency_of_purchases'].apply(freq_to_promo_flag)
df['promo_dependency_score'] = (
    (df['discount_applied'] == 'Yes').astype(int)
    + (df['promo_code_used'] == 'Yes').astype(int)
    + df['freq_promo_flag']
)

# Feature 2: Value Tier
freq_map = {
    'Weekly': 6,
    'Bi-Weekly': 5,
    'Fortnightly': 4,
    'Monthly': 3,
    'Every 3 Months': 2,
    'Quarterly': 1.5,
    'Annually': 1
}
df['frequency_score'] = df['frequency_of_purchases'].map(freq_map)

scaler = MinMaxScaler()
df['norm_purchase_amount'] = scaler.fit_transform(df[['purchase_amount_usd']])
df['norm_previous_purchases'] = scaler.fit_transform(df[['previous_purchases']])
df['norm_review_rating'] = scaler.fit_transform(df[['review_rating']])
df['norm_frequency_score'] = scaler.fit_transform(df[['frequency_score']])

df['composite_score'] = (
    df['norm_purchase_amount']    * 0.35
    + df['norm_previous_purchases'] * 0.40
    + df['norm_review_rating']      * 0.15
    + df['norm_frequency_score']    * 0.10
)

p25 = df['composite_score'].quantile(0.25)
p50 = df['composite_score'].quantile(0.50)
p85 = df['composite_score'].quantile(0.85)

def assign_tier(score):
    if score >= p85:
        return 'Diamond'
    elif score >= p50:
        return 'Gold'
    elif score >= p25:
        return 'Silver'
    else:
        return 'Bronze'

df['value_tier'] = df['composite_score'].apply(assign_tier)

# Feature 3: Satisfaction Flag
df['satisfaction_flag'] = (df['review_rating'] >= 4.0).astype(int)

# Feature 4: Loyalty A
prev_purchases_median = df['previous_purchases'].median()
df['loyalty_a'] = (
    (df['previous_purchases'] >= prev_purchases_median)
    & (df['frequency_of_purchases'].isin(['Weekly', 'Bi-Weekly', 'Fortnightly']))
    & (df['promo_code_used'] == 'No')
    & (df['discount_applied'] == 'No')
).astype(int)

# Feature 5: Loyalty B
p60_composite = df['composite_score'].quantile(0.60)
df['loyalty_b'] = (
    (df['composite_score'] >= p60_composite)
    & (df['previous_purchases'] >= prev_purchases_median)
).astype(int)

# Comparing Loyalty A vs Loyalty B
loyalty_comparison = f"""Metric | Loyalty A | Loyalty B
---|---|---
% of total customers labeled loyal | {df['loyalty_a'].mean()*100:.1f}% | {df['loyalty_b'].mean()*100:.1f}%
Average Purchase Amount (USD) | ${df[df['loyalty_a']==1]['purchase_amount_usd'].mean():.2f} | ${df[df['loyalty_b']==1]['purchase_amount_usd'].mean():.2f}
Average Previous Purchases | {df[df['loyalty_a']==1]['previous_purchases'].mean():.1f} | {df[df['loyalty_b']==1]['previous_purchases'].mean():.1f}
Average Promo Dependency Score | {df[df['loyalty_a']==1]['promo_dependency_score'].mean():.2f} | {df[df['loyalty_b']==1]['promo_dependency_score'].mean():.2f}
Revenue share (sum purchase_amount_usd / total) | {(df[df['loyalty_a']==1]['purchase_amount_usd'].sum() / df['purchase_amount_usd'].sum())*100:.1f}% | {(df[df['loyalty_b']==1]['purchase_amount_usd'].sum() / df['purchase_amount_usd'].sum())*100:.1f}%

Recommendation:
Based on the revenue share and organic engagement, Loyalty B captures a substantially larger segment of the high-value base and revenue. However, Definition A identifies the truly organic, highly engaged, and promo-independent segment. For the purpose of protecting the core business while sunsetting promos, we will use Definition A for the strictest profiling, but Definition B indicates that some highly valuable customers still occasionally use promos. The sunset strategy should aim to convert Loyalty B customers into Loyalty A over time.
"""

with open('project_output/python/loyalty_comparison.txt', 'w') as f:
    f.write(loyalty_comparison)
    
print("Loyalty comparison saved.")

# Feature 6: Purchase Frequency Numeric
df['frequency_numeric'] = df['frequency_score']  # since we already mapped it

# Feature 7: Is Subscriber
df['is_subscriber'] = (df['subscription_status'] == 'Yes').astype(int)

# Feature 8: Age Bracket
def assign_age_bracket(age):
    if age <= 25: return 'Young Adult'
    elif age <= 35: return 'Core Millennial'
    elif age <= 45: return 'Older Millennial'
    elif age <= 59: return 'Gen X'
    else: return 'Senior'

df['age_bracket'] = df['age'].apply(assign_age_bracket)

# Save Customer Features
df.to_csv('project_output/python/customer_features.csv', index=False)
print("Customer features saved.")

# Print Summary
print(f"""
========================================
DATA PIPELINE SUMMARY
========================================
Total customers:                    {len(df)}
Rows with imputed Review Rating:    {review_nulls} ({review_nulls/len(df)*100:.1f}%)
Loyalty A rate:                     {df['loyalty_a'].mean()*100:.1f}%
Loyalty B rate:                     {df['loyalty_b'].mean()*100:.1f}%
Promo-dependent (score = 3):        {(df['promo_dependency_score'] == 3).sum()} ({(df['promo_dependency_score'] == 3).mean()*100:.1f}%)
Diamond tier customers:             {(df['value_tier'] == 'Diamond').sum()} ({(df['value_tier'] == 'Diamond').mean()*100:.1f}%)
Average composite score:            {df['composite_score'].mean():.3f}
Age range in dataset:               {df['age'].min()} to {df['age'].max()}
Flags triggered (out-of-range):     {total_flags}
========================================
""")
