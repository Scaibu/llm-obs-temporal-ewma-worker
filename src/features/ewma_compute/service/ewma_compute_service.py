"""
Blueprint:
- Domain orchestrator service for EWMA baseline calculation and lifecycle updates.
- Follows canonical role (06) service.
- Coordinates mathematical rules, multi-step workflows, and outbound repository persistence.
- 100% comment-free function bodies per rule (6).
"""

from __future__ import annotations

from features.ewma_compute.contracts.ewma_compute_types import (
    EwmaRecord,
    AnomalyPayload,
    ClusterCost,
)
from features.ewma_compute.domain.rules.ewma_compute_rules import EwmaRules

from features.ewma_compute.domain.workflows.ewma_compute_workflow import (
    EwmaComputeWorkflow,
)
from features.ewma_compute.infrastructure.ports.ewma_compute_repository_port import (
    EwmaRepositoryPort,
)


class EwmaService:
    def __init__(self, repository: EwmaRepositoryPort | None = None) -> None:
        self._repository = repository
        self._workflow = EwmaComputeWorkflow()

    @staticmethod
    def calculate_new_ewma(
        current_value: float, previous_ewma: float, alpha: float = EwmaRules.DEFAULT_ALPHA
    ) -> float:
        return EwmaRules.calculate_new_ewma(current_value, previous_ewma, alpha=alpha)

    @staticmethod
    def process_update(
        current_value: float,
        existing_record: EwmaRecord | None,
        global_model_avg: float,
        alpha: float = EwmaRules.DEFAULT_ALPHA,
        service: str = "",
        model: str = "",
        hour_of_week: int = 0,
    ) -> EwmaRecord:
        return EwmaRules.process_update(
            current_value=current_value,
            existing_record=existing_record,
            global_model_avg=global_model_avg,
            alpha=alpha,
            service=service,
            model=model,
            hour_of_week=hour_of_week,
        )

    async def update_and_persist(
        self,
        service: str,
        model: str,
        hour_of_week: int,
        current_cost: float,
        global_model_avg: float,
        alpha: float = EwmaRules.DEFAULT_ALPHA,
        trace_id: str = "",
    ) -> EwmaRecord:
        existing = None
        if self._repository is not None:
            existing = await self._repository.get_record(
                service=service, model=model, hour_of_week=hour_of_week, trace_id=trace_id
            )

        updated = self._workflow.execute_record_update(
            current_cost=current_cost,
            existing_record=existing,
            global_model_avg=global_model_avg,
            alpha=alpha,
            service=service,
            model=model,
            hour_of_week=hour_of_week,
        )

        if self._repository is not None:
            await self._repository.save_record(updated, trace_id=trace_id)

        return updated

    def evaluate_anomaly(
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
        return self._workflow.execute_anomaly_check(
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

