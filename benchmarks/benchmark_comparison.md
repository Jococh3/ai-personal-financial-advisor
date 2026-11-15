# E516 Benchmark Comparison

All times are observed, not estimated. Dataset loading and Spark cache warmup excluded.

| Rows | Pandas mean (s) | Spark configuration | Spark mean (s) | Pandas / Spark |
|---:|---:|---|---:|---:|
| 10,000 | 0.02259 | Not yet measured | — | — |
| 100,000 | 0.03258 | Not yet measured | — | — |
| 1,000,000 | 0.16883 | Not yet measured | — | — |

**Interpretation:** Times include execution and result materialization, but not input loading. Only compare hardware-equivalent and execution-equivalent runs when making speedup claims. Running Pandas on a laptop and Spark on Jetstream2 is an environment comparison, not pure parallel speedup.
