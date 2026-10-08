# Snowflake X-LAB reference architecture

```mermaid
flowchart TD
    A[Event and ticket simulator] --> B[Snowpipe Streaming high-performance]
    A --> O[Online FS stream ingest API]
    B --> C[Raw events plus immutable event IDs]
    C --> D[Canonical dedup + Dynamic Tables]
    D --> E[Offline Feature Store]
    E --> G[Snowflake GPU ML Jobs]
    G --> H[Model Registry]
    H --> I[Model serving / Snowpark Container Services]
    O --> I
    D --> S[Native semantic view]
    D --> R[Cortex Search + multimodal enrichment]
    S --> J[Cortex Agent]
    R --> J
    J --> K[Sandboxed code execution]
    I --> T[Recommendation API]
    J --> T
    T --> Q[Benchmarks and observability]
    B --> Q
    G --> Q
```

## Data correctness and boundaries

Canonical event ID = (`tenant_id`, `event_id`), not Kafka offset. Source offsets are checkpointed only after Snowpipe commit confirmation. Do not drop late data without a defined watermark policy. Compare as-of point-in-time training features and versioned serving features; train/serve skew is a test failure.

Online Feature Store stream ingestion is **not** automatically equivalent to the Snowpipe Streaming SQL path. The two have distinct transports, semantics, latencies and pricing. Run them as parallel experimental arms before proposing a unified architecture.

Cortex Search indexes metadata and text; a hybrid search service is not a generic GPU vector-index benchmark. Multimodal processing requires separately staged assets, consent/licensing and model/region checks.

Every production tenant boundary must be protected in storage/query privileges and trusted API authorization; a model instruction is never a security boundary. Sandbox code execution has separate rights and does not implicitly read SQL itself.
