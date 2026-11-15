import sys
from pathlib import Path
import unittest
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from process_transactions import aggregate_transactions
from generate_report import generate_report
from financial_tools import get_customer_spending,summarize_category
from validate_spark import compare

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.df=pd.DataFrame({'customer':['c1','c1','c2','c1'],
                              'category':['food','food','food','rent'],
                              'amount':[1.0,2.0,5.0,10.0]})
    def test_original_pandas_aggregation(self):
        agg=aggregate_transactions(self.df)
        self.assertEqual(int(agg.loc[('c1','food'),'transactions']),2)
        self.assertEqual(float(agg.loc[('c1','food'),'total_spending']),3.0)
    def test_original_customer_report(self):
        report=generate_report('c1',aggregate_transactions(self.df))
        self.assertEqual(report['total_spending'],13.0)
        self.assertEqual(len(report['categories']),2)
    def test_spark_comparison_logic_matching(self):
        original=aggregate_transactions(self.df)
        rows=original.reset_index().to_dict('records')
        self.assertTrue(compare(original,rows)['passed'])
    def test_spark_comparison_logic_detects_bad_value(self):
        original=aggregate_transactions(self.df)
        rows=original.reset_index().to_dict('records')
        rows[0]['total_spending'] += 1.0
        self.assertFalse(compare(original,rows)['passed'])
    def test_real_dataset_tool_interface(self):
        if not (ROOT/'data'/'bs140513_032310.csv').exists():
            self.skipTest('BankSim CSV not provided')
        r=get_customer_spending("'C1000148617'")
        self.assertEqual(r['customer_id'],"'C1000148617'")
        self.assertGreater(r['total_spending'],0)
        c=summarize_category("'es_transportation'")
        self.assertGreater(c['transactions'],0)

if __name__=='__main__':unittest.main()
