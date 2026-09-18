---
name: a01-watershed-characterizer
description: Detailed procedure to produce a sourced, quantitative physical and hydrological characterization of the Leaf River basin (USGS 02472000, Collins MS) that informs model structure choices.
---
# Skill: Watershed characterization (Agent 1)

## Purpose
Give downstream agents (especially a03 model proposer) the physical knowledge needed to decide **which
processes matter**: storage/soil moisture dynamics, baseflow contribution, evapotranspiration control,
snow (likely irrelevant), routing delay, and human influence (dams, withdrawals). Every claim must be
sourced; every number must have units.

## Inputs
- `config/project.yaml` (basin identification to verify)
- `context/CONTEXT.md` (scaffold facts: P≈1432 mm/yr, PET≈1062 mm/yr, Q≈500 mm/yr, runoff ratio≈0.35)

## Step 1 — Identify the gauge precisely
1. Search USGS NWIS for "Leaf River near Collins, MS" (site 02472000). Record: site number, lat/lon (NAD83),
   drainage area (mi² and km²), datum elevation, period of record, regulation remarks.
2. Confirm the basin used in the classic literature: Duan et al. (1992), Sorooshian et al. (1993), Vrugt et al.
   (2003, SCEM-UA), Moradkhani et al. (2005). Literature commonly cites ≈1,944 km² — **verify, don't assume**.
3. Convert: if Q in the data were m³/s instead of mm/day, check `Q_mm = Q_m3s*86.4/A_km2` plausibility against
   the scaffold runoff ratio. Report this cross-check for a02.

## Step 2 — Physiography & topography
- HUC codes (HUC-8 03170004 Upper Leaf? verify), Pascagoula River system position, ecoregion (EPA Level III/IV).
- Elevation range, mean slope, stream length, drainage density, basin shape (compactness), main tributaries
  (e.g., Bogue Homa, Tallahala Creek — verify which are upstream of Collins).
- Sources: USGS StreamStats, NHDPlus, 3DEP. Include a location map in Quarto if a GeoJSON/boundary is fetchable;
  otherwise describe and cite.

## Step 3 — Climate
- Köppen class (humid subtropical Cfa expected), mean annual P, T, seasonal regime (winter–spring wet season,
  late summer–fall low flow), convective vs frontal storms, tropical cyclone influence.
- Aridity index PET/P and compare with the dataset (≈0.74). Budyko position.
- Snow: quantify (expected negligible) → justify omitting snow modules.
- Sources: NOAA NCEI normals, PRISM, CAMELS (if the gauge is in CAMELS: attributes file gives p_mean, pet_mean,
  aridity, high_prec_freq, frac_snow, etc.). **Check whether 02472000 is a CAMELS basin; if yes, extract all
  CAMELS attributes into a table.**

## Step 4 — Geology, soils, hydrogeology
- Coastal Plain sediments (sands, clays), aquifers (e.g., Citronelle, Miocene aquifer system), permeability.
- Soils: hydrologic soil groups (SSURGO/STATSGO), depth to restrictive layer, available water capacity.
- Implications: expected baseflow index, soil storage capacity range → give **plausible parameter ranges**
  (e.g., max soil storage 100–800 mm) that a03/a10 can use as priors.

## Step 5 — Land cover and human influence
- NLCD / historical land cover (pine forest, pasture, agriculture), urban fraction (Hattiesburg is downstream? verify).
- Dams/reservoirs, withdrawals, channelization during 1948–1988. Flag any non-stationarity risks.

## Step 6 — Hydrologic regime
- From USGS/literature: mean flow, flood seasonality, notable floods in 1948–1988 (esp. within eval WY1949–1951),
  low-flow characteristics, baseflow index estimates, recession behavior.
- Note: the evaluation window is wetter than the calibration record (scaffold); search for historic context.

## Step 7 — Benchmark literature synthesis
Table: study | model | objective | calibration/eval periods | reported NSE/KGE/RMSE. This gives a03 and a16
realistic performance targets (conceptual models typically NSE ~0.8–0.9 on Leaf River — verify).

## Step 8 — Process-relevance conclusions (most important section)
Explicit table "Process → evidence → importance (high/med/low) → modeling implication":
soil moisture accounting, saturation excess vs infiltration excess, interflow, groundwater/baseflow, ET limitation,
channel routing/lag (estimate time of concentration), snow, human regulation.

## Quarto report `reports/01_watershed.qmd`
YAML: title, author "Agent a01", date, `bibliography: references.bib`, `jupyter: leafriver`.
Sections: 1 Summary (≤10 bullets) · 2 Gauge & location · 3 Physiography · 4 Climate · 5 Geology/soils ·
6 Land cover & human influence · 7 Hydrologic regime · 8 Benchmark literature · 9 Process relevance &
modeling implications · 10 Parameter prior ranges · 11 Uncertainties/unverified facts · References.
Append BibTeX entries for every source (URLs with access date for web pages).

## Quality bar
- ≥10 distinct credible sources (USGS, NOAA, USDA-NRCS, peer-reviewed). No Wikipedia-only claims.
- Mark each fact as VERIFIED (primary source) or LITERATURE (secondary).
- Do not use the evaluation-period observed data for anything.

## Handoff `a01.json` key_numbers (minimum)
`drainage_area_km2`, `mean_elev_m`, `aridity_PET_over_P`, `snow_fraction`, `baseflow_index_est`,
`time_of_concentration_days_est`, `in_camels` (bool), `benchmark_nse_range`.
downstream_notes for a02 (unit cross-check), a03 (process priorities), a10 (parameter priors).

## Handoff checklist (do not skip)
- [ ] Outputs listed above exist and are non-empty
- [ ] `context/handoffs/a01.json` written (schema `context/handoffs/_TEMPLATE.json`), incl. `downstream_notes`
- [ ] Section appended to `context/CONTEXT.md`; decisions appended to `context/DECISIONS.md`
- [ ] `python scripts/state.py set a01-watershed-characterizer done`
- [ ] `scripts/backup.sh a01-watershed-characterizer "<message>"` → tag stored in handoff `backup_tag`
