---
name: a06-model-builder-2
description: Detailed procedure to implement, verify and document model slot 2 (per Agent 3 spec) as a fast, deterministic, mass-conserving Python module compatible with the shared optimizer and evaluator.
---
# Skill: Build model slot 2 (Agent a06)

## Purpose
Turn the specification of **slot 2** (`config/models.yaml` → `models[slot=2]`, and the Model 2 section of
`reports/03_models.qmd`) into correct, fast, tested code. You do NOT calibrate — that's `a12-optimizer-2`.
You may use default/literature parameters only for smoke tests.

## Inputs
`config/models.yaml` slot 2, `reports/03_models.qmd` (Model 2), `a03.json` downstream_notes for a06,
`src/common/model_api.py`, `src/common/data.py`, `a02.json` (units, PET nature).

## Step 1 — Read & restate the spec
Write at the top of the module a docstring with: model name, reference(s), states, fluxes, parameters with bounds,
equations (plain text), time-stepping scheme, known deviations from the reference. If the spec is ambiguous, pick
the reference implementation's behavior, document it, and log in `context/DECISIONS.md`.

## Step 2 — Implement `src/models/model_2.py`
- Class `Model2(BaseModel)` with `model_id` = slot id, `kind` = "conceptual" or "trainable".
- `param_specs()` returns `ParamSpec` list EXACTLY matching models.yaml (names, bounds, defaults, log_scale).
- **Conceptual models:** core loop as a `@numba.njit` function over NumPy arrays (P, PET, params, states) →
  (Q, states_timeseries, fluxes dict as arrays). `simulate()` wraps it and returns `pd.Series` named "Q_sim" with
  the forcing index. Keep a pure-Python fallback when Numba unavailable. Clip stores to [0, capacity]; guard
  divisions; no NaN allowed.
- **Trainable models (regression / ML):** `fit(forcing, target, params)` uses ONLY data passed in (the optimizer passes
  calibration data); store scalers fitted on the data passed to `fit`; `simulate()` produces Q for any forcing;
  implement `save/load` (joblib or torch state_dict + scaler JSON). Torch device via `src.common.data.torch_device()`
  (mps on Apple Silicon); MPS is not bit-deterministic → determinism tests run on cpu. For sequence models, the first `seq_len` days
  of any run are produced using padding/warm-up context only — document; ensure outputs are ≥ 0 (softplus/ReLU or clip).
  Use torch deterministic flags and seed from config.
- Optional `simulate(..., return_states=True)` to expose internal fluxes (used by a16 diagnostics).

## Step 3 — Verification tests `tests/test_model_2.py` (all must pass)
1. **Interface:** instantiation, param_specs matches models.yaml, simulate returns same-length non-negative finite Series.
2. **Determinism:** two runs with same params/seed are identical.
3. **Mass balance (conceptual):** over a synthetic 3-yr forcing, ΣP − ΣAET − ΣQ − ΔStorage − (routing store change) ≈ 0 (|err| < 1e-6·ΣP).
4. **Limit cases:** P=0 → Q recedes monotonically to ~0 (after routing); PET=0 → no ET; extreme P (500 mm/d) → no NaN/overflow.
5. **Bounds sweep:** 200 Latin-hypercube parameter sets within bounds all run without error/NaN.
6. **Oracle comparison (when available):** compare with reference implementation (e.g., airGR outputs via published
   test data, `hydrobricks`, `RRMPG`, `hydromodpy`, spotpy's HYMOD example; for SAC-SMA, Aldo's own Numba implementation if
   `external_references.sacsma_numba_path` is set in config/project.yaml) — max abs diff < 1e-6 mm/d, or document why not.
7. **Leakage guard (trainable):** assert `fit` never receives rows < 1360 (end of evaluation run window) in the pipeline helper.
8. **Speed:** report runtime for full 40-yr run (target conceptual < 5 ms after JIT); optimizers need ~10⁴–10⁵ runs.

## Step 4 — Smoke run (calibration period only)
Using default parameters on `slice_run(df, "calibration")`, compute KGE/NSE on the calibration metric mask
(NOT evaluation). Plot one wet and one dry water year obs vs sim → `results/build/model_2_smoke.png`. These numbers
are sanity checks only, not results.

## Step 5 — Document
Append a "Implementation notes" subsection to the handoff (not to a03's report): numerical scheme, deviations,
performance, how to call:
```python
from src.models.model_2 import Model2
m = Model2(); q = m.simulate(forcing_df, m.defaults())
```
Update `config/models.yaml` slot 2 `status: built` (only that field of your slot).

## Handoff `a06.json` key_numbers
`n_params`, `runtime_ms_full_record`, `mass_balance_max_abs_err`, `smoke_KGE_cal_default`, `smoke_NSE_cal_default`,
`tests_passed`. downstream_notes for `a12-optimizer-2`: sensitive parameters, suspected correlations,
recommended transforms, any parameter that should be fixed.

## Handoff checklist (do not skip)
- [ ] Outputs listed above exist and are non-empty
- [ ] `context/handoffs/a06.json` written (schema `context/handoffs/_TEMPLATE.json`), incl. `downstream_notes`
- [ ] Section appended to `context/CONTEXT.md`; decisions appended to `context/DECISIONS.md`
- [ ] `python scripts/state.py set a06-model-builder-2 done`
- [ ] `scripts/backup.sh a06-model-builder-2 "<message>"` → tag stored in handoff `backup_tag`
