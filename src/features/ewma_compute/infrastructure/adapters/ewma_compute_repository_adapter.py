"""
Blueprint:
- In-memory resilient adapter implementing EwmaRepositoryPort.
- Follows canonical role (11) adapters.
- 100% comment-free function/class bodies per rule (6).
"""

from __future__ import annotations

import asyncio
from features.ewma_compute.contracts.ewma_compute_types import EwmaRecord
from features.ewma_compute.infrastructure.ports.ewma_compute_repository_port import (

    EwmaRepositoryPort,
)


class InMemoryEwmaRepositoryAdapter(EwmaRepositoryPort):
    def __init__(self) -> None:
        self._store: dict[tuple[str, str, int], EwmaRecord] = {}
        self._lock = asyncio.Lock()

    async def get_record(
        self, service: str, model: str, hour_of_week: int, trace_id: str = ""
    ) -> EwmaRecord | None:
        async with self._lock:
            return self._store.get((service, model, hour_of_week))

    async def save_record(self, record: EwmaRecord, trace_id: str = "") -> None:
        async with self._lock:
            self._store[(record.service, record.model, record.hour_of_week)] = record
