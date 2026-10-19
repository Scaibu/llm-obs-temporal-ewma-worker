"""
Blueprint:
- Pure business logic rules and decision tables for Exponentially Weighted Moving Average (EWMA).
- Mathematical formulation: S_t = alpha * Y_t + (1 - alpha) * S_{t-1}.
- Invariants:
  1. Alpha bounded in (0.0, 1.0].
  2. Input values, EWMA values, and global averages must be finite non-negative numbers (val >= 0.0, not NaN, not Inf).
  3. hour_of_week must be bounded in [0, 167].
  4. Cold start threshold: sample_count < 7 is cold start, sample_count >= 7 is warm.
  5. Anomaly evaluation is suppressed during cold start; baseline comparisons apply a noise floor epsilon to prevent false positives on zero-cost baselines.
- Follows canonical role (07) rules: 100% comment-free function bodies in accordance with rule (6).
"""

from __future__ import annotations

import math
from features.ewma_compute.contracts.ewma_compute_types import (
    EwmaRecord,
    AnomalyPayload,
    ClusterCost,
)



class EwmaRules:
    COLD_START_MIN_SAMPLES: int = 7
    DEFAULT_ALPHA: float = 0.1
    EPSILON_NOISE_FLOOR: float = 1e-6
    MAX_HOUR_OF_WEEK: int = 167

    @classmethod
    def validate_non_negative_finite(cls, value: float, field_name: str) -> None:
        if math.isnan(value) or math.isinf(value):
            raise ValueError(f"{field_name} must be a finite number, got {value}")
        if value < 0.0:
            raise ValueError(f"{field_name} must be non-negative, got {value}")

    @classmethod
    def validate_hour_of_week(cls, hour_of_week: int) -> None:
        if not (0 <= hour_of_week <= cls.MAX_HOUR_OF_WEEK):
            raise ValueError(
                f"hour_of_week must be between 0 and {cls.MAX_HOUR_OF_WEEK}, got {hour_of_week}"
            )

    @classmethod
    def calculate_new_ewma(
        cls, current_value: float, previous_ewma: float, alpha: float = DEFAULT_ALPHA
    ) -> float:
        if math.isnan(alpha) or math.isinf(alpha) or not (0.0 < alpha <= 1.0):
            raise ValueError(f"Alpha must be in (0, 1], got {alpha}")
        cls.validate_non_negative_finite(current_value, "current_value")
        cls.validate_non_negative_finite(previous_ewma, "previous_ewma")
        return (alpha * current_value) + ((1.0 - alpha) * previous_ewma)

    @classmethod
    def process_update(
        cls,
        current_value: float,
        existing_record: EwmaRecord | None,
        global_model_avg: float,
        alpha: float = DEFAULT_ALPHA,
        service: str = "",
        model: str = "",
        hour_of_week: int = 0,
    ) -> EwmaRecord:
        cls.validate_non_negative_finite(current_value, "current_value")
        cls.validate_non_negative_finite(global_model_avg, "global_model_avg")

        if existing_record is None:
            cls.validate_hour_of_week(hour_of_week)
            return EwmaRecord(
                service=service,
                model=model,
                hour_of_week=hour_of_week,
                ewma_value=global_model_avg,
                sample_count=1,
                is_cold_start=True,
            )

        cls.validate_hour_of_week(existing_record.hour_of_week)
        new_sample_count = existing_record.sample_count + 1
        new_ewma = cls.calculate_new_ewma(
            current_value, existing_record.ewma_value, alpha=alpha
        )
        new_is_cold_start = new_sample_count < cls.COLD_START_MIN_SAMPLES

        return EwmaRecord(
            service=existing_record.service,
            model=existing_record.model,
            hour_of_week=existing_record.hour_of_week,
            ewma_value=new_ewma,
            sample_count=new_sample_count,
            is_cold_start=new_is_cold_start,
        )

    @classmethod
    def evaluate_anomaly(
        cls,
        service: str,
        model: str,
        hour_of_week: int,
        current_cost: float,
        record: EwmaRecord,
        timestamp: str,
        cluster_costs: list[ClusterCost],
        multiplier: float = 2.0,
        noise_floor: float = EPSILON_NOISE_FLOOR,
    ) -> AnomalyPayload | None:
        cls.validate_hour_of_week(hour_of_week)
        cls.validate_non_negative_finite(current_cost, "current_cost")

        if record.is_cold_start:
            return None

        effective_baseline = max(record.ewma_value, noise_floor)
        threshold = effective_baseline * multiplier
        if current_cost > threshold:
            return AnomalyPayload(
                service=service,
                model=model,
                hour_of_week=hour_of_week,
                current_cost=current_cost,
                ewma_value=record.ewma_value,
                threshold_value=threshold,
                sample_count=record.sample_count,
                timestamp=timestamp,
                cluster_drilldown=cluster_costs,
            )
        return None

