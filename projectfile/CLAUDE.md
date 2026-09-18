# CLAUDE.md — Orchestrator & shared rules (read by EVERY agent)

## Mission
Find the model that best reproduces daily streamflow of the Leaf River (Mississippi, USA) using
`data/raw/LeafRiverDaily.txt` (P, PET, Q; 1948-10-01..1988-09-30). Final ranking by KGE and NSE on the
evaluation window defined in `config/project.yaml`.

## Periods (authoritative: config/project.yaml → periods.definition = index)
0-based, half-open row indices of `data/raw/LeafRiverDaily.txt`:
| Use | Run rows | Warm-up rows | Metric rows | n metric days |
|---|---|---|---|---|
| Evaluation (Agent 16 only; user def. "Oct 1 1948–Sep 30 1951") | 265:1360 | 265:357 | 357:1360 | 1003 |
| Calibration | 1360:14610 | 1360:1725 | 1725:14610 | 12885 |
| ↳ internal train | | | 1725:12053 | |
| ↳ internal validation | | | 12053:14610 | |
| Unused (adjacent to eval, EDA only) | 0:265 | | | |

⚠ Open issue: with start date 1948-10-01 (supported by PET seasonality), rows 265:1360 carry date labels
1949-06-23..1952-06-21. Agent 2 audits this; the user decides. Always slice with `src/common/data.py` so a switch
of `periods.definition` propagates automatically.

## Agents & phases (see orchestration.yaml)
P1: a01 watershed, a02 data → P2: a03 models, a04 metrics → P3: a10 optimizers →
P4: a05–a09 build models (slots 1–5) → P5: a11–a15 calibrate (slots 1–5) → P6: a16 evaluate (5 models + pre-declared ensembles).

## Hard rules
1. **Start-up ritual:** read `CLAUDE.md`, `config/project.yaml`, `context/CONTEXT.md`, `context/DECISIONS.md`,
   `context/ISSUES.md`, and the handoff JSONs of your dependencies. Then read your skill in `.claude/skills/<agent>/SKILL.md`.
2. **Data** only through `src/common/data.py`. **KGE/NSE** only through `src/common/metrics.py`.
3. **No evaluation leakage.** Only a16 sets `LR_AGENT=a16`. Anyone else touching evaluation rows 265:1360 for
   fitting, scaling, feature selection or model choice invalidates the study.
   Final report metrics: **KGE and NSE only**. Any diagnostic is fine during development.
4. **Model contract:** every model subclasses `src/common/model_api.BaseModel`; units mm/day; deterministic given params+seed.
5. **Stay in your lane:** write only your declared outputs (orchestration.yaml). Problems with others' outputs → `context/ISSUES.md`.
6. **Quarto:** reports in `reports/NN_name.qmd`, `jupyter: leafriver`, executable code, figures saved under `results/figures/`,
   cite with `reports/references.bib` (append entries, never delete). Render with `quarto render reports/<file>.qmd`;
   if the Quarto CLI is missing, still produce a valid .qmd and note it in the handoff.
7. **Reproducibility:** seed 42 (config); every script runnable from repo root as `python -m src....`; pin library versions in handoff.
8. **Handoff protocol (mandatory, in this order):**
   a. write `context/handoffs/<aNN>.json` (schema: `_TEMPLATE.json`);
   b. append your section to `context/CONTEXT.md` and any decision rows to `context/DECISIONS.md`;
   c. `python scripts/state.py set <agent-id> done` (or `blocked`);
   d. `scripts/backup.sh <agent-id> "<short message>"` and put the returned tag in the handoff.
9. Be quantitative: always report numbers with units and the period they refer to.
10. If something required is unknown, make the most defensible assumption, log it in DECISIONS.md, and continue.

## Environment & compute
- Conda env **`leafriver`** (`environment.yml`; setup: `bash scripts/setup_env.sh`). Run every command inside it
  (`conda activate leafriver` or `conda run -n leafriver ...`). Never pip-install into base; if a package is missing,
  add it to `environment.yml`, log it in DECISIONS.md, and `conda env update -f environment.yml`.
- Single laptop, no HPC. Use at most `LR_N_JOBS` cores (`src.common.data.n_jobs()`); torch device via
  `src.common.data.torch_device()` (mps/cpu). Each optimizer ≤ 3 h wall time.
- Quarto kernel: `jupyter: leafriver`. Tests: `python -m pytest -q tests`.
- Hybrids and ensembles are allowed (weights fixed on calibration data only).
