# E516 Benchmark Comparison

All times are observed, not estimated. Dataset loading and Spark cache warmup excluded.

| Rows | Pandas mean (s) | Spark configuration | Spark mean (s) | Pandas / Spark |
|---:|---:|---|---:|---:|
| 10,000 | 0.01520 | 1-worker-10k | 1.37816 | 0.01x |
| 10,000 | 0.01520 | 2-workers-10k | 1.33351 | 0.01x |
| 100,000 | 0.04160 | 1-worker-100k | 1.63450 | 0.03x |
| 100,000 | 0.04160 | 2-workers-100k | 1.54681 | 0.03x |
| 1,000,000 | 0.23449 | 1-worker-1m | 2.56072 | 0.09x |
| 1,000,000 | 0.23449 | 2-workers-1m | 2.25436 | 0.10x |

**Interpretation:** Times include execution and result materialization, but not input loading. Only compare hardware-equivalent and execution-equivalent runs when making speedup claims. Pandas ran on the Jetstream2 master VM, while Spark ran on one or two Jetstream2 worker VMs. The workloads exclude input loading, but their execution and result-materialization boundaries are not perfectly identical. These measurements compare observed application performance, not pure parallel speedup.
