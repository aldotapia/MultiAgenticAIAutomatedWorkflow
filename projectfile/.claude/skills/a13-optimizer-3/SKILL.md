---
name: a13-optimizer-3
description: Detailed procedure for robust, leakage-free parameter optimization of model slot 3: multi-seed global search, convergence and identifiability diagnostics, internal validation, and final parameter selection for evaluation.
---
# Skill: Calibrate model slot 3 (Agent a13)

## Purpose
Produce the single best, well-justified parameter set (or trained weights) for model slot 3, ready for a16,
using ONLY the calibration period. Robustness > squeezing 0.001 of objective.

## Inputs
`src/models/model_3.py` + `a07.json` (builder notes), `config/optimization.yaml` per_model entry for this
model + `reports/10_optimization.qmd`, `config/metrics.yaml` objective, `src/optimization/runner.py`,
`src/common/metrics_extra.py`.

## Step 0 — Preconditions
`python -m pytest -q tests/test_model_3.py tests/test_runner.py` must pass; otherwise write to
`context/ISSUES.md`, set state `blocked`, stop.

## Step 1 — Setup
- Data: `slice_run(df, "calibration")` (rows 1360:14610); objective on `internal_mask(frame, "train")` (rows 1725:12053);
  warm-up rows 1360:1725 simulated but excluded from the metric.
- Compute: laptop only. Use at most `n_jobs()` cores (set by run_pipeline.sh); respect the wall-time cap in config.
- Objective: `metrics_extra.objective` (maximize). Apply parameter transforms from a10 (log for scale params).
- Output dir `results/calibration/model_3/`. Record library versions & hardware.

## Step 2 — Sensitivity screening (conceptual models; skip for closed-form regression)
Morris elementary effects or Sobol (SALib, ~500–2000 runs) on internal-train objective. Plot μ*/σ. If a parameter is
insensitive, you MAY fix it at default only if a10's protocol allows; log in DECISIONS.md.

## Step 3 — Optimization runs
Run the prescribed algorithm for every seed in `config/optimization.yaml` (default 5), with the prescribed budget.
- Conceptual: `python -m src.optimization.runner --slot 3 --seed <s>`; save traces.
- Trainable (regression/ML): hyperparameter search (optuna study stored in `study.db`), selection on internal
  validation; then train final config with each seed. Scalers fitted on training data only. Early stopping on
  internal validation (rows 12053:14610).
If a run hits the budget without meeting convergence criteria, extend once by 50% and note it.

## Step 4 — Diagnostics (figures in the output dir)
1. Convergence: best objective vs evaluations per seed (conceptual) or train/val loss curves (trainable).
2. Final objective spread across seeds (table); if range > 0.02 KGE → poor convergence: flag & investigate.
3. Parameter identifiability: normalized best parameters per seed (parallel coordinates), dotty plots from the
   trace (objective vs each parameter), correlation matrix of top-5% sets.
4. Parameters at/near bounds (within 1% of range) → flag; consider whether a03 bounds are too narrow (ISSUE, don't
   silently change bounds unless a10 protocol permits).
5. Hydrograph obs vs sim for internal validation; FDC comparison (log); residual vs Q plot; ACF of residuals.
6. Water balance: simulated vs observed runoff ratio on calibration.

## Step 5 — Select the final parameter set
- Save the final-parameter simulation over the whole calibration run window to
  `results/calibration/model_3/cal_simulation.parquet` (row, date, Q_obs, Q_sim) — a16 fits ensemble weights on it.
- Choose seed with best internal-train objective whose internal-validation KGE is within 0.02 of the best validation
  KGE (guards overfitting). Document.
- Per a10 protocol, optionally re-run final calibration on the **full calibration window** (rows 1725:14610)
  starting from the chosen solution (conceptual) or retrain on train+val for the early-stopping epoch count
  (trainable). State unambiguously which set is FINAL.
- Save `best_params.json`: {model_id, slot, params, objective_name, seed, algorithm, n_evals, library_versions,
  metrics: {internal_train: {KGE, NSE, r, alpha, beta}, internal_validation: {...}, full_calibration: {...}}}
  and, for trainable models, weights/scaler paths.
- Verify reproducibility: reload params → simulate → metrics identical to saved.

## Step 6 — summary.md
≤1 page: algorithm & budget, convergence verdict, identifiability issues, final params table, calibration metrics,
risks for evaluation (e.g., underestimates high flows → eval period is wetter). **Never** compute metrics on
evaluation rows 265:1360.

## Update
`config/models.yaml` slot 3 `status: calibrated`.

## Handoff `a13.json` key_numbers
`objective_internal_train`, `KGE_internal_val`, `NSE_internal_val`, `KGE_full_cal`, `NSE_full_cal`,
`seed_spread_objective`, `n_evals_total`, `params_at_bounds` (list), `wall_time_min`.
downstream_notes for a16: path to final params, how to run the model for evaluation, known weaknesses.

## Handoff checklist (do not skip)
- [ ] Outputs listed above exist and are non-empty
- [ ] `context/handoffs/a13.json` written (schema `context/handoffs/_TEMPLATE.json`), incl. `downstream_notes`
- [ ] Section appended to `context/CONTEXT.md`; decisions appended to `context/DECISIONS.md`
- [ ] `python scripts/state.py set a13-optimizer-3 done`
- [ ] `scripts/backup.sh a13-optimizer-3 "<message>"` → tag stored in handoff `backup_tag`
