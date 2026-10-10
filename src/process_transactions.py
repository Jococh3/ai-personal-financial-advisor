from pathlib import Path
import pandas as pd


def load_transactions():
    # Find the project root directory
    project_dir = Path(__file__).resolve().parent.parent

    # Locate the dataset
    csv_path = project_dir / "data" / "bs140513_032310.csv"

    # Load the dataset into a DataFrame
    df = pd.read_csv(csv_path)

    return df


def aggregate_transactions(df):
    # Group transactions by customer and category
    customer_spending = (
        df.groupby(["customer", "category"])
        .agg(
            transactions=("amount", "count"),
            total_spending=("amount", "sum"),
            average_transaction=("amount", "mean"),
        )
        .round(2)
    )

    return customer_spending
