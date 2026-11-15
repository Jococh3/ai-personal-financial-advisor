"""Validate Spark aggregation against the preserved original Pandas code."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
from process_transactions import aggregate_transactions
from spark_transactions import (make_spark, load_spark_transactions,
                                aggregate_spark_transactions)


def compare(pandas_agg, spark_rows, tolerance=0.011):
    """Return a detailed comparison; strict counts, cent-tolerant floats."""
    p = pandas_agg.reset_index()
    p['customer'] = p['customer'].astype(str)
    p['category'] = p['category'].astype(str)
    s = pd.DataFrame(spark_rows, columns=['customer', 'category', 'transactions',
                                          'total_spending', 'average_transaction'])
    merged = p.merge(s, on=['customer','category'], how='outer', indicator=True,
                     suffixes=('_pandas','_spark'), validate='one_to_one')
    missing = merged[merged['_merge'] != 'both']
    matched = merged[merged['_merge'] == 'both'].copy()
    counts_bad = matched[matched['transactions_pandas'] != matched['transactions_spark']]
    total_diff = (matched['total_spending_pandas'] - matched['total_spending_spark']).abs()
    avg_diff = (matched['average_transaction_pandas'] - matched['average_transaction_spark']).abs()
    values_bad = matched[(total_diff > tolerance) | (avg_diff > tolerance)]
    result = {
        'passed': bool(missing.empty and counts_bad.empty and values_bad.empty),
        'pandas_groups': int(len(p)), 'spark_groups': int(len(s)),
        'missing_or_extra_groups': int(len(missing)),
        'transaction_count_mismatches': int(len(counts_bad)),
        'amount_mismatches': int(len(values_bad)),
        'max_total_difference': float(total_diff.max()) if len(total_diff) else 0.0,
        'max_average_difference': float(avg_diff.max()) if len(avg_diff) else 0.0,
        'tolerance': tolerance,
        'sample_mismatches': pd.concat([missing,counts_bad,values_bad]).head(5)
                             .astype(object).where(pd.notna(pd.concat([missing,counts_bad,values_bad]).head(5)), None)
                             .to_dict(orient='records'),
    }
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--csv', default=str(ROOT/'data'/'bs140513_032310.csv'))
    parser.add_argument('--master', default=None)
    parser.add_argument('--partitions', type=int)
    parser.add_argument('--output', default=str(ROOT/'results'/'spark_validation.json'))
    args=parser.parse_args()
    spark=make_spark('E516Validation',args.master)
    try:
        pdf=pd.read_csv(args.csv)
        p=aggregate_transactions(pdf)
        sdf=load_spark_transactions(spark,args.csv,args.partitions)
        rows=[r.asDict() for r in aggregate_spark_transactions(sdf).collect()]
        report=compare(p,rows)
        dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(report,indent=2,default=str))
        print(json.dumps({k:v for k,v in report.items() if k!='sample_mismatches'},indent=2))
        if not report['passed']:
            raise SystemExit(1)
    finally:
        spark.stop()

if __name__=='__main__':main()
