"""Reproducible experiment entry point; cloud actions require a separate explicit consent flag."""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from .streaming import benchmark
from .bandit import simulate
from .security import run_boundary_suite
from .ranking import popularity_benchmark
from .metrics import latency_summary


def main():
    p = argparse.ArgumentParser(prog="xlab", description="Snowflake X-LAB stress and model experiments")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("stream-sim", help="Local fault injection; NOT Snowpipe latency")
    s.add_argument("--events", type=int, default=10000)
    b = sub.add_parser("bandit-sim")
    b.add_argument("--rounds", type=int, default=3000)
    sub.add_parser("redteam-local")
    for c in ("ranking", "two-tower"):
        t = sub.add_parser(c)
        t.add_argument("--data", default="data")
        t.add_argument("--k", type=int, default=10)
        if c == "two-tower":
            t.add_argument("--epochs", type=int, default=4)
            t.add_argument("--device", choices=["cpu", "cuda", "auto"], default="auto")
    cloud = sub.add_parser("probe-snowflake", help="Actual SQL round trip with explicit cost acknowledgment")
    cloud.add_argument("--query", choices=["SELECT 1", "SELECT CURRENT_TIMESTAMP()"], default="SELECT 1")
    cloud.add_argument("--repeats", type=int, default=20)
    cloud.add_argument("--apply", action="store_true")
    for child in (s, b, cloud, *[sub.choices[k] for k in ("redteam-local", "ranking", "two-tower")]):
        child.add_argument("--output", type=str, help="Optional JSON artifact path")
    args = p.parse_args()
    if args.command == "stream-sim":
        result = benchmark(args.events)
    elif args.command == "bandit-sim":
        result = simulate(args.rounds)
    elif args.command == "redteam-local":
        result = run_boundary_suite()
    elif args.command in {"ranking", "two-tower"}:
        path = Path(args.data) / "listening_events.csv"
        events = pd.read_csv(path)
        if args.command == "ranking":
            result = popularity_benchmark(events, args.k)
        else:
            from .two_tower import train_two_tower
            result = train_two_tower(events, epochs=args.epochs, device=args.device, k=args.k)
    else:
        from .snowflake_probe import probe_sql
        result = probe_sql(args.query, args.repeats, args.apply)
    artifact = {"executed_at_utc": datetime.now(timezone.utc).isoformat(), "experiment": args.command, "result": result}
    payload = json.dumps(artifact, indent=2)
    if args.output:
        dest = Path(args.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(payload + "\n", encoding="utf8")
        print(f"Wrote {dest}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
