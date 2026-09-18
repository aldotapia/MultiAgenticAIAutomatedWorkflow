"""Interface contract every model (slots 1-5) MUST implement so optimizers and the evaluator are model-agnostic."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class ParamSpec:
    name: str
    lower: float
    upper: float
    default: float
    units: str = "-"
    log_scale: bool = False
    description: str = ""


class BaseModel(ABC):
    model_id: str = "base"
    #: "conceptual" -> parameters optimized with global search via simulate()
    #: "trainable"  -> gradient/closed-form fit via fit(); hyperparameters exposed as ParamSpec
    kind: str = "conceptual"

    @abstractmethod
    def param_specs(self) -> list[ParamSpec]: ...

    @abstractmethod
    def simulate(self, forcing: pd.DataFrame, params: dict, initial_states: dict | None = None) -> pd.Series:
        """forcing: DataFrame (P, PET[, Q only if kind=='trainable' and used as target]) indexed by date.
        Returns simulated Q (mm/day) Series on the SAME index, warm-up included. Must be deterministic."""

    def fit(self, forcing: pd.DataFrame, target: pd.Series, params: dict) -> None:  # trainable models only
        raise NotImplementedError

    def save(self, path: str) -> None: ...
    def load(self, path: str) -> None: ...

    # helpers
    def bounds(self) -> np.ndarray:
        return np.array([[p.lower, p.upper] for p in self.param_specs()])

    def defaults(self) -> dict:
        return {p.name: p.default for p in self.param_specs()}
