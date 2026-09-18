# Leaf River multi-agent streamflow modeling

Runtime: **Claude Code** (subagents in `.claude/agents/`, skills in `.claude/skills/`). Project rules: `CLAUDE.md`.
Single source of truth for periods/paths: `config/project.yaml`. DAG: `orchestration.yaml`.

## Quick start
```bash
bash scripts/setup_env.sh                # creates conda env "leafriver" (incl. Quarto, torch/MPS), runs tests, git init
conda activate leafriver
python scripts/state.py ready            # which agents can start now
scripts/run_agent.sh a02-data-analyst    # run one agent headless
scripts/run_pipeline.sh                  # run all ready agents, phase by phase (parallel inside phase)
```
Interactive alternative: open `claude` in repo root and say *"Use the a01-watershed-characterizer subagent"*.

## Layout
```
CLAUDE.md               shared rules + start-up ritual + handoff protocol
orchestration.yaml      phases, dependencies, I/O contracts
config/                 project.yaml (periods), models.yaml (a03), metrics.yaml (a04), optimization.yaml (a10)
.claude/agents/         16 subagent definitions
.claude/skills/         16 detailed skills (one per agent)
context/                CONTEXT.md (shared memory), DECISIONS.md, ISSUES.md, state.json, handoffs/*.json, backups/
src/common/             data.py (loader + eval guard), metrics.py (canonical KGE/NSE), model_api.py (BaseModel)
src/models/, src/optimization/   filled by agents 5-9 and 10-15
reports/                Quarto website (_quarto.yml, references.bib, NN_*.qmd)
results/                build/, calibration/model_N/, evaluation/, figures/
scripts/                setup_env.sh, backup.sh, state.py, run_agent.sh, run_pipeline.sh
environment.yml         conda env `leafriver`
```

## Periods (0-based rows, half-open; switch to calendar dates with `periods.definition: dates`)
- Evaluation (Agent 16 only): run 265:1360, warm-up 265:357, metrics 357:1360 (1,003 days).
- Calibration: run 1360:14610, warm-up 1360:1725; internal train 1725:12053, validation 12053:14610.
- Final report metrics: KGE and NSE only. Ensembles/hybrids allowed.
- ⚠ Rows 265:1360 ≙ 1949-06-23..1952-06-21 if the file starts 1948-10-01 (see context/ISSUES.md).

## Compute
Laptop only. `run_pipeline.sh` splits cores among agents in the same phase (`LR_N_JOBS`); `MAX_PARALLEL=2 scripts/run_pipeline.sh`
to reduce load.

## Backups / context sharing
Each agent ends with `scripts/backup.sh <agent>` → git commit + tag `backup/<agent>-<ts>` + tarball in `context/backups/`.
Roll back: `git checkout backup/<agent>-<ts> -- <path>`.
