---
name: a16-evaluator
description: Detailed protocol to evaluate the 5 calibrated models on the held-out Leaf River evaluation window, compute KGE and NSE correctly with warm-up exclusion, quantify uncertainty, diagnose errors, and select the best model with a transparent rule.
---
# Skill: Evaluation & selection (Agent 16)

## Purpose
Unbiased, reproducible comparison of all 5 calibrated models on the held-out window, and a defensible final choice.
You are the ONLY agent allowed to access evaluation observations: `export LR_AGENT=a16`.

## Protocol (fixed — do not alter)
- Run every model over the evaluation run window — **rows 265:1360** (user definition of Oct 1 1948–Sep 30 1951) —
  with FINAL parameters from `results/calibration/model_N/best_params.json`. Initial states: model defaults (same for all).
- Warm-up rows 265:357 (first 3 months) discarded. Metrics ONLY on **rows 357:1360** (1,003 days).
- Always use `slice_run`/`metric_mask`; they honor `periods.definition` in config.
- Metrics: **KGE** (Gupta 2009) and **NSE** from `src/common/metrics.py` (never re-implement).
- No re-calibration, no parameter tweaks, no model changes after seeing evaluation results. If a model fails to run,
  report failure, do not fix silently (you may log an ISSUE and re-evaluate only a builder-fixed version, documented).

```python
import os; os.environ["LR_AGENT"] = "a16"
from src.common.data import load_data, slice_run, metric_mask
from src.common.metrics import kge_components, nse
df = load_data(); ev = slice_run(df, "evaluation", allow_evaluation=True)
m = metric_mask(ev, "evaluation")
assert m.sum() == 1003 and len(ev) == 1095
```

## Step 1 — Preconditions
All a11–a15 statuses `done` (or explicitly `blocked` → evaluate the rest and report). Load each best_params.json,
verify reproducibility on full calibration period (metrics must equal those saved by the optimizer ± 1e-9).

## Step 2 — Simulate & compute
For each model: simulate, store in `results/evaluation/simulations.parquet` (columns: date, Q_obs, model_1..5).
Compute on metric window: **KGE and NSE** (final metrics). Internally you may compute anything (r, α, β, FDC
errors, …) to guide the discussion, but report tables show ONLY KGE and NSE. Also compute KGE/NSE per
year-block of the metric window (rows 357:722, 722:1087, 1087:1360) to show stability.

### Ensembles & hybrids (allowed)
BEFORE any evaluation simulation, build from the `cal_simulation.parquet` files: (a) equal-weight mean of all models,
(b) weights fitted on internal validation rows (non-negative, sum to 1, maximize KGE). Freeze them in
`results/evaluation/ensemble_weights.json` and run `scripts/backup.sh a16-evaluator "frozen ensemble weights"`.
Evaluate them as extra candidates.
Benchmarks for context: mean-calibration-flow model and day-of-year climatology from calibration period
(KGE of mean-flow benchmark ≈ −0.41).

## Step 3 — Uncertainty of the metrics
Block bootstrap (block = 30 days, 2,000 resamples, seed 42) on the metric window → 95% CI for KGE and NSE per model;
paired bootstrap of differences between the top model and each other model (probability top > other).
If ML models have multiple seeds, report seed spread too.

## Step 4 — Selection rule (declare before looking at numbers; write it in the report as-is)
1. Primary: highest **KGE** on the evaluation window.
2. If the top-2 KGE difference < 0.02 AND paired-bootstrap P(top > second) < 0.8 → tie-break by highest **NSE**;
   if still tied, prefer fewer parameters (parsimony).
3. Disqualify a model if it produced NaN/negative flows — report it anyway.

## Step 5 — Diagnostics & figures (results/evaluation/figures)
Hydrographs obs vs all models (full window + zooms on largest 3 events, log-scale version), scatter obs–sim
(1:1 line), FDC comparison (log y), residual time series, cumulative flow curves, calibration-vs-evaluation
KGE/NSE degradation plot. Figures are qualitative; no metrics other than KGE/NSE printed. Discuss eval being wetter than calibration (see CONTEXT.md) and which models extrapolate better.

## Step 6 — Report `reports/16_evaluation.qmd`
1 Executive summary: winner, KGE and NSE (with 95% CI), one-paragraph justification.
2 Protocol (periods, warm-up, formulas, selection rule).
3 **Main results table** — model | #params | KGE | KGE 95%CI | NSE | NSE 95%CI | cal KGE | cal NSE.
4 Per-year-block KGE/NSE table. 5 Diagnostics figures. 6 Discussion: complexity vs performance, high/low flow behavior,
failure modes, hypotheses from a03 confirmed/rejected, comparison with literature values from a01.
7 Recommendations (what to try next). 8 Reproducibility (commands, versions, git tag). References.

Save `results/evaluation/metrics.csv` (tidy) and `results/evaluation/selection.json`
{best_model_id, slot, KGE, NSE, rule_applied, runner_up}.

## Handoff `a16.json` key_numbers
`best_model_id`, `best_KGE_eval`, `best_NSE_eval`, `all_models: {id: {KGE, NSE}}` (incl. ensembles), `metric_days` (1003).

## Handoff checklist (do not skip)
- [ ] Outputs listed above exist and are non-empty
- [ ] `context/handoffs/a16.json` written (schema `context/handoffs/_TEMPLATE.json`), incl. `downstream_notes`
- [ ] Section appended to `context/CONTEXT.md`; decisions appended to `context/DECISIONS.md`
- [ ] `python scripts/state.py set a16-evaluator done`
- [ ] `scripts/backup.sh a16-evaluator "<message>"` → tag stored in handoff `backup_tag`
