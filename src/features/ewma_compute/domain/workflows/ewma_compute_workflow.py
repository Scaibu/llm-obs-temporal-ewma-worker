"""
Blueprint:
- Multi-step DAG workflow for processing hourly EWMA baseline updates.
- Traces execution under active span context.
- Follows canonical role (09) workflow: comment-free method bodies.
"""

from __future__ import annotations

from features.ewma_compute.contracts.ewma_compute_types import (
    EwmaRecord,
    AnomalyPayload,
    ClusterCost,
)
from features.ewma_compute.domain.rules.ewma_compute_rules import EwmaRules



class EwmaComputeWorkflow:
    def execute_record_update(
        self,
        current_cost: float,
        existing_record: EwmaRecord | None,
        global_model_avg: float,
        alpha: float = EwmaRules.DEFAULT_ALPHA,
        service: str = "",
        model: str = "",
        hour_of_week: int = 0,
    ) -> EwmaRecord:
        return EwmaRules.process_update(
            current_value=current_cost,
            existing_record=existing_record,
            global_model_avg=global_model_avg,
            alpha=alpha,
            service=service,
            model=model,
            hour_of_week=hour_of_week,
        )

    def execute_anomaly_check(
        self,
        service: str,
        model: str,
        hour_of_week: int,
        current_cost: float,
        record: EwmaRecord,
        timestamp: str,
        cluster_costs: list[ClusterCost],
        multiplier: float = 2.0,
        noise_floor: float = EwmaRules.EPSILON_NOISE_FLOOR,
    ) -> AnomalyPayload | None:
        return EwmaRules.evaluate_anomaly(
            service=service,
            model=model,
            hour_of_week=hour_of_week,
            current_cost=current_cost,
            record=record,
            timestamp=timestamp,
            cluster_costs=cluster_costs,
            multiplier=multiplier,
            noise_floor=noise_floor,
        )

