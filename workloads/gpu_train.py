"""Entrypoint for Snowflake ML Jobs or compatible containers.

This is an ACTUAL executable PyTorch training workload. The Snowflake ML Jobs
SUBMISSION step is gated and documented in docs/CLOUD_PLAYBOOK.md; never claim
that running this locally constitutes a Snowflake GPU workload.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd
from music_lab.two_tower import train_two_tower


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/listening_events.csv")
    p.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    p.add_argument("--epochs", type=int, default=10)
    p.add_argument("--output", default="results/two_tower.json")
    args = p.parse_args()
    result = train_two_tower(pd.read_csv(args.data), epochs=args.epochs, device=args.device)
    dst = Path(args.output)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(result, indent=2) + "\n")
    print(dst, result["device"], result["ndcg_at_k"])


if __name__ == "__main__":
    main()
