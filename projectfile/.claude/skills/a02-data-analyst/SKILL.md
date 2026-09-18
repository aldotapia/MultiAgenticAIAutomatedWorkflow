---
name: a02-data-analyst
description: Detailed EDA and quality-control procedure for the Leaf River daily P/PET/Q record, producing an extensive Quarto variable description and signatures that inform model and metric choice.
---
# Skill: Data description & evaluation (Agent 2)

## Purpose
Establish exactly what the data are, whether they are trustworthy, and what hydrological behavior they show.
Downstream: a03 (processes, memory length, nonlinearity), a04 (flow distribution → metric choice),
builders (units, zero handling), a10 (response surface expectations).

## Allowed use of the evaluation period
You MAY describe the full record (including WY1949–1951) — that's EDA. You must NOT derive any quantity
intended to be plugged into models (e.g., scaling stats) from it. Report calibration-only stats separately.

## Step 0 — Load
```python
from src.common.data import load_data
df = load_data()                     # P, PET, Q; date index 1948-10-01..1988-09-30
df.to_parquet("data/processed/leafriver_daily.parquet")
```
Add derived columns in a SEPARATE frame for the report only (water year, month, season).

## Step 1 — Structure & integrity
- Shape, dtypes, date continuity (no gaps), duplicates, NaN, negatives, exact zeros per variable,
  numeric precision (decimals as stored), constant runs (≥5 identical consecutive values = possible infill).
- Verify the start-date assumption: 14,610 days = 40 WY incl. 10 leap days. Check seasonality of PET peaks in
  Jun–Jul (Northern Hemisphere) — if PET peaks in Dec–Jan the date alignment is wrong → raise ISSUE.
- Units: test mm/day hypothesis — annual P ~1,400 mm plausible for south MS; Q/P ratio; compare with a01's
  drainage area (Q mm/d ↔ m³/s conversion).

## Step 2 — Per-variable description (one subsection each for P, PET, Q)
Table of: mean, sd, CV, skewness, kurtosis, min, percentiles (1,5,10,25,50,75,90,95,99,99.9), max,
% zeros, % days > thresholds. Plots: full time series, zoom per water year (small multiples), histogram +
log-histogram, ECDF, monthly boxplots, annual totals bar chart with trend line.
- **P:** wet-day frequency (>0.1 mm, >1 mm), mean wet-day intensity, dry/wet spell length distributions,
  annual maxima (Rx1day, Rx5day), seasonality index, Mann-Kendall trend on annual totals.
- **PET:** seasonal cycle shape (is it a smooth climatology repeated each year? test inter-annual variance of
  same-DOY values → if ~0, PET is climatological, important for a03), P–PET correlation.
- **Index/date alignment audit (mandatory subsection):** the user-defined evaluation window is rows 265:1360
  (described as Oct 1 1948–Sep 30 1951), but the scaffold found PET peaks at cycle row ~266 (June under a
  1948-10-01 start), implying rows 265:1360 ≙ 1949-06-23..1952-06-21. Quantify with PET/P phase (harmonic fit,
  peak day), Q seasonality, and compare both hypotheses. Report conclusion; do NOT change config — raise ISSUE.
- **Q:** flow duration curve (log y), percentiles Q5/Q50/Q95, high-flow and low-flow frequency/duration,
  annual peaks, rising/falling limb stats, flashiness (Richards–Baker index).

## Step 3 — Hydrological signatures (compute, table with units)
Runoff ratio (total and per WY), elasticity of Q to P, baseflow index (Lyne–Hollick α=0.925, 3 passes; and
Eckhardt), recession analysis (−dQ/dt vs Q log-log, fit b and a; master recession constant k),
FDC slope (33–66%), high/low flow frequency, peak timing, lag between P and Q (cross-correlation up to 30 d),
autocorrelation of Q (lag-1, e-folding time), P–Q event runoff coefficients (select ≥20 isolated events),
seasonal water balance (P − PET − Q), Budyko plot per WY, dynamic storage estimate (cumulative P−Q−AET proxy).

## Step 4 — Consistency & quality checks
- Double-mass curve cumulative P vs cumulative Q (breaks → non-stationarity).
- Years with Q > P (impossible) or runoff ratio outliers.
- Q responses without P (possible P undercatch/timing offset) and large P without Q response.
- Check whether P→Q lag suggests a 1-day timing offset in the data.
- Stationarity: Pettitt test on annual Q and P; compare decades.

## Step 5 — Period comparison (critical)
Table and plots comparing (EDA may read evaluation rows directly by index): evaluation metric rows 357:1360,
calibration metric rows 1725:14610, internal train 1725:12053, internal validation 12053:14610, unused rows 0:265. Mean/percentiles of P, PET, Q, runoff ratio, FDC overlays, peak counts.
Quantify how far eval conditions are outside calibration distribution (e.g., % eval days with Q > calib Q99).

## Step 6 — Implications section
Bullet list for each downstream agent: memory length (recommended LSTM sequence length or conceptual warm-up),
evidence of nonlinearity/threshold behavior, importance of baseflow, suggested objective transformation given
skewness (a04), whether PET is climatological, risks (wet eval period, extrapolation).

## Quarto `reports/02_data.qmd`
Executable; figures saved to `results/figures/a02_*.png` too. Sections: Summary · File & structure ·
Variable dictionary (name, description, units, source, resolution, range) · P · PET · Q · Joint analysis &
signatures · Quality control · Period comparison · Implications · Appendix (code).
Use `#| label: fig-...` and `#| fig-cap:`; tables via pandas `.to_markdown()` or `great_tables` if available.

## Handoff `a02.json` key_numbers (minimum)
`P_mean_mm_yr`, `PET_mean_mm_yr`, `Q_mean_mm_yr`, `runoff_ratio`, `bfi_lyne_hollick`, `recession_k`,
`lag_peak_xcorr_days`, `Q_skewness`, `pct_zero_P`, `pet_is_climatological`, `eval_vs_cal_Q_mean_ratio`,
`qc_flags` (list).

## Handoff checklist (do not skip)
- [ ] Outputs listed above exist and are non-empty
- [ ] `context/handoffs/a02.json` written (schema `context/handoffs/_TEMPLATE.json`), incl. `downstream_notes`
- [ ] Section appended to `context/CONTEXT.md`; decisions appended to `context/DECISIONS.md`
- [ ] `python scripts/state.py set a02-data-analyst done`
- [ ] `scripts/backup.sh a02-data-analyst "<message>"` → tag stored in handoff `backup_tag`
