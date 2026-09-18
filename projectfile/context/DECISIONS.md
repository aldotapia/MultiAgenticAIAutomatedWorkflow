# Decision log (append-only)
| date | agent | decision | alternatives considered | rationale |
|------|-------|----------|-------------------------|-----------|
| scaffold | orchestrator | Calibration period = 1951-10-01..1988-09-30 (warm-up to 1952-09-30) | pre-eval period (does not exist) | Eval period is at record start |
| scaffold | orchestrator | Internal validation split 1981-10..1988-09 inside calibration | k-fold by water year | Enables early stopping & pre-eval ranking without leakage |
| scaffold | orchestrator | Primary selection metric KGE; NSE also reported | NSE only | User requires both; KGE decomposes bias/variability/timing |
| user | orchestrator | Evaluation window = rows 265:1360 (metric 357:1360); calibration rows 1360:14610 | date-based Oct 1948–Sep 1951 (kept as `definition: dates`) | User instruction; conflicts with PET seasonality → ISSUE-001 |
| user | orchestrator | Final report metrics KGE & NSE only | extra diagnostics in report | User instruction |
| user | orchestrator | Hybrids & ensembles allowed; ensemble weights frozen on internal validation before eval | single models only | User instruction; avoids eval leakage |
| user | orchestrator | Laptop-only compute, conda env `leafriver`, core sharing via LR_N_JOBS, ≤3 h per optimizer | HPC/SLURM | User instruction |
