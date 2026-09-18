---
name: a10-optimization-advisor
description: Procedure to review parameter estimation algorithms for hydrological models, benchmark candidates on a cheap test model, and prescribe algorithm, settings, budget, and a common optimization runner for each of the 5 models.
---
# Skill: Optimization algorithms (Agent 10)

## Purpose
Give each optimizer agent (a11–a15) a concrete, justified recipe (algorithm, library, hyperparameters, budget,
convergence criteria, restarts) and a shared runner so results are comparable.

## Inputs
`config/models.yaml` (param counts, bounds, families), `a03.json`, `config/metrics.yaml` (objective), `a02.json`.

## Step 1 — Catalogue (for each: principle, pseudocode, key hyperparameters, pros/cons for non-smooth,
## multimodal, threshold-laden hydrological response surfaces, Python implementations with versions, references)
- **Local:** Nelder–Mead, Powell, L-BFGS-B (finite differences), Rosenbrock, Gauss–Marquardt–Levenberg (PEST-like).
- **Global evolutionary / population:** SCE-UA (Duan 1992 — developed ON Leaf River), Differential Evolution
  (scipy), CMA-ES (`cma`), PSO (`pyswarms`), Genetic Algorithm, DDS (Tolson & Shoemaker 2007), dual annealing /
  simulated annealing, basin-hopping.
- **Surrogate / Bayesian:** Bayesian optimization (GP, TPE via optuna), RBF surrogate (DYCORS).
- **Uncertainty-aware / sampling:** GLUE, DREAM(ZS), SCEM-UA, MCMC (emcee), ROPE, Sobol-based screening.
- **Multi-objective:** NSGA-II/III (pymoo), MOSCEM, ParaPIn/Borg.
- **Gradient-based (trainable models):** Adam/AdamW + LR schedules, early stopping; hyperparameter search with
  optuna TPE + median pruner; for regression: closed-form OLS/ridge with CV on λ.

## Compute constraint
Single laptop, no HPC. Use `src.common.data.n_jobs()` for parallel objective evaluations (multiprocessing /
joblib), Numba for conceptual models, torch device from `torch_device()` (mps/cpu). Budgets must keep each
optimizer ≤ `compute.max_wall_time_per_optimizer_hours`, assuming 5 optimizers share the cores.

## Step 2 — Mini-benchmark (evidence for recommendation)
Implement a quick HYMOD or GR4J (Numba) — or use builder output if already available — on the calibration
**internal train** period; run SCE-UA, DE, CMA-ES, DDS, PSO, dual annealing with equal budgets (e.g., 2k, 5k,
10k evals) × 5 seeds. Plot best-objective vs evaluations (median + IQR), final parameter spread (equifinality),
runtime. Validation-period KGE of each best set. Keep this ≤ ~30 min compute.

## Step 3 — Recommendation per model (write into config/optimization.yaml `per_model`)
Defaults to confirm/override with Step 2 evidence:
- Linear regression/ARX: closed-form ridge; λ and API decay constants via optuna TPE (200 trials) or grid,
  selected on internal validation.
- GR4J / HYMOD (≤5 params): SCE-UA (spotpy), ngs = 2n+1 complexes, 10–20k evals, 5 seeds.
- SAC-SMA (~16 params): SCE-UA or DDS with 30–50k evals, 5 seeds; optional DREAM afterwards for posterior.
- LSTM: AdamW, lr 1e-3 with ReduceLROnPlateau, batch 256, early stopping patience 20 on internal validation;
  optuna (~30 trials, MedianPruner, ≤40 epochs/trial) over hidden size {32,64,128}, seq length {90,180,365}, dropout {0,0.2,0.4}, lr; 5 seeds of
  final config, ensemble mean optional (must be declared).
For every model specify: objective (from a04, maximize), parameter transform (log for scale params), budget,
convergence criteria (e.g., SCE-UA: pcento 0.1% over 10 loops), seeds, what to save.

## Step 4 — Shared runner `src/optimization/runner.py`
Function `calibrate(model: BaseModel, algorithm: str, settings: dict, seed: int) -> dict` that:
loads data via `src/common/data.py` (calibration run slice), evaluates objective on `internal_mask(frame, "train")`, logs every
evaluation to `results/calibration/<model_id>/trace_seed<seed>.csv` (params, objective, time), returns best params,
and computes internal-validation and full-calibration KGE/NSE for the best set. Pure CLI:
`python -m src.optimization.runner --slot N --seed 42`. Never touches evaluation period. Add `tests/test_runner.py`
with a 2-parameter toy model.

## Report `reports/10_optimization.qmd`
Summary + recommendation table (model × algorithm × budget) · Catalogue · Benchmark design & results · Rationale ·
Final protocol for a11–a15 (step list, incl. final refit on full calibration period for conceptual models:
optimize on internal-train, check validation, then re-run final calibration on full 1952-10..1988-09 with best
settings — state clearly which parameter set goes to a16) · References.

## Handoff checklist (do not skip)
- [ ] Outputs listed above exist and are non-empty
- [ ] `context/handoffs/a10.json` written (schema `context/handoffs/_TEMPLATE.json`), incl. `downstream_notes`
- [ ] Section appended to `context/CONTEXT.md`; decisions appended to `context/DECISIONS.md`
- [ ] `python scripts/state.py set a10-optimization-advisor done`
- [ ] `scripts/backup.sh a10-optimization-advisor "<message>"` → tag stored in handoff `backup_tag`
