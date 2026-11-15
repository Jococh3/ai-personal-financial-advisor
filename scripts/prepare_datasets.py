"""Create deterministic benchmark CSVs; 1M rows resampled from synthetic BankSim."""
import argparse
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parent.parent

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--input',default=str(ROOT/'data'/'bs140513_032310.csv'))
    a.add_argument('--output-dir',default=str(ROOT/'data'/'benchmark'))
    a.add_argument('--sizes',type=int,nargs='+',default=[10000,100000,1000000])
    a.add_argument('--seed',type=int,default=516)
    args=a.parse_args()
    source=pd.read_csv(args.input)
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    manifest={'source':str(args.input),'original_rows':len(source), 'seed':args.seed,
              'note':'Bootstrap sampling with replacement for sizes exceeding source rows; not new customers or independent events.',
              'datasets':[]}
    for n in args.sizes:
        if n<=0:raise ValueError('sizes must be positive')
        sampled=source.sample(n=n,replace=n>len(source),random_state=args.seed)
        target=out/f'banksim_{n}.csv';sampled.to_csv(target,index=False)
        manifest['datasets'].append({'rows':n,'path':str(target),'resampled':n>len(source)})
        print(target, len(sampled))
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
