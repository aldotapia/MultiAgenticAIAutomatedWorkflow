---
name: a04-metrics-advisor
description: Procedure to catalogue goodness-of-fit metrics and signatures for daily streamflow, test their behavior on Leaf River data, and recommend a calibration objective aligned with the KGE/NSE evaluation.
---
# Skill: Performance metrics (Agent 4)

## Purpose
Decide what calibration objective will produce the best KGE/NSE in evaluation while still yielding
hydrologically sound simulations, and provide a complete, tested metric library for a11–a16.

## Inputs
`a02.json` + report (flow skewness, FDC, zero flows, BFI), `config/project.yaml` (KGE/NSE definitions),
`src/common/metrics.py` (canonical — DO NOT modify).

## Step 1 — Catalogue (each with: formula in LaTeX, range, optimum, units, sensitivity (high/low flow),
## strengths, weaknesses, reference)
- **Squared-error family:** MSE, RMSE, NSE, log-NSE, sqrt-NSE, inverse-Q NSE, weighted NSE, NNSE (normalized), R².
- **KGE family:** KGE (2009), KGE' (Kling 2012, CV ratio), KGE'' (Tang 2021), non-parametric KGE (Pool 2018),
  KGE on transformed flows, KGE components r, α, β separately; split KGE.
- **Absolute/bias:** MAE, PBIAS, volume error, mean absolute relative error.
- **Correlation/agreement:** Pearson r, Spearman ρ, Willmott d, d1, refined index of agreement.
- **Likelihood-based:** Gaussian, heteroscedastic (Box-Cox/log-sinh transformed), AR(1) residual likelihood,
  generalized likelihood (Schoups & Vrugt 2010) — relevant if a10 recommends DREAM.
- **Event/peak:** peak error, peak timing error, high-flow bias (FHV, top 2%), low-flow bias (FLV, bottom 30% log), FMS (mid-segment FDC slope) — Yilmaz et al. (2008).
- **Signature-based:** BFI error, recession constant error, runoff ratio error, autocorrelation error, FDC-based distances.
- **Information/probabilistic:** mutual information, CRPS (if ensembles), Wasserstein distance of FDCs.
- **Multi-objective:** Pareto combos (e.g., KGE + logKGE), weighted sums, DE metric (Schwemmle 2021).

## Step 2 — Empirical behavior test on THIS data (calibration period only)
Using observed Q (calibration period) build synthetic simulations: scaled (×0.8, ×1.2), shifted by +1 day, smoothed
(7-d moving average), baseflow-only (Lyne–Hollick), seasonal climatology, and noise-added. Compute every metric;
show heatmap. This shows which metrics punish bias, timing, variability, and peaks — **justify recommendation with it**.
Also compute climatology/mean-flow benchmark NSE/KGE → note that KGE = −0.41 for mean flow (Knoben et al. 2019).

## Step 3 — Recommendation
Decision criteria: alignment with evaluation (KGE and NSE); robustness to skewed flows; balance high/low flows;
compatibility with optimizers (a10) and ML losses (differentiable variant for LSTM, e.g., NSE* batch loss of
Kratzert 2019 or 1−KGE). Expected default recommendation: **calibrate on KGE (2009)** — it is the selection
metric and decomposes bias/variability/correlation; optionally a composite `0.5·KGE(Q) + 0.5·KGE(√Q)` if Step 2
shows poor low-flow sensitivity. Report NSE for all. The final report (a16) shows ONLY KGE and NSE; everything else is development diagnostics. Provide one objective for conceptual models and one loss
for trainable models; state they must be **maximized** (or 1−value minimized).

## Step 4 — Code `src/common/metrics_extra.py`
Pure NumPy functions `f(sim, obs, **kw) -> float`, NaN-safe (reuse `_clean`), a registry
`METRICS = {"KGE": ..., "NSE": ..., ...}`, and `objective(sim, obs)` implementing the recommendation (imports KGE/NSE
from `metrics.py`). Tests `tests/test_metrics_extra.py`: perfect sim = optimum; known analytic cases; compare
with `hydroeval` where available (tolerance 1e-10).

## Step 5 — config/metrics.yaml
Fill `recommended_objective`, `transform_for_objective`, `secondary_diagnostics`, plus `trainable_loss`.

## Report `reports/04_metrics.qmd`
Summary & recommendation box · Catalogue (grouped tables + formulas) · Empirical sensitivity experiment (heatmap)
· Benchmarks (mean-flow, climatology) · Recommendation & rationale · How a16 must report · References.

## Handoff checklist (do not skip)
- [ ] Outputs listed above exist and are non-empty
- [ ] `context/handoffs/a04.json` written (schema `context/handoffs/_TEMPLATE.json`), incl. `downstream_notes`
- [ ] Section appended to `context/CONTEXT.md`; decisions appended to `context/DECISIONS.md`
- [ ] `python scripts/state.py set a04-metrics-advisor done`
- [ ] `scripts/backup.sh a04-metrics-advisor "<message>"` → tag stored in handoff `backup_tag`
