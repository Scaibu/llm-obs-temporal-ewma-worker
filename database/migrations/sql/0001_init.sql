CREATE TABLE ewma_baselines (
  id BIGSERIAL PRIMARY KEY,
  service VARCHAR(255) NOT NULL,
  model VARCHAR(255) NOT NULL,
  hour_of_week SMALLINT NOT NULL,
  ewma_value DOUBLE PRECISION NOT NULL,
  sample_count INTEGER NOT NULL DEFAULT 1,
  is_cold_start BOOLEAN NOT NULL DEFAULT TRUE,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT ewma_baselines_service_model_hour_uk UNIQUE (service, model, hour_of_week),
  CONSTRAINT ewma_baselines_hour_of_week_range_ck CHECK (hour_of_week >= 0 AND hour_of_week <= 167),
  CONSTRAINT ewma_baselines_ewma_value_nonneg_ck CHECK (ewma_value >= 0.0),
  CONSTRAINT ewma_baselines_sample_count_pos_ck CHECK (sample_count >= 1),
  CONSTRAINT ewma_baselines_service_nonempty_ck CHECK (service = btrim(service) AND service <> ''),
  CONSTRAINT ewma_baselines_model_nonempty_ck CHECK (model = btrim(model) AND model <> '')
);

