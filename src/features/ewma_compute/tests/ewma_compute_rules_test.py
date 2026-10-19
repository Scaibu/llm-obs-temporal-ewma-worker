"""
Blueprint:
- Exhaustive unit tests for EWMA domain rules and workflows.
- Verifies mathematical invariance, property bounds, adversarial inputs, and noise floor thresholds.
- Follows canonical role (14) tests.
"""

import math
import pytest
from features.ewma_compute.domain.rules.ewma_compute_rules import EwmaRules
from features.ewma_compute.domain.workflows.ewma_compute_workflow import EwmaComputeWorkflow
from features.ewma_compute.contracts.ewma_compute_schema import EwmaSchemaMapper
from features.ewma_compute.contracts.ewma_compute_types import EwmaRecord, ClusterCost



def test_calculate_new_ewma() -> None:
    val = EwmaRules.calculate_new_ewma(100.0, 50.0, 0.1)
    assert val == 55.0


def test_calculate_new_ewma_invalid_alpha() -> None:
    with pytest.raises(ValueError):
        EwmaRules.calculate_new_ewma(100.0, 50.0, 0.0)

    with pytest.raises(ValueError):
        EwmaRules.calculate_new_ewma(100.0, 50.0, 1.5)

    with pytest.raises(ValueError):
        EwmaRules.calculate_new_ewma(100.0, 50.0, float("nan"))


def test_calculate_new_ewma_negative_or_infinite_inputs() -> None:
    with pytest.raises(ValueError, match="current_value must be non-negative"):
        EwmaRules.calculate_new_ewma(-10.0, 50.0)

    with pytest.raises(ValueError, match="previous_ewma must be non-negative"):
        EwmaRules.calculate_new_ewma(10.0, -5.0)

    with pytest.raises(ValueError, match="must be a finite number"):
        EwmaRules.calculate_new_ewma(float("inf"), 50.0)


def test_process_update_cold_start() -> None:
    record = EwmaRules.process_update(
        120.0, None, 80.0, service="srv", model="m1", hour_of_week=42
    )
    assert record.service == "srv"
    assert record.model == "m1"
    assert record.hour_of_week == 42
    assert record.ewma_value == 80.0
    assert record.sample_count == 1
    assert record.is_cold_start is True


def test_process_update_invalid_hour() -> None:
    with pytest.raises(ValueError, match="hour_of_week must be between 0 and 167"):
        EwmaRules.process_update(10.0, None, 5.0, hour_of_week=168)

    with pytest.raises(ValueError, match="hour_of_week must be between 0 and 167"):
        EwmaRules.process_update(10.0, None, 5.0, hour_of_week=-1)


def test_process_update_transition_cold_start() -> None:
    existing = EwmaRecord(
        service="srv",
        model="gpt-4",
        hour_of_week=42,
        ewma_value=50.0,
        sample_count=6,
        is_cold_start=True,
    )
    record = EwmaRules.process_update(100.0, existing, 0.0)
    assert record.ewma_value == 55.0
    assert record.sample_count == 7
    assert record.is_cold_start is False


def test_evaluate_anomaly_detected() -> None:
    record = EwmaRecord(
        service="srv",
        model="gpt-4",
        hour_of_week=10,
        ewma_value=10.0,
        sample_count=10,
        is_cold_start=False,
    )
    workflow = EwmaComputeWorkflow()
    anomaly = workflow.execute_anomaly_check(
        service="srv",
        model="gpt-4",
        hour_of_week=10,
        current_cost=25.0,
        record=record,
        timestamp="2026-10-19T00:00:00Z",
        cluster_costs=[ClusterCost(cluster_id="c1", cost=25.0)],
        multiplier=2.0,
    )
    assert anomaly is not None
    assert anomaly.current_cost == 25.0
    assert anomaly.threshold_value == 20.0


def test_evaluate_anomaly_cold_start_ignored() -> None:
    record = EwmaRecord(
        service="srv",
        model="gpt-4",
        hour_of_week=10,
        ewma_value=10.0,
        sample_count=3,
        is_cold_start=True,
    )
    workflow = EwmaComputeWorkflow()
    anomaly = workflow.execute_anomaly_check(
        service="srv",
        model="gpt-4",
        hour_of_week=10,
        current_cost=50.0,
        record=record,
        timestamp="2026-10-19T00:00:00Z",
        cluster_costs=[],
        multiplier=2.0,
    )
    assert anomaly is None


def test_evaluate_anomaly_noise_floor_zero_baseline() -> None:
    record = EwmaRecord(
        service="srv",
        model="gpt-4",
        hour_of_week=10,
        ewma_value=0.0,
        sample_count=10,
        is_cold_start=False,
    )
    workflow = EwmaComputeWorkflow()
    tiny_cost = 1e-7
    anomaly = workflow.execute_anomaly_check(
        service="srv",
        model="gpt-4",
        hour_of_week=10,
        current_cost=tiny_cost,
        record=record,
        timestamp="2026-10-19T00:00:00Z",
        cluster_costs=[],
        multiplier=2.0,
    )
    assert anomaly is None


def test_schema_mapper_invariants() -> None:
    valid_data = {
        "service": "billing",
        "model": "gpt-4o",
        "hour_of_week": 167,
        "ewma_value": 4.5,
        "sample_count": 8,
        "is_cold_start": False,
    }
    record = EwmaSchemaMapper.from_record_dict(valid_data)
    assert record.hour_of_week == 167
    assert record.sample_count == 8

    with pytest.raises(ValueError, match="hour_of_week"):
        invalid = dict(valid_data)
        invalid["hour_of_week"] = 168
        EwmaSchemaMapper.from_record_dict(invalid)

    with pytest.raises(ValueError, match="sample_count"):
        invalid = dict(valid_data)
        invalid["sample_count"] = 0
        EwmaSchemaMapper.from_record_dict(invalid)

