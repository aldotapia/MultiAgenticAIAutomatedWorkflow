"""Canonical data access for all agents. Do NOT re-implement loading or period slicing elsewhere."""
from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_config(name: str = "project") -> dict:
    with open(ROOT / "config" / f"{name}.yaml") as f:
        return yaml.safe_load(f)


def load_data() -> pd.DataFrame:
    """Daily DataFrame (P, PET, Q in mm/day, float64) with date index and a 'row' column (0-based file row)."""
    cfg = load_config()["data"]
    df = pd.read_csv(ROOT / cfg["raw_file"], sep=r"\s+", header=None,
                     names=[c["name"] for c in cfg["columns"]], dtype="float64")
    if len(df) != cfg["n_rows"]:
        raise ValueError(f"Expected {cfg['n_rows']} rows, got {len(df)}")
    df.index = pd.date_range(cfg["start_date"], periods=len(df), freq="D", name="date")
    assert str(df.index[-1].date()) == cfg["end_date"], "Date span mismatch"
    df["row"] = np.arange(len(df))
    return df


def _periods() -> dict:
    p = load_config()["periods"]
    return p[p["definition"]], p["definition"]


def _select(df: pd.DataFrame, bounds, definition: str) -> pd.DataFrame:
    if definition == "index":
        a, b = bounds
        return df[(df["row"] >= a) & (df["row"] < b)]
    return df.loc[bounds[0]:bounds[1]]


def _guard(which: str, allow_evaluation: bool):
    if which == "evaluation" and not (allow_evaluation and os.environ.get("LR_AGENT") == "a16"):
        raise PermissionError("Evaluation period is reserved for Agent 16 (set LR_AGENT=a16).")


def slice_run(df: pd.DataFrame, which: str, allow_evaluation: bool = False) -> pd.DataFrame:
    """Full simulation window (warm-up included) for 'calibration' or 'evaluation'."""
    _guard(which, allow_evaluation)
    per, d = _periods()
    return _select(df, per[which]["run"], d)


def metric_mask(frame: pd.DataFrame, which: str) -> np.ndarray:
    """Boolean mask over `frame` rows selecting the metric window (warm-up excluded)."""
    per, d = _periods()
    a, b = per[which]["metric"]
    if d == "index":
        return ((frame["row"] >= a) & (frame["row"] < b)).to_numpy()
    return ((frame.index >= a) & (frame.index <= b))


def internal_mask(frame: pd.DataFrame, part: str) -> np.ndarray:
    """part = 'train' | 'validation' inside calibration."""
    per, d = _periods()
    a, b = per["calibration_internal"][part]
    if d == "index":
        return ((frame["row"] >= a) & (frame["row"] < b)).to_numpy()
    return ((frame.index >= a) & (frame.index <= b))


def n_jobs(default: int = 1) -> int:
    return int(os.environ.get(load_config()["compute"]["n_jobs_env_var"], default))


def torch_device() -> str:
    import torch
    for dev in load_config()["compute"]["torch_device_priority"]:
        if dev == "cuda" and torch.cuda.is_available(): return "cuda"
        if dev == "mps" and getattr(torch.backends, "mps", None) and torch.backends.mps.is_available(): return "mps"
    return "cpu"
