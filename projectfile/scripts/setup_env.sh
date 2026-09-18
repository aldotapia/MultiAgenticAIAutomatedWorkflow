#!/usr/bin/env bash
# One-time setup:  bash scripts/setup_env.sh
set -euo pipefail
cd "$(dirname "$0")/.."
command -v conda >/dev/null || { echo "Install Miniforge first: https://github.com/conda-forge/miniforge"; exit 1; }
if conda env list | grep -qE '^leafriver\s'; then
  conda env update -n leafriver -f environment.yml --prune
else
  conda env create -f environment.yml
fi
eval "$(conda shell.bash hook)"
conda activate leafriver
python -m ipykernel install --user --name leafriver --display-name "Python (leafriver)"
python - <<'PY'
import numpy, pandas, numba, torch, spotpy, optuna
from src.common.data import torch_device
print("numpy", numpy.__version__, "| numba", numba.__version__, "| torch", torch.__version__, "| device:", torch_device())
PY
quarto check jupyter || echo "WARN: quarto check failed"
python -m pytest -q tests
[ -d .git ] || { git init -q; git add -A; git -c user.name=leafriver -c user.email=leafriver@local commit -qm scaffold; }
echo "Environment ready. Activate with: conda activate leafriver"
