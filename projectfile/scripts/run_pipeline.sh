#!/usr/bin/env bash
# Runs every ready agent, phase by phase; agents in the same phase run in parallel and SHARE the laptop cores.
# MAX_PARALLEL limits concurrency (default 5).  Re-run after fixing blocked agents.
set -euo pipefail
cd "$(dirname "$0")/.."
eval "$(conda shell.bash hook)"; conda activate leafriver
CORES=$(python -c 'import os;print(max(1,os.cpu_count()-1))')
MAXP="${MAX_PARALLEL:-5}"
while true; do
  READY=($(python scripts/state.py ready))
  [ ${#READY[@]} -eq 0 ] && break
  N=$(( ${#READY[@]} < MAXP ? ${#READY[@]} : MAXP ))
  export LR_N_JOBS=$(( CORES / N > 0 ? CORES / N : 1 ))
  echo ">> launching ${READY[*]:0:$N} with LR_N_JOBS=$LR_N_JOBS each"
  for a in "${READY[@]:0:$N}"; do scripts/run_agent.sh "$a" > "context/logs_${a}.txt" 2>&1 & done
  wait
done
python scripts/state.py show
