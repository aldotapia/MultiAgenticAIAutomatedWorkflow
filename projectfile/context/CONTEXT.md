# Shared project context (append-only, newest at bottom)

Every agent appends ONE section when finished, max ~40 lines, using:

```
## <agent-id> — <YYYY-MM-DD HH:MM> — status: done|blocked
**Key findings:** (bullets, numbers with units)
**Outputs:** (paths)
**What downstream agents must know:** (bullets)
**Open issues / assumptions:** (bullets)
```

## scaffold — initial facts (verified at setup)
**Key findings:**
- data/raw/LeafRiverDaily.txt: 14,610 rows, 3 whitespace columns, no header, no negatives/NaN.
- Assumed columns: P, PET, Q in mm/day; start 1948-10-01, end 1988-09-30 (exactly 40 water years).
- Long-term means: P ≈ 1432 mm/yr, PET ≈ 1062 mm/yr, Q ≈ 500 mm/yr → runoff ratio ≈ 0.35.
- Under the date hypothesis, WY1949–WY1951 is WETTER than the rest (mean Q 1.75 vs 1.33 mm/d) → extrapolation risk; a02 recomputes for rows 357:1360.
**What downstream agents must know:**
- USER UPDATE: evaluation = rows 265:1360 (0-based), metrics rows 357:1360; calibration = rows 1360:14610 (365-row warm-up).
- PET seasonal cycle peaks at cycle row ~266 (June if start = 1948-10-01), so rows 265:1360 ≙ 1949-06-23..1952-06-21 by date. Unresolved — see ISSUES.md.
- Units confirmed by user: mm/day. Final report metrics: KGE and NSE only. Ensembles/hybrids allowed.
- Compute: single laptop (conda env `leafriver`, likely Apple Silicon → torch mps). No HPC.
- Leaf River is the classic test basin for SCE-UA (Duan et al., 1992), HYMOD, SAC-SMA.
