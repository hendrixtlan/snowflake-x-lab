# Delivery roadmap

## Milestone 1 — Local reproducible baseline (implemented)
Synthetic event generator, chronological evaluation, SQL bootstrap, SQL data quality, CI.

## Milestone 2 — Snowflake data platform
Automated stage upload via Snowflake CLI, idempotent MERGE ingestion, dynamic tables, incremental transformations, Snowpark feature equivalence, query profiling. Add integration tests run against a dedicated test database.

## Milestone 3 — Snowflake ML
Create feature views with point-in-time correctness, add ML Job training, log candidate models and metrics to Model Registry, implement proper ranking candidate generation, Recall@K/NDCG@K, and user-level cold-start tests.

## Milestone 4 — Real-time and observability
Investigate online feature serving (preview), serving latency, retraining triggers, model monitoring and drift. Always compare against offline baseline.

## Milestone 5 — Cortex AI and agents
Ingest song descriptions/metadata, deploy Cortex Search, configure semantic views and Cortex Agent tools, evaluate response grounding and SQL correctness, add least-privilege read-only tools. Test analytical search only if feature available and approved.

## Milestone 6 — Production disciplines
Terraform or verified Snowflake CLI IaC, environment promotion, RBAC, access reviews, cost budgets, masked test data, dashboards, rollback and release checks.

## Benchmark gates
Log dataset size, query runtime, warehouse size, credit consumption, ML ranking metrics, inference p50/p95 latency, feature freshness, and LLM grounding scores. No unmeasured 'better' claims.
