"""Snowflake ML Jobs GPU dispatch. Cost-bearing, account-gated, never runs by default."""
import argparse
import os
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description="Submit the bundled training workload to a Snowflake GPU compute pool")
    p.add_argument("--pool", required=True, help="Pre-provisioned dedicated GPU compute pool")
    p.add_argument("--stage", required=True, help="Pre-provisioned stage e.g. MUSIC_LAB.ML.PAYLOAD_STAGE")
    p.add_argument("--apply", action="store_true", help="Submit the paid job")
    args = p.parse_args()
    if not args.apply or os.getenv("XLAB_ACK_COST") != "YES":
        print("DRY RUN: requires --apply and XLAB_ACK_COST=YES. Pool:", args.pool, "Stage:", args.stage)
        return
    from snowflake.snowpark import Session
    from snowflake.ml.jobs import submit_directory
    repo = Path(__file__).resolve().parents[1]
    if not (repo / "data/listening_events.csv").exists():
        raise FileNotFoundError("Generate data first: music-lab generate")
    session = Session.builder.config("connection_name", os.getenv("SNOWFLAKE_CONNECTION_NAME", "xlab")).create()
    try:
        job = submit_directory(
            str(repo), args.pool, entrypoint="workloads/gpu_train.py", stage_name=args.stage,
            args=["--data", "data/listening_events.csv", "--device", "cuda", "--epochs", "12"],
            pip_requirements=["numpy>=1.26,<3", "pandas>=2.2,<3", "torch>=2.2,<3"],
            session=session,
        )
        print("Submitted ML Job:", job)
        print("Inspect job metrics, GPU utilization and cost in Snowsight. No completion implied.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
