"""Canonical KGE/NSE (reference implementations). Agent 4 may ADD metrics but must not change these."""
from __future__ import annotations
import numpy as np


def _clean(sim, obs):
    sim, obs = np.asarray(sim, float), np.asarray(obs, float)
    m = np.isfinite(sim) & np.isfinite(obs)
    return sim[m], obs[m]


def nse(sim, obs) -> float:
    s, o = _clean(sim, obs)
    return 1.0 - np.sum((s - o) ** 2) / np.sum((o - o.mean()) ** 2)


def kge_components(sim, obs) -> dict:
    s, o = _clean(sim, obs)
    r = np.corrcoef(s, o)[0, 1]
    alpha = s.std() / o.std()
    beta = s.mean() / o.mean()
    kge = 1.0 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
    return {"KGE": kge, "r": r, "alpha": alpha, "beta": beta}


def kge(sim, obs) -> float:
    return kge_components(sim, obs)["KGE"]
