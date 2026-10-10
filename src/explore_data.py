from pathlib import Path
import pandas as pd
import json
from process_transactions import load_transactions, aggregate_transactions
from generate_report import generate_report
from statistics import mean
from time import perf_counter

# Find the Project Folder
project_dir = Path(__file__).resolve().parent.parent

# Define the location of our dataset
csv_path = project_dir / "data" / "bs140513_032310.csv"

# Load the CSV into a Pandas DataFrame
df = load_transactions()

# Display the first five transactions
print("\nFirst five transactions")
print(df.head())

# Display information about the dataset
print("\nDataset information:")
df.info()

# Check for missing values
print("\nMissing values:")
print(df.isnull().sum())

# Check for duplicated transactions
print("\nDuplicate rows:")
print(df.duplicated().sum())

# Check for invalid transaction amounts
print("\nNegative transaction amounts:")
print((df["amount"] < 0).sum())

# Examine transcation categories
print("\nTransaction categories:")
print(df["category"].value_counts())

# Examine transaction amount statistics
print("\nTransaction statistics:")
print(df.describe())

# Calculate total spending by category
spending_by_category = (
    df.groupby("category")["amount"].sum().sort_values(ascending=False)
)

print("\nTotal spending by category:")
print(spending_by_category)

# Calculate spending statistics by category
category_stats = (
    df.groupby("category")["amount"]
    .agg(transactions="count", total_spending="sum", average_transaction="mean")
    .sort_values(by="average_transaction", ascending=False)
)

print("\nSpending statistics by category:")
print(category_stats.round(2))


from statistics import mean
from time import perf_counter

# Run aggregation five times
execution_times = []

for run in range(5):
    start_time = perf_counter()

    customer_spending = aggregate_transactions(df)

    end_time = perf_counter()

    elapsed = end_time - start_time
    execution_times.append(elapsed)

    print(f"\nRun {run + 1}: {elapsed:.6f} seconds")

average_time = mean(execution_times)

print(f"\nAverage aggregation time: {average_time:.6f} seconds")
print(f"Fastest run: {min(execution_times):.6f} seconds")
print(f"Slowest run: {max(execution_times):.6f} seconds")

# Save Pandas benchmark results
benchmark_results = {
    "engine": "pandas",
    "operation": "customer_category_aggregation",
    "transaction_count": len(df),
    "runs_seconds": execution_times,
    "average_seconds": average_time,
    "fastest_seconds": min(execution_times),
    "slowest_seconds": max(execution_times),
}

# Create the benchmark directory
benchmark_dir = project_dir / "benchmarks"
benchmark_dir.mkdir(parents=True, exist_ok=True)

# Save results as JSON
benchmark_path = benchmark_dir / "pandas_bsaline.json"

with open(benchmark_path, "w", encoding="utf-8") as file:
    json.dump(benchmark_results, file, indent=4)

print("\nCustomer spending breakdown:")
print(customer_spending.head(15))

# Select an individual customer's spending profile
customer_id = "'C1000148617'"

customer_report = customer_spending.loc[customer_id]

print(f"\nFinancial report for {customer_id}:")
print(customer_report)

# Calculate their total spending across all categories
total_spending = customer_report["total_spending"].sum()

print(f"\nTotal spending: ${total_spending:,.2f}")

# Test the function
report = generate_report("'C1000148617'", customer_spending)

print("\nCustomer financial report:")
print(report)

# Create output directory
output_dir = project_dir / "results"
output_dir.mkdir(parents=True, exist_ok=True)

# Define the output file location
output_path = output_dir / "customer_report.json"

# Save the report as JSON
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(report, file, indent=4)

print(f"\nReport saved to: {output_path}")

# Read the JSON report
with open(output_path, "r", encoding="utf-8") as file:
    saved_report = json.load(file)

# Verifying the saved data
print("\nSaved report verification:")
print("Customer:", saved_report["customer_id"])
print("Total spending:", saved_report["total_spending"])
print("Categories:", len(saved_report["categories"]))

assert saved_report == report, "Saved report does not match!"
print("JSON verification passed!")
