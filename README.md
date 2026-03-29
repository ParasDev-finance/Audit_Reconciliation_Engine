# Audit_Reconciliation_Engine
A Polars-based data pipeline for automating bank ledger reconciliation and anomaly detection.
# Automated Financial Audit & Reconciliation Engine

## 📌 Business Overview
In corporate finance, manual bank reconciliation is highly prone to human error and consumes hundreds of hours of auditor time. This project is a highly optimized, automated data pipeline designed to ingest, clean, and reconcile massive financial ledgers against bank statements in milliseconds.

Instead of relying on basic spreadsheet lookups, this tool leverages **Polars** (a multithreaded, Rust-based DataFrame library) to process large-scale financial data and automatically flag critical audit exceptions.

## ⚙️ Core Features
* **Enterprise-Scale Data Ingestion:** Capable of processing 10,000+ transaction records instantly.
* **Intelligent Data Cleaning:** Automatically standardizes inconsistent date formats (e.g., mixing `YYYY-MM-DD` and `DD/MM/YYYY`) using SQL-style `coalesce` logic.
* **Automated Exception Hunting:** Executes a full outer join to isolate three critical audit anomalies:
  1. **Outstanding Items:** Recorded in the ledger but un-cleared by the bank.
  2. **Unrecorded Liabilities:** Hidden bank fees or withdrawals not present in the company ledger.
  3. **Financial Mismatches:** Typographical errors in transaction amounts.
* **Variance Calculation:** Automatically calculates the exact monetary variance for any mismatched transactions.
* **Executive Dashboard:** Utilizes Seaborn and Matplotlib to generate a visual summary of audit findings, including a variance distribution histogram to separate minor typos from major financial discrepancies.

## 🛠️ Tech Stack
* **Language:** Python
* **Data Engineering:** Polars (Rust-backed engine for hyper-fast data processing), Pandas (for synthetic data generation)
* **Visualization:** Matplotlib, Seaborn

## 🚀 How to Run
1. Run `main.py`.
2. The script will automatically generate 10,000 rows of synthetic, "messy" financial data (`messy_ledger.csv` and `messy_bank_statement.csv`).
3. The Polars engine will clean the data, execute the reconciliation, and print a comprehensive Audit Report to the console.
4. A visual dashboard will render showing the distribution of anomalies. 

## 📊 Sample Output
 ⚙️ Generating 10,000 baseline transactions...
🌪️ Chaos successfully injected! CSVs saved.

🧹 Cleaning data and standardizing dates...
--- 🚨 AUTOMATED AUDIT REPORT 🚨 ---
Total Transactions Scanned: 10050
1. Outstanding Items Found: 200
2. Unrecorded Bank Items Found: 50
3. Amount Mismatches Found: 98

![capture_temp](https://github.com/user-attachments/assets/03bdbf48-612a-44ac-a890-b36c7e255614)


