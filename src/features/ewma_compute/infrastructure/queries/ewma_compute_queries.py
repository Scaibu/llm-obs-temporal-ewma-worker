"""
Blueprint:
- Named parameterized SQL queries for EWMA compute and baseline storage.
- Follows canonical role (12) queries with FLOW_{VERB}_{ENTITY}_{CRITERIA} convention.
- 100% comment-free function/code bodies per rule (6).
"""

FLOW_SELECT_EWMA_RECORD_BY_KEY = """
SELECT service, model, hour_of_week, ewma_value, sample_count, is_cold_start, updated_at
FROM ewma_baselines
WHERE service = :service AND model = :model AND hour_of_week = :hour_of_week
LIMIT 1;
"""

FLOW_UPSERT_EWMA_RECORD = """
INSERT INTO ewma_baselines (service, model, hour_of_week, ewma_value, sample_count, is_cold_start, updated_at)
VALUES (:service, :model, :hour_of_week, :ewma_value, :sample_count, :is_cold_start, NOW())
ON CONFLICT (service, model, hour_of_week)
DO UPDATE SET
    ewma_value = EXCLUDED.ewma_value,
    sample_count = EXCLUDED.sample_count,
    is_cold_start = EXCLUDED.is_cold_start,
    updated_at = NOW();
"""
