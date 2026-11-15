"""Run only on an environment with PySpark installed (Jetstream2 or local Spark)."""
import importlib.util
import sys
from pathlib import Path
import unittest
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from process_transactions import aggregate_transactions
from validate_spark import compare
from spark_transactions import make_spark,aggregate_spark_transactions

@unittest.skipUnless(importlib.util.find_spec('pyspark'),'PySpark not installed: run on Jetstream2')
class SparkRuntimeTests(unittest.TestCase):
    def test_aggregation_matches_pandas(self):
        pdf=pd.DataFrame({'customer':['c1','c1','c2','c1'],
                          'category':['food','food','food','rent'],
                          'amount':[1.0,2.0,5.0,10.0]})
        spark=make_spark('E516UnitTest','local[2]')
        try:
            sdf=spark.createDataFrame(pdf)
            results=[r.asDict() for r in aggregate_spark_transactions(sdf).collect()]
            self.assertTrue(compare(aggregate_transactions(pdf),results)['passed'])
        finally:spark.stop()
