#!/usr/bin/env bash
# Headless run of one agent:  scripts/run_agent.sh a02-data-analyst
set -euo pipefail
cd "$(dirname "$0")/.."
A="${1:?agent}"
eval "$(conda shell.bash hook)"; conda activate leafriver
export LR_N_JOBS="${LR_N_JOBS:-$(python -c 'import os;print(max(1,os.cpu_count()-1))')}"
[ "$A" = "a16-evaluator" ] && export LR_AGENT=a16 || export LR_AGENT="${A%%-*}"
python scripts/state.py set "$A" running
claude -p "Use the $A subagent to complete its task as defined in .claude/agents/$A.md. Follow CLAUDE.md strictly. Conda env 'leafriver' is active; LR_N_JOBS=$LR_N_JOBS cores available to you. Finish with the handoff protocol." \
  --permission-mode acceptEdits
