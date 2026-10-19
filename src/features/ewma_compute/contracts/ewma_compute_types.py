"""
Blueprint:
- Pure domain models, input/output DTOs, and error types for EWMA feature.
- Follows canonical role (04) types.
- Comment-free function/class bodies.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class EwmaRecord:
    service: str
    model: str
    hour_of_week: int
    ewma_value: float
    sample_count: int
    is_cold_start: bool
    updated_at: datetime | None = None


@dataclass
class ClusterCost:
    cluster_id: str
    cost: float


@dataclass
class AnomalyPayload:
    service: str
    model: str
    hour_of_week: int
    current_cost: float
    ewma_value: float
    threshold_value: float
    sample_count: int
    timestamp: str
    cluster_drilldown: list[ClusterCost]


@dataclass(frozen=True)
class EwmaComputeCommand:
    current_value: float
    existing_record: EwmaRecord | None
    global_model_avg: float
    alpha: float = 0.1
    service: str = ""
    model: str = ""
    hour_of_week: int = 0


@dataclass(frozen=True)
class AnomalyEvaluationCommand:
    service: str
    model: str
    hour_of_week: int
    current_cost: float
    record: EwmaRecord
    timestamp: str
    cluster_costs: list[ClusterCost]
    multiplier: float = 2.0


__all__ = [
    "EwmaRecord",
    "AnomalyPayload",
    "ClusterCost",
    "EwmaComputeCommand",
    "AnomalyEvaluationCommand",
]

