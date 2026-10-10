# AI Personal Financial Advisor

An ENGR-E516 Engineering Cloud Computing project at Indiana University exploring how transaction aggregation can support personal financial insights. The current implementation provides a local Pandas pipeline; distributed processing and AI advice are planned.

## Completed: Pandas pipeline

- Load the BankSim CSV and inspect its schema, missing values, duplicate rows, negative amounts, categories, and transaction statistics.
- Aggregate transaction count, total spending, and average transaction amount by customer and category.
- Generate a structured spending report for a selected synthetic customer, save it as JSON, and verify the saved report matches the generated report.
- Measure customer/category aggregation over five runs and save the timing results.

### Project files

| Path | Purpose |
| --- | --- |
| `src/explore_data.py` | Runs exploration, aggregation benchmarks, and report generation |
| `src/process_transactions.py` | Loads transactions and aggregates spending |
| `src/generate_report.py` | Builds a customer spending report |
| `benchmarks/pandas_bsaline.json` | Existing Pandas benchmark results (filename preserved) |
| `results/customer_report.json` | Example report using synthetic BankSim customer data |
| `requirements.txt` | Python dependencies |

## Setup and usage

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
```

Download the [BankSim synthetic financial payment dataset from Kaggle](https://www.kaggle.com/datasets/ealaxi/banksim1) and place `bs140513_032310.csv` in the project's `data/` directory. The CSV is excluded from Git; follow the dataset provider's license and terms.

Run from the project root:

```powershell
.\.venv\Scripts\python.exe src\explore_data.py
```

This command prints exploration results and regenerates `benchmarks/pandas_bsaline.json` and `results/customer_report.json`.

## Recorded Pandas benchmark

Source: `benchmarks/pandas_bsaline.json`, using 594,643 transactions and five aggregation runs.

| Metric | Seconds |
| --- | ---: |
| Average | 0.089895 |
| Fastest | 0.088015 |
| Slowest | 0.093758 |

The timer covers customer/category aggregation on an already loaded DataFrame, including rounding. CSV loading, exploration, and report serialization are outside the timed operation. These results are a local baseline; hardware and runtime metadata were not recorded, so they do not establish distributed performance or speedup.

## Planned: PySpark and Jetstream2

- Implement equivalent customer/category aggregation with PySpark and validate results against Pandas.
- Deploy the distributed workflow on Jetstream2.
- Compare runtime and scaling across dataset sizes and compute configurations, recording reproducible environment details.
- Add an AI advice layer based on structured spending summaries.

These features are not implemented in the current repository.

## Data handling

Use synthetic BankSim data for development. Do not commit personal financial records, raw dataset CSVs, environment files, or credentials. `.gitignore` excludes the virtual environment, Python caches, local dataset CSVs, and common credential file patterns.
