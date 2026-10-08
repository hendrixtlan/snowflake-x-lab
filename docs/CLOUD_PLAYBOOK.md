# Snowflake account execution playbook (opt-in only)

**Do not confuse shipped code with executed Snowflake results.** No live Snowflake credentials are available inside this artifact-generation environment; cloud execution remains an integration exercise.

## Prerequisites

- Dedicated dev account or isolated database, named roles, grants and budget notifications; use no customer data.
- Configure `~/.snowflake/connections.toml` with `[xlab]` using federated identity or a key pair. Do not commit PATs, private keys, auth outputs or raw agent transcripts.
- Python 3.11+, `python -m pip install -e '.[dev,gpu,snowflake-ml,cloud]'` for workload dispatch. Ensure Snowflake GPU runtime has compatible PyTorch and approved package sources.
- Paid experiments are disabled by default. Set `XLAB_ACK_COST=YES` explicitly for each shell session only after reviewing object lifetime and billing.

## Correct sequence

1. `sql/01_setup.sql` (legacy source model), then `sql/extreme/00_bootstrap.sql`.
2. `sql/extreme/01_snowpipe_streaming.sql`; configure high-performance SDK using [Snowflake's Named Channels quickstart](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-getting-started). That SDK is **not bundled**. Benchmark commit offsets, duplicate replay, actual commit-to-query timestamps, and credits separately from local simulation.
3. `sql/extreme/02_dynamic_features.sql`. Confirm effective refresh mode and use EXPLAIN CHANGES before treating refresh as incremental.
4. Run `sql/extreme/07_data_access_policy.sql` to create a fail-closed principal-scoped secure view; seed principal mappings and only then attach the optional raw-table row policy after validation with two distinct Snowflake users. Never put tenant selection solely in model instructions.
5. `sql/extreme/03_semantic_view.sql`, `04_cortex_search.sql`, `05_cortex_agent.sql` (t1-scoped example only). Search indexes and agents incur charges; monitor service usage.
6. Complete versioned evaluation dataset and review `06_ai_function_eval.sql`, then manually run EXECUTE EXPERIMENT. A label dataset does not exist in the starter repo; this is deliberately not executed.
7. For Online Feature Store: an administrator first creates and grants least-privilege `XLAB_FS_PRODUCER` and `XLAB_FS_CONSUMER` roles. After confirming pricing, deploy a **t1-only batch-backed feature view** and billable online service. Snowflake currently documents public-preview Postgres serving and `OnlineConfig(enable=True, store_type=OnlineStoreType.POSTGRES)`. The following script **does** create the service and must never run unattended:

```bash
XLAB_ACK_COST=YES python workloads/provision_online_features.py \
  --producer-role XLAB_FS_PRODUCER --consumer-role XLAB_FS_CONSUMER --apply
```

Then benchmark its real SDK reads (this is a 1-minute offline refresh + 10-second sync path, **not** a sub-2-second stream source):

```bash
XLAB_ACK_COST=YES python workloads/benchmark_online_features.py \
  --feature-store XLAB_FS --feature-view T1_USER_ENGAGEMENT --user-id t1_u0 --apply
```

After the experiment, stop billing explicitly:

```bash
XLAB_ACK_COST=YES python workloads/provision_online_features.py \
  --producer-role XLAB_FS_PRODUCER --consumer-role XLAB_FS_CONSUMER \
  --destroy-online-service --apply
```

The separate under-two-second freshness experiment must create a stream feature view with `StreamConfig` + Snowflake's REST ingest source; it is **not implemented in this version**. Neither a cached batch feature nor 10-ms read claims are evidence of streaming freshness.

8. GPU training: provision a GPU compute pool yourself, with fixed maximum nodes and short autosuspend. Generate local test data before sending the repo payload:

```bash
music-lab generate
XLAB_ACK_COST=YES python workloads/submit_gpu_job.py \
  --pool XLAB_GPU_POOL --stage MUSIC_LAB.ML.PAYLOAD_STAGE --apply
```

This dispatches `workloads/gpu_train.py` with PyTorch; account/region/GPU image/package compatibility must be checked. It does not automatically register the trained model or publish a service. The local workload expects `data/listening_events.csv` to be present in its payload.

9. Agent red-team, **after seeding a synthetic forbidden canary in a separate tenant and setting up distinct caller roles**:

```bash
XLAB_ACK_COST=YES SNOWFLAKE_PAT='...' \
 python workloads/live_agent_redteam.py \
 --account-url https://your-account.snowflakecomputing.com --apply
```

No live redteam trial is valid without an account-level authorized dataset, actual user/role isolation and review of tool traces.

## Measuring real extremes

Use a dedicated load generator with concurrency levels 1, 10, 50, 100 and 1000 requests (where within account quotas). Warm up before recording p50/p95/p99, error/429 rates, bytes/s, freshness, credits and dollar estimates (using your region's contract rate). Compare both **SDK and direct REST endpoints**, avoiding apples-to-oranges latency claims. Store one JSON artifact per environment, configuration, model version, date, and run ID. Absent metrics must be marked `not_executed` rather than zero.

## Teardown

- Stop SDK producers; wait for committed source offsets.
- Suspend/drop agents, Cortex Search services, Dynamic Tables as appropriate.
- Call Feature Store `drop_online_service()` after testing; Online Feature Store may run continuously.
- Drop GPU compute pool/services after jobs complete; disable external access integrations.
- Confirm credit usage in Account Usage / Snowsight; avoid dropping user-owned production objects.
