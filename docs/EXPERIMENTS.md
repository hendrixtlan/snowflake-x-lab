# Extreme benchmark contracts

| Suite | Ground truth | Measurements | Failure criteria | Execution status |
|---|---|---|---|---|
| Streaming replay | exactly N distinct synthetic event IDs per tenant | commit equality, late count, duplicate rate, ingest-to-query p95 (cloud) | missing/duplicated canonical IDs | local simulation implemented, Snowpipe pending |
| Online features | known injected event and a feature key updated by it | p50/p95/p99 server + client, freshness and online/offline diff | stale values beyond target; mismatch | cloud gated |
| Two-tower | positive interactions held out per user | recall@10, NDCG@10, GPU walltime, cost | no improvement vs popularity | real local model implemented; GPU dispatch gated |
| Bandit | logged propensity with support | IPS/SNIPS, effective sample size, reward | support violations or low effective N | local LinUCB+estimators implemented |
| Multimodal | hand-labeled poster image / flyer / synthetic promo audio | Recall@K, calibrated labeling, groundedness | misclassification or hallucination | design/SQL only |
| Agent | authorized queries, forbidden synthetic cross-tenant canary | task completion, unauthorized tool calls, leak count, credits | any canary disclosure | local boundary stub implemented; live agent test gated |
| Resilience | injected restart, timeouts and backpressure | recovery time, loss/duplication, p99 | duplicate commits or lost offsets | partial replay injection; account chaos pending |

**Targets** in `configs/extreme.json` are hypotheses, not measured outcomes. Never compare local-simulation ingest delay to Snowpipe service latency.

## Highest-value advanced experiments

1. Same clickstream key via Snowpipe Streaming high-performance pipe vs Online Feature Store stream ingestion vs Dynamic Tables: time from producer timestamp to SQL visibility to online serving; quantify skew, caching, batching, cost and convergence.
2. GPU two-tower vs approximate-nearest-neighbor or Cortex Search retrieval: hold identical time splits and allowed candidate catalogs; evaluate quality/latency/cost; implement hard-negative mining.
3. Contextual bandit policy with logging propensities and inverse propensity off-policy evaluation; detect regressions during price drops or trend shifts.
4. Model rollback while requests are in flight; validate version pinning, feature compatibility, tail latency and user impact.
5. Adversarial code-execution-agent prompt injection with cross-tenant canary. Validate Snowflake RBAC, row access policies, Cortex Search security and application authorization under each role, not just LLM refusal.
6. Evaluation+optimization prompt/model Pareto frontier using Cortex AI Function experiments. Report ground-truth scores, tokens, dollars and repeat variance.

## Reproducibility / ethics

Store exact account region, Snowflake release, Snowflake ML Python version, compute family, warehouse size, model IDs, seed, dataset checksum, time window, retries, warmup, benchmark client location and concurrency. Synthetic data is the only default data source. GPU, Online Feature Store and Cortex are billable services; do not auto-enable in CI.
