"""Benchmark Spark aggregation with materialized input and full result collection.

Run via spark-submit on Jetstream2. Do not use local Spark timings to claim
cluster speedup. Use --master or spark-submit --master for selected cluster.
"""
import argparse
import json
import platform
import sys
from pathlib import Path
from time import perf_counter

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))
from spark_transactions import make_spark,load_spark_transactions,aggregate_spark_transactions


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--data-dir',required=True,help='HDFS URI, shared mount, or accessible local directory')
    p.add_argument('--sizes',type=int,nargs='+',default=[10000,100000,1000000])
    p.add_argument('--runs',type=int,default=5)
    p.add_argument('--partitions',type=int)
    p.add_argument('--master',default=None)
    p.add_argument('--label',default='unspecified',help='e.g. 1-worker,2-worker,4-worker')
    p.add_argument('--output',required=True)
    args=p.parse_args()
    if args.runs<1:raise ValueError('runs must be positive')
    spark=make_spark('E516SparkBench',args.master)
    try:
        sc=spark.sparkContext
        results=[]
        for n in args.sizes:
            name=f'banksim_{n}.csv'
            data_uri=args.data_dir.rstrip('/')+'/'+name
            df=load_spark_transactions(spark,data_uri,args.partitions).cache()
            input_count=df.count()  # force input read and cache before timed runs
            times=[];groups=None
            for _ in range(args.runs):
                start=perf_counter()
                collected=aggregate_spark_transactions(df).collect()
                times.append(perf_counter()-start)
                groups=len(collected)
            df.unpersist(blocking=True)
            results.append({'dataset':name,'rows':input_count,'groups':groups,
                            'runs_seconds':times,'mean_seconds':sum(times)/len(times),
                            'min_seconds':min(times),'max_seconds':max(times)})
            print(name, results[-1]['mean_seconds'])
        report={'engine':'pyspark','label':args.label,'timing_boundary':
                'cached input materialized before timer; aggregate and collect all grouped records',
                'note':'Spark task scheduling and collect overhead included; not perfectly identical to Pandas in-process materialization.',
                'spark_version':spark.version,'spark_master':sc.master,
                'default_parallelism':sc.defaultParallelism,
                'configured_partitions':args.partitions,'python':sys.version,
                'platform':platform.platform(),'runs':args.runs,'results':results}
        out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,indent=2))
    finally:
        spark.stop()

if __name__=='__main__':main()
