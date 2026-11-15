"""PySpark equivalent of the original Pandas customer/category aggregation.

This module is importable without PySpark installed; a Spark runtime is needed to
execute its functions. Intended for Spark 3.5.6 on Jetstream2.
"""
from __future__ import annotations


def make_spark(app_name: str = "E516FinancialData", master: str | None = None):
    from pyspark.sql import SparkSession
    builder = SparkSession.builder.appName(app_name)
    if master:
        builder = builder.master(master)
    return builder.getOrCreate()


def load_spark_transactions(spark, csv_path: str, partitions: int | None = None):
    from pyspark.sql import functions as F
    from pyspark.sql import types as T
    # Only the three columns used by the original Pandas aggregation are needed.
    schema = T.StructType([
        T.StructField("customer", T.StringType(), True),
        T.StructField("category", T.StringType(), True),
        T.StructField("amount", T.DoubleType(), True),
    ])
    # Use header-aware CSV parsing, selecting fields by name rather than position.
    df = (spark.read.option("header", True).option("mode", "FAILFAST")
          .option("inferSchema", False).csv(csv_path)
          .select(F.col("customer"), F.col("category"),
                  F.col("amount").cast("double").alias("amount")))
    if partitions is not None:
        if partitions < 1:
            raise ValueError("partitions must be a positive integer")
        df = df.repartition(partitions)
    return df


def aggregate_spark_transactions(df):
    """Return customer/category totals mirroring process_transactions.py.

    Original Pandas groupby drops null keys, counts non-null amounts, and rounds
    numeric summaries to 2 decimals. Spark's round uses HALF_UP, unlike Pandas'
    binary floating-point/banker's tie behavior; validation allows cent-level
    rounding tolerances and reports differences instead of hiding them.
    """
    from pyspark.sql import functions as F
    return (df.filter(F.col("customer").isNotNull() & F.col("category").isNotNull())
            .groupBy("customer", "category")
            .agg(F.count("amount").alias("transactions"),
                 F.round(F.sum("amount"), 2).alias("total_spending"),
                 F.round(F.avg("amount"), 2).alias("average_transaction")))


def collect_spark_aggregation(df):
    """Materialize result for benchmarking and external integration."""
    return [row.asDict(recursive=True) for row in df.collect()]
