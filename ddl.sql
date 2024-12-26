CREATE TABLE market_news(
    id BIGINT,
    author VARCHAR,
    headline VARCHAR,
    source VARCHAR,
    summary VARCHAR,
    data_provider VARCHAR,
    `url` VARCHAR,
    symbol VARCHAR,
    sentiment VARCHAR,
    timestamp_ms BIGINT,
    event_time AS TO_TIMESTAMP_LTZ(timestamp_ms, 3),
    WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'market-news',
    'properties.bootstrap.servers' = 'redpanda-1:29092, redpanda-2:29093'
    'properties.group.id' = 'market-news-group',
    'properties.auto.offset.reset' = 'earliest'
    'format' = 'json'
);
