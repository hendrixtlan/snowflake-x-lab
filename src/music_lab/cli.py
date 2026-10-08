import argparse
import json
from pathlib import Path
import pandas as pd
from .generate import generate
from .model import train_evaluate


def main():
    parser = argparse.ArgumentParser(description="Music recommendation lab")
    sub = parser.add_subparsers(dest="command", required=True)
    p_gen = sub.add_parser("generate")
    p_gen.add_argument("--out", default="data")
    p_gen.add_argument("--events", type=int, default=12000)
    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--data", default="data")
    args = parser.parse_args()
    if args.command == "generate":
        print(json.dumps({k: str(v) for k, v in generate(out=args.out, events=args.events).items()}, indent=2))
    elif args.command == "evaluate":
        base = Path(args.data)
        tables = [pd.read_csv(base / f"{name}.csv") for name in ("listening_events", "users", "tracks")]
        print(json.dumps(train_evaluate(*tables), indent=2))

if __name__ == "__main__":
    main()
