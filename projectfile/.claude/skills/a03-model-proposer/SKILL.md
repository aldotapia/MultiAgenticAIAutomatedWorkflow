---
name: a03-model-proposer
description: Procedure to select and fully specify 5 rainfall-runoff models spanning complexity levels, with equations, state/flux definitions, parameters and bounds, so builders can implement them unambiguously.
---
# Skill: Model proposal (Agent 3)

## Purpose
Choose **5 models** that together (a) maximize the chance of the best possible streamflow reproduction,
(b) span complexity so results are interpretable (does complexity pay off?), and (c) are implementable in
Python (existing package or from scratch). Your spec must be precise enough that a builder can code it without
reading any other document.

## Inputs
`reports/01_watershed.qmd` + `a01.json` (processes, priors), `reports/02_data.qmd` + `a02.json` (signatures,
memory length, PET nature), `context/CONTEXT.md`.

## Selection criteria (score each candidate 1–5, show table)
Process adequacy for a humid, soil-storage/baseflow-dominated Coastal Plain basin · data demands (only P, PET) ·
parameter count vs 36 yr of calibration data · literature performance on Leaf River · implementation risk ·
complementarity with other picks · compute cost for global optimization (~10⁴–10⁵ runs).

## Candidate pool (evaluate at least these, add others you find)
- Benchmarks: climatological/seasonal mean, persistence-free linear regression / ARX on lagged P & PET
  (no lagged observed Q → fair comparison), unit hydrograph + loss (IHACRES-like).
- Conceptual lumped: GR4J (4 par), HYMOD (5 par; Leaf River classic), HBV-light without snow (~9–11 par),
  SAC-SMA (~16 par; NWS standard, Leaf River classic), Xinanjiang, TOPMODEL (needs topographic index — check
  a01 availability), abc, FUSE/MARRMoT-style structures.
- Data-driven: LSTM (Kratzert et al. 2018/2019; note single-basin data is small — consider regularization),
  GRU/TCN, gradient boosting with engineered antecedent features (API, rolling sums).
- Hybrid: conceptual model + LSTM post-processor on residuals, or differentiable conceptual model (dPL-style).
- Ensembles: multi-model weighted average (weights fitted on internal validation only). **Hybrids and ensembles
  are explicitly allowed** — as one of the 5 slots, and a16 additionally evaluates pre-declared ensembles of the 5.
- Compute constraint: everything runs on ONE laptop (likely Apple Silicon, torch `mps`/`cpu`). Prefer models whose
  calibration fits in ≤3 h wall time; LSTM hidden size ≤128.

## Recommended default set (override with justification if evidence says otherwise)
1. **Linear ARX / multiple linear regression** with antecedent precipitation indices (baseline, closed form)
2. **GR4J** (parsimonious, strong benchmark)
3. **HYMOD** (Leaf River historical reference)
4. **SAC-SMA** (process-rich, NWS operational)
5. **LSTM** (single-basin, P/PET/DOY features, calibration-only normalization) — or hybrid GR4J+LSTM if a02 shows
   limited data sufficiency.

## Required content per model (in report AND models.yaml)
1. Overview: origin, key references, where used, why chosen for Leaf River.
2. Conceptual diagram (Mermaid `flowchart` block or SVG figure) of stores and fluxes.
3. Perceptual model → conceptual assumptions (what is represented, what is ignored).
4. **Full mathematical formulation**: state variables with units; flux equations; state update (continuous ODE and
   the discrete daily scheme actually used — explicit Euler vs analytical/operator splitting; state order of
   operations within a time step); routing (unit hydrograph ordinates, Nash cascade); output equation.
   LaTeX with numbered equations. For LSTM: gate equations, input features, sequence length, head, loss, normalization.
   For regression: design matrix definition, estimator (OLS/ridge), feature definitions (e.g., API_k = Σ λ^i P_{t-i}).
5. Parameter table: symbol, name, units, lower, upper, default, physical meaning, literature source for bounds.
6. Initial states and warm-up requirement.
7. Mass balance check equation (for conceptual models) the builder must test.
8. Numerical pitfalls (negative stores, division by zero, tiny PET, UH ordinates normalization).
9. Implementation route: package (name, version, license, API call) or from-scratch pseudocode. Prefer from-scratch
   NumPy/Numba for conceptual models (full control, speed, no hidden defaults); cite the reference implementation
   you follow (e.g., Perrin et al. 2003 for GR4J; airGR as test oracle).
10. Expected strengths/weaknesses on this basin and expected performance range.

## config/models.yaml
Fill all 5 slots with the schema already in the file; `status: proposed`; module paths `src/models/model_N.py`.
Set `kind` concept via `family`. Make parameter bounds consistent with the report.

## Report `reports/03_models.qmd`
Sections: Summary table (slot, model, family, #params, source, rationale) · Selection method & scoring table ·
Model 1…5 (items 1–10 each) · Cross-model comparison (processes represented matrix) · Hypotheses to test in a16
(e.g., "SAC-SMA > GR4J only on low flows") · References.

## Handoff notes
downstream_notes for each builder (a05..a09): implementation gotchas; for a10: parameter counts, smoothness
(thresholds → non-smooth → derivative-free global search), whether gradient methods apply (LSTM).

## Handoff checklist (do not skip)
- [ ] Outputs listed above exist and are non-empty
- [ ] `context/handoffs/a03.json` written (schema `context/handoffs/_TEMPLATE.json`), incl. `downstream_notes`
- [ ] Section appended to `context/CONTEXT.md`; decisions appended to `context/DECISIONS.md`
- [ ] `python scripts/state.py set a03-model-proposer done`
- [ ] `scripts/backup.sh a03-model-proposer "<message>"` → tag stored in handoff `backup_tag`
