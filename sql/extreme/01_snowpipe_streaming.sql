-- LIVE: high-performance Snowpipe Streaming ingestion pipe.
-- Official SDK or REST POSTs rows to this PIPE; creating a PIPE alone does not produce data.
CREATE TABLE IF NOT EXISTS MUSIC_LAB.STREAM.EVENTS (
  TENANT_ID VARCHAR NOT NULL,
  EVENT_ID VARCHAR NOT NULL,
  USER_ID VARCHAR NOT NULL,
  CONTENT_ID VARCHAR NOT NULL,
  EVENT_TS TIMESTAMP_NTZ,
  EVENT_TYPE VARCHAR,
  COMPLETION_RATE FLOAT
);
CREATE OR REPLACE PIPE MUSIC_LAB.STREAM.EVENTS_PIPE AS
  COPY INTO MUSIC_LAB.STREAM.EVENTS
       (TENANT_ID, EVENT_ID, USER_ID, CONTENT_ID, EVENT_TS, EVENT_TYPE, COMPLETION_RATE)
  FROM (
    SELECT $1:tenant_id::VARCHAR, $1:event_id::VARCHAR,
           $1:user_id::VARCHAR, $1:content_id::VARCHAR,
           TRY_TO_TIMESTAMP_NTZ($1:event_ts::VARCHAR),
           $1:event_type::VARCHAR, TRY_TO_DOUBLE($1:completion_rate::VARCHAR)
    FROM TABLE(DATA_SOURCE(TYPE => 'STREAMING'))
  );
-- Do not assume exactly once or on-time delivery. Replay tests enforce source checkpoints.
-- Use METADATA$ROW_LAST_COMMIT_TIME for ingest-commit timing where supported,
-- not CURRENT_TIMESTAMP in the pipe (can be compiled once for long-lived streams).
