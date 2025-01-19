-- Create table for processed real-time data with partitioning

CREATE TABLE IF NOT EXISTS realtime_feed (
    id SERIAL PRIMARY KEY,
    trip_id VARCHAR,
    route_id VARCHAR,
    route_long_name VARCHAR,
    start_time VARCHAR,
    vehicle_trip_id VARCHAR,
    vehicle_timestamp TIMESTAMP,
    vehicle_id VARCHAR,
    current_status INTEGER,
    current_stop_id VARCHAR,
    speed DOUBLE PRECISION,
    odometer DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    bearing DOUBLE PRECISION,
    alert_id VARCHAR,
    alert_description TEXT,
    alert_cause INTEGER,
    alert_effect INTEGER,
    alert_url TEXT,
    alert_header_text TEXT[],
    alert_description_text TEXT[],
    alert_active_periods JSONB,
    alert_informed_entities JSONB,
    delay_minutes DOUBLE PRECISION,
    is_outlier BOOLEAN,
    processed_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (processed_at);

-- Create partitions (e.g., monthly)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'realtime_feed_2025_01') THEN
        EXECUTE 'CREATE TABLE realtime_feed_2025_01 PARTITION OF realtime_feed
                 FOR VALUES FROM (''2025-01-01'') TO (''2025-02-01'')';
    END IF;
    -- Repeat for other months as needed
END$$;
