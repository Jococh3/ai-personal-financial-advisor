"""Compare real observed timings; refuse to invent missing Spark results."""
import argparse
import json
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pandas',required=True)
    p.add_argument('--spark',nargs='+',default=[])
    p.add_argument('--output',required=True)
    args=p.parse_args()
    base=json.loads(Path(args.pandas).read_text())
    by_size={r['rows']:r for r in base['results']}
    lines=['# E516 Benchmark Comparison','',
           'All times are observed, not estimated. Dataset loading and Spark cache warmup excluded.', '',
           '| Rows | Pandas mean (s) | Spark configuration | Spark mean (s) | Pandas / Spark |',
           '|---:|---:|---|---:|---:|']
    if not args.spark:
        for count,pd in by_size.items():
            lines.append(f"| {count:,} | {pd['mean_seconds']:.5f} | Not yet measured | — | — |")
    for file in args.spark:
        s=json.loads(Path(file).read_text());label=s.get('label','Spark')
        for r in s['results']:
            pd=by_size.get(r['rows'])
            if pd is None:continue
            speedup=pd['mean_seconds']/r['mean_seconds'] if r['mean_seconds'] else float('nan')
            lines.append(f"| {r['rows']:,} | {pd['mean_seconds']:.5f} | {label} | {r['mean_seconds']:.5f} | {speedup:.2f}x |")
    lines.extend(['','**Interpretation:** Times include execution and result materialization, but not input loading. '
                  'Only compare hardware-equivalent and execution-equivalent runs when making speedup claims. '
                  'Running Pandas on a laptop and Spark on Jetstream2 is an environment comparison, not pure parallel speedup.'])
    Path(args.output).write_text('\n'.join(lines)+'\n')
    print(args.output)

if __name__=='__main__':main()
