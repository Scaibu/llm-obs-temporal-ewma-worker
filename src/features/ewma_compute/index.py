"""
Blueprint:
- Public facade for ewma_compute feature.
- Follows canonical role (13) index: exports domain service and public types only; shields internal adapters.
- Preserves backward compatibility: exposes EwmaService directly for existing callers.
"""

from features.ewma_compute.service.ewma_compute_service import EwmaService
from features.ewma_compute.domain.rules.ewma_compute_rules import EwmaRules
from features.ewma_compute.domain.workflows.ewma_compute_workflow import (
    EwmaComputeWorkflow,
)
from features.ewma_compute.contracts.ewma_compute_types import (
    EwmaComputeCommand,
    AnomalyEvaluationCommand,
)
from features.ewma_compute.infrastructure.ports.ewma_compute_repository_port import (
    EwmaRepositoryPort,
)
from features.ewma_compute.infrastructure.adapters.ewma_compute_repository_adapter import (
    InMemoryEwmaRepositoryAdapter,
)

__all__ = [
    "EwmaService",
    "EwmaRules",
    "EwmaComputeWorkflow",
    "EwmaComputeCommand",
    "AnomalyEvaluationCommand",
    "EwmaRepositoryPort",
    "InMemoryEwmaRepositoryAdapter",
]
