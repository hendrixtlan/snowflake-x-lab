# Local experiment evidence — 2026-10-07 (Mexico City)

These results were generated locally in a container, **NOT** against a Snowflake account. The evidence JSON files under `evidence/local/` include precise UTC execution timestamps and test parameters; see `experiments/manifest.yml` for feature-level run status.

| Local experiment | Observed measurement | Interpretation |
|---|---:|---|
| Injected streaming replay | 100,000 unique simulated source events | Local fault-injection model, **not Snowpipe Streaming** |
| Replay deduplication | 3,063 duplicate deliveries rejected | Exactly-once state *simulated* in Python |
| Replay loop speed | 1,273,538 simulated events/s | Local Python loop throughput, **not cloud ingest performance** |
| Popularity top-10 Recall@K | 0.1019 | Simple baseline on synthetic interactions |
| PyTorch two-tower Recall@K | 0.0971 | CPU run (4 epochs); **worse than baseline in this run** |
| PyTorch two-tower NDCG@K | 0.0463 | Requires tuning, hard negatives, better time splits |
| Contextual bandit mean reward | 0.6363 | Synthetic environment, 3,000 decisions |
| Local security checks | 4/4 passing | Local policy stub, **not live Cortex red-team** |

**Unmeasured:** Snowflake p50/p95/p99, online freshness, GPU device use in Snowflake, GPU cost, agent success, live tenant isolation, stream ingest-to-query time, actual service credits. None are assigned scores or passed status.

The baseline results are intentionally not curated to make the neural model look better. The two-tower candidate currently trails the simple baseline; model work remains open. This is an evidence-led research repo, not a marketing benchmark.

Run tests locally with `PYTHONPATH=src pytest -q` or install `-e '.[dev]'` in a network-enabled environment and use `pytest -q`. The build environment cannot reach Python package indexes, so editable-install CI behavior could not be directly verified here; syntax, direct Python module execution, and eight tests were verified.
