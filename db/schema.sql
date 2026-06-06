CREATE TABLE cloud_metrics (
    ts TIMESTAMPTZ NOT NULL,

    service_name VARCHAR(50) NOT NULL,
    metric_name VARCHAR(50) NOT NULL,

    metric_value DOUBLE PRECISION NOT NULL,
    estimated_cost DOUBLE PRECISION NOT NULL,

    environment VARCHAR(20) NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable(
    'cloud_metrics',
    'ts',
    if_not_exists => TRUE
);