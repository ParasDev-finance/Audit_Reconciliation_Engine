# ==========================================
# IMPORTS
# ==========================================
import pandas as pd
import numpy as np
import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import random
from datetime import datetime, timedelta

# ==========================================
# STEP 1: GENERATE DUMMY DATA (PANDAS)
# ==========================================
print("⚙️ Generating 10,000 baseline transactions...")
num_records = 10000
start_date = datetime(2026, 1, 1)

tx_ids = [f"TXN-{str(i).zfill(5)}" for i in range(1, num_records + 1)]
dates = [(start_date + timedelta(days=random.randint(0, 89))).strftime('%Y-%m-%d') for _ in range(num_records)]
descriptions = random.choices(
    ['Client Payment', 'Vendor Payment', 'Software Sub', 'Office Supplies', 'Consulting'], 
    k=num_records
)
amounts = np.round(np.random.uniform(-5000, 15000, num_records), 2)

master_df = pd.DataFrame({'Transaction_ID': tx_ids, 'Date': dates, 'Description': descriptions, 'Amount': amounts})

# Create Company Ledger (With Formatting Errors)
ledger_df = master_df.copy()
messy_indices = ledger_df.sample(frac=0.05).index
ledger_df.loc[messy_indices, 'Date'] = pd.to_datetime(ledger_df.loc[messy_indices, 'Date']).dt.strftime('%d/%m/%Y')

# Create Bank Statement (With Audit Exceptions)
bank_df = master_df.copy()
bank_df = bank_df.drop(bank_df.sample(frac=0.02).index) # Exception A: Outstanding
mismatch_indices = bank_df.sample(frac=0.01).index
bank_df.loc[mismatch_indices, 'Amount'] = bank_df.loc[mismatch_indices, 'Amount'] + 10.50 # Exception B: Typos

extra_bank_records = pd.DataFrame({
    'Transaction_ID': [f"FEE-{str(i).zfill(4)}" for i in range(1, 51)],
    'Date': ['2026-03-31'] * 50,
    'Description': ['Monthly Account Fee'] * 50,
    'Amount': [-15.00] * 50
})
bank_df = pd.concat([bank_df, extra_bank_records], ignore_index=True) # Exception C: Unrecorded Fees

ledger_df = ledger_df.sample(frac=1).reset_index(drop=True)
bank_df = bank_df.sample(frac=1).reset_index(drop=True)

ledger_df.to_csv('messy_ledger.csv', index=False)
bank_df.to_csv('messy_bank_statement.csv', index=False)
print("🌪️ Chaos successfully injected! CSVs saved.\n")

# ==========================================
# STEP 2: INGEST & CLEAN DATA (POLARS)
# ==========================================
print("🧹 Cleaning data and standardizing dates...")
ledger_df_pl = pl.read_csv('messy_ledger.csv')
bank_df_pl = pl.read_csv('messy_bank_statement.csv')

ledger_clean = ledger_df_pl.with_columns(
    pl.coalesce([
        pl.col("Date").str.to_date("%Y-%m-%d", strict=False),
        pl.col("Date").str.to_date("%d/%m/%Y", strict=False)
    ]).alias("Date_Cleaned")
)

bank_clean = bank_df_pl.with_columns(
    pl.col("Date").str.to_date("%Y-%m-%d", strict=False).alias("Date_Cleaned")
)

# ==========================================
# STEP 3: THE RECONCILIATION ENGINE (POLARS)
# ==========================================
ledger_prep = ledger_clean.rename({"Amount": "Amount_Ledger", "Description": "Desc_Ledger"})
bank_prep = bank_clean.rename({"Amount": "Amount_Bank", "Description": "Desc_Bank"})

merged_df = ledger_prep.join(bank_prep, on='Transaction_ID', how='full')

outstanding_items = merged_df.filter(pl.col('Amount_Bank').is_null())
unrecorded_items = merged_df.filter(pl.col('Amount_Ledger').is_null())

mismatches = merged_df.filter(
    pl.col('Amount_Ledger').is_not_null() & 
    pl.col('Amount_Bank').is_not_null() & 
    (pl.col('Amount_Ledger') != pl.col('Amount_Bank'))
).with_columns(
    (pl.col('Amount_Ledger') - pl.col('Amount_Bank')).round(2).alias('Variance')
)

print("--- 🚨 AUTOMATED AUDIT REPORT 🚨 ---")
print(f"Total Transactions Scanned: {merged_df.shape[0]}")
print(f"1. Outstanding Items Found: {outstanding_items.shape[0]}")
print(f"2. Unrecorded Bank Items Found: {unrecorded_items.shape[0]}")
print(f"3. Amount Mismatches Found: {mismatches.shape[0]}\n")

# ==========================================
# STEP 4: VISUAL DASHBOARD (SEABORN/MATPLOTLIB)
# ==========================================
exception_counts = {
    'Outstanding Items': outstanding_items.shape[0],
    'Unrecorded Bank Items': unrecorded_items.shape[0],
    'Amount Mismatches': mismatches.shape[0]
}

mismatches_pd = mismatches.select('Variance').to_pandas()

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
sns.set_theme(style="whitegrid")

# Chart 1: Exception Breakdown
sns.barplot(
    x=list(exception_counts.keys()), 
    y=list(exception_counts.values()), 
    ax=axes[0], 
    palette=['#ff9999', '#66b3ff', '#99ff99'],
    hue=list(exception_counts.keys()),
    legend=False
)
axes[0].set_title('Audit Exceptions by Category', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Number of Transactions')

for i, v in enumerate(exception_counts.values()):
    axes[0].text(i, v + 2, str(v), ha='center', fontweight='bold', fontsize=12)

# Chart 2: Variance Distribution
sns.histplot(data=mismatches_pd, x='Variance', bins=20, kde=True, color='coral', ax=axes[1])
axes[1].set_title('Distribution of Financial Variances (₹)', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Variance Amount')
axes[1].set_ylabel('Frequency')

plt.tight_layout()
plt.show()
