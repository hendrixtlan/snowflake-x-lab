"""Live Online Feature Store SDK read latency. Explicit opt-in and cloud environment."""
from __future__ import annotations
import argparse
import json
import os
from time import perf_counter
from music_lab.metrics import latency_summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--database", default="MUSIC_LAB")
    p.add_argument("--feature-store", required=True)
    p.add_argument("--warehouse", default="MUSIC_LAB_XS")
    p.add_argument("--feature-view", required=True)
    p.add_argument("--version", default="V1")
    p.add_argument("--user-id", required=True, help="Example: t1_u0. Must belong to the isolated tenant.")
    p.add_argument("--warmup", type=int, default=10)
    p.add_argument("--repeats", type=int, default=100)
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    if not args.apply or os.environ.get("XLAB_ACK_COST") != "YES":
        print("DRY RUN - no online service contacted. --apply and XLAB_ACK_COST=YES required.")
        return
    if not 0 <= args.warmup <= 1000 or not 1 <= args.repeats <= 5000:
        raise ValueError("Invalid sample count")
    from snowflake.snowpark import Session
    from snowflake.ml.feature_store import FeatureStore, CreationMode
    session = Session.builder.config("connection_name", os.getenv("SNOWFLAKE_CONNECTION_NAME", "xlab")).create()
    fs = None
    try:
        fs = FeatureStore(session=session, database=args.database, name=args.feature_store,
                          default_warehouse=args.warehouse, creation_mode=CreationMode.FAIL_IF_NOT_EXIST)
        fv = fs.get_feature_view(args.feature_view, args.version)
        delays = []
        for i in range(args.warmup + args.repeats):
            t0 = perf_counter()
            df = fs.read_feature_view(fv, keys=[[args.user_id]], store_type="online")
            _ = df.collect() if hasattr(df, "collect") else df
            if i >= args.warmup:
                delays.append((perf_counter() - t0) * 1000)
        print(json.dumps({"environment": "live_snowflake_online_feature_store_sdk", "method": "sdk_read_feature_view",
                          "feature_view": args.feature_view, "warmup": args.warmup,
                          "warning": "SDK client round-trip, NOT REST server-only latency; separately test ingest-to-feature freshness.",
                          **latency_summary(delays)}, indent=2))
    finally:
        if fs is not None:
            if hasattr(fs, "close"):
                fs.close()
        session.close()


if __name__ == "__main__":
    main()
