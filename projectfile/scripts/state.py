"""State helper. python scripts/state.py show | set <agent> <status> | ready"""
import json, sys, yaml
from pathlib import Path
R = Path(__file__).resolve().parents[1]
S = R / "context/state.json"
state = json.loads(S.read_text())
dag = yaml.safe_load((R / "orchestration.yaml").read_text())["agents"]
cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
if cmd == "show":
    for k, v in state.items(): print(f"{k:32s} {v}")
elif cmd == "set":
    state[sys.argv[2]] = sys.argv[3]; S.write_text(json.dumps(state, indent=2)); print("ok")
elif cmd == "ready":
    for a, spec in dag.items():
        if state[a] == "pending" and all(state[d] == "done" for d in spec["depends_on"]):
            print(a)
