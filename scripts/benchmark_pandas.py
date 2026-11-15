"""Reproducible Pandas benchmark, keeping original baseline file unchanged."""
import argparse
import json
import platform
import sys
from pathlib import Path
from time import perf_counter
import pandas as pd

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))
from process_transactions import aggregate_transactions


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--data-dir',default=str(ROOT/'data'/'benchmark'))
    p.add_argument('--runs',type=int,default=5)
    p.add_argument('--output',default=str(ROOT/'benchmarks'/'pandas_comparable.json'))
    args=p.parse_args()
    if args.runs<1:raise ValueError('runs must be positive')
    results=[]
    for path in sorted(Path(args.data_dir).glob('banksim_*.csv'),key=lambda x:int(x.stem.split('_')[-1])):
        df=pd.read_csv(path)
        # Dataset loading is outside the timer, and the returned groups are fully
        # materialized to Python records during the timed operation.
        run_times=[]; group_count=None
        for _ in range(args.runs):
            start=perf_counter()
            groups=aggregate_transactions(df).reset_index().to_dict(orient='records')
            elapsed=perf_counter()-start
            run_times.append(elapsed)
            group_count=len(groups)
        results.append({'dataset':path.name,'rows':len(df),'groups':group_count,
                        'runs_seconds':run_times,'mean_seconds':sum(run_times)/len(run_times),
                        'min_seconds':min(run_times),'max_seconds':max(run_times)})
        print(path.name,results[-1]['mean_seconds'])
    report={'engine':'pandas','timing_boundary':'in-memory input; aggregate and materialize all grouped result records',
            'source':'local_execution','runs':args.runs,'python':sys.version,'pandas':pd.__version__,
            'platform':platform.platform(),'processor':platform.processor(),
            'results':results}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2))

if __name__=='__main__':main()
