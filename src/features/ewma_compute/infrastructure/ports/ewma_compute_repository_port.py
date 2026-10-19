"""
Blueprint:
- Abstract hexagonal outbound port interface for EWMA baseline persistence.
- Follows canonical role (10) ports.
- 100% comment-free function/class bodies per rule (6).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from features.ewma_compute.contracts.ewma_compute_types import EwmaRecord



class EwmaRepositoryPort(ABC):
    @abstractmethod
    async def get_record(
        self, service: str, model: str, hour_of_week: int, trace_id: str = ""
    ) -> EwmaRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def save_record(self, record: EwmaRecord, trace_id: str = "") -> None:
        raise NotImplementedError
