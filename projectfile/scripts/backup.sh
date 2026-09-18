#!/usr/bin/env bash
# Usage: scripts/backup.sh <agent_id> ["message"]
# 1) git commit + tag  2) timestamped tarball of context/, config/, reports/, src/, results/ (no raw data)
set -euo pipefail
cd "$(dirname "$0")/.."
AGENT="${1:?agent id required}"; MSG="${2:-checkpoint}"
TS=$(date +%Y%m%d-%H%M%S)
[ -d .git ] || git init -q
git config user.name  >/dev/null || git config user.name  "leafriver-agents"
git config user.email >/dev/null || git config user.email "agents@leafriver.local"
git add -A
git commit -qm "[$AGENT] $MSG" || echo "nothing to commit"
git tag -f "backup/${AGENT}-${TS}" >/dev/null
tar --exclude='results/**/*.pt' -czf "context/backups/${AGENT}-${TS}.tar.gz" context/CONTEXT.md context/DECISIONS.md context/ISSUES.md context/state.json context/handoffs config reports src tests results 2>/dev/null || true
echo "backup/${AGENT}-${TS}"
