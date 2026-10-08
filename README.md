# SNOWFLAKE X-LAB — Extreme AI, Streaming, GPUs, Agents, Resilience

**2026-10-07. Experimental research repo v0.2.0, not a finished production service.** A continuation of the original Snowflake AI & Data Science Lab, rebuilt to test meaningful technical limits rather than standard CRUD/BI examples.

> **Integrity ledger:** The local experiments (event replay, LinUCB, propensity estimators, top-K popularity, PyTorch two-tower, permission stubs, tests) are implemented and run locally. The account-backed SQL, Online Feature Store SDK probe, ML Jobs submission and live Cortex red-team launchers are shipped but **NOT executed against Snowflake**. Do not interpret simulation scores as live Snowflake latency, quality or cost.

## Why this lab exists

One synthetic, tenant-partitioned entertainment marketplace produces high-rate listening, view, skip and ticket purchase events under deliberate seasonal drift. It drives a unified benchmark matrix:

1. **Snowpipe Streaming high-performance**: test replay, duplicate delivery, commit offset correctness, cold starts and credit cost.
2. **Dynamic Tables**: measure lag, effective incremental refresh, data skew and replay consistency.
3. **Online Feature Store (Postgres, 2026 public preview)**: benchmark serving p50/p95/p99, freshness, and online/offline skew.
4. **GPU ML Jobs and two-tower retrieval**: train in a dedicated GPU pool, compare against a top-K popularity baseline, measure speed, loss and economics.
5. **Contextual bandits**: implement LinUCB with a reproducible simulation plus IPS/SNIPS estimators on correctly logged propensities.
6. **tenant-scoped Cortex Search + authorization-backed semantic views + Cortex Agents**: build hybrid retrieval/analytics with a sandboxed Python tool and evidence-based explanations.
7. **Cortex AI Function Evaluation**: version labeled datasets, compare model/prompt quality and token consumption.
8. **Adversarial and chaos experiments**: replay anomalies, model/feature staleness, cross-tenant canary attempts and rollback rehearsals.

Measured local evidence: [`docs/LOCAL_EVIDENCE.md`](docs/LOCAL_EVIDENCE.md), with JSON artifacts in [`evidence/local/`](evidence/local/).

Full experiment manifest: [`experiments/manifest.yml`](experiments/manifest.yml). Engineering contracts: [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md). Cloud procedure: [`docs/CLOUD_PLAYBOOK.md`](docs/CLOUD_PLAYBOOK.md). Current feature status: [`docs/FEATURE_STATUS_2026-10-07.md`](docs/FEATURE_STATUS_2026-10-07.md).

## Quickstart — real local code, no Snowflake charges

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest -q
music-lab generate
xlab stream-sim --events 100000 --output results/stream.json
xlab ranking --output results/ranking.json
xlab bandit-sim --rounds 3000 --output results/bandit.json
xlab redteam-local --output results/redteam.json
```

For the real PyTorch dual-embedding tower (CPU or CUDA GPU):

```bash
python -m pip install -e '.[gpu]'
xlab two-tower --epochs 6 --device auto --output results/two_tower.json
```

Generate multi-tenant JSONL events for Snowpipe Streaming (synthetic only):

```bash
python -c "from music_lab.generate_extreme import generate_extreme; print(generate_extreme())"
```

All output artifacts report their environment; benchmark targets in `configs/extreme.json` **are not achieved numbers**.

## Live Snowflake experiments (paid, manually authorized)

Never configure automatic cloud deployment in PR CI. Create a named connection `xlab` under `~/.snowflake/connections.toml`, use a dedicated role, approve your account's network/region permissions, and place budget/credit guardrails before provisioning GPU pools and online services. `docs/CLOUD_PLAYBOOK.md` gives the precise order.

```bash
python -m pip install -e '.[snowflake-ml,cloud]'
# After account config and explicit approval:
XLAB_ACK_COST=YES xlab probe-snowflake --repeats 20 --apply
```

The opt-in feature provisioning script can register a t1-only Postgres online feature view and creates a continuously billed online service; a separate feature read client measures real SDK latency. The GPU job submission requires a pre-provisioned GPU pool and pre-provisioned stage. Neither script silently creates expensive infrastructure.

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the Mermaid diagram and security boundaries.

```text
synthetic producer ─> high-performance Snowpipe ─> raw event log
                                         │
                                 canonical Dynamic Tables
                                         │
                       Offline FS ── GPU ML Jobs ── Registry ── Serving
                                         │                     ↑
                       Online FS stream/REST ──────────────────┘
                                         │
                semantic views + Cortex Search ── Cortex Agent + Python tool
                                         │
                         trace/eval/latency/cost/attack-score artifacts
```

## Research rigor and limitations

- Relative vendor claims (such as 10-ms p50 reads) are independently measured, never assumed.
- Current top-K holdout excludes a user's last positive; global popularity can still leak other users' future behavior, explicitly documented. Full time-sliced candidate snapshots are next.
- The two-tower model uses **real PyTorch BPR training**, but negative sampling is implicit and results on synthetic preference labels are not evidence of production recommendation quality. Models are not yet registered.
- The local red-team checks are an **authorization stub**, not a successful Cortex pentest. Live SQL roles, Search filtering and code-tool traces need tests with two genuinely separate tenant identities.
- Multimodal image/audio ingestion is defined as an experiment but **not implemented** in this version; it needs licensed/sample assets and approved Cortex models.
- At this stage, live performance numbers, service costs and resilience thresholds are **unknown**. README does not fabricate them.

## Repository contents

- `src/music_lab/` baseline model, local load simulator, bandit, ranking, GPU-capable PyTorch trainer, security test fixtures, live SQL latency probe
- `workloads/` gated Snowflake GPU job submission, Postgres Online Feature Store provisioning and SDK benchmark, Cortex Agent live canary test
- `sql/extreme/` streaming pipe, Dynamic Tables, native semantic view, Cortex Search, secure agent, AI Function evaluation, row policy
- `configs/` goals **not** results; `experiments/` manifest tracking implemented vs gated work
- `tests/` deterministic offline CI; `.github/workflows/` cloud-secret-free tests
- `docs/` setup and test contracts, architecture, feature status and limitations

Snowflake documentation is linked in [`docs/FEATURE_STATUS_2026-10-07.md`](docs/FEATURE_STATUS_2026-10-07.md). This is a technical portfolio research lab, not a promise of production-readiness.
