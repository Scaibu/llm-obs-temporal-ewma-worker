"""
Blueprint:
- Validation and Anti-Corruption Layer (ACL) for EWMA domain models.
- Follows canonical role (03) schema.
"""

from __future__ import annotations

from typing import Any, Mapping
from features.ewma_compute.contracts.ewma_compute_types import (
    EwmaRecord,
    AnomalyPayload,
)



class EwmaSchemaMapper:
    @staticmethod
    def to_record_dict(record: EwmaRecord) -> dict[str, Any]:
        return {
            "service": record.service,
            "model": record.model,
            "hour_of_week": record.hour_of_week,
            "ewma_value": record.ewma_value,
            "sample_count": record.sample_count,
            "is_cold_start": record.is_cold_start,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        }

    @staticmethod
    def from_record_dict(data: Mapping[str, Any]) -> EwmaRecord:
        hour_of_week = int(data["hour_of_week"])
        if not (0 <= hour_of_week <= 167):
            raise ValueError(f"hour_of_week must be in [0, 167], got {hour_of_week}")
        ewma_value = float(data["ewma_value"])
        if ewma_value < 0.0:
            raise ValueError(f"ewma_value must be non-negative, got {ewma_value}")
        sample_count = int(data["sample_count"])
        if sample_count < 1:
            raise ValueError(f"sample_count must be at least 1, got {sample_count}")
        return EwmaRecord(
            service=str(data["service"]),
            model=str(data["model"]),
            hour_of_week=hour_of_week,
            ewma_value=ewma_value,
            sample_count=sample_count,
            is_cold_start=bool(data["is_cold_start"]),
        )

