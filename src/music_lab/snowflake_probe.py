"""Actual account-backed SQL query latency sampler. Disabled by default, never an ingestion claim."""
from __future__ import annotations
import os
from time import perf_counter
from .metrics import latency_summary


def probe_sql(query: str, repeats: int, acknowledge: bool) -> dict:
    if not acknowledge or os.environ.get("XLAB_ACK_COST") != "YES":
        raise PermissionError("Cloud run requires --apply and XLAB_ACK_COST=YES")
    if repeats <= 0 or repeats > 500:
        raise ValueError("repeats must be 1..500")
    try:
        import snowflake.connector
    except ImportError as e:
        raise RuntimeError("Install snowflake-connector-python") from e
    if query.strip().upper() not in {"SELECT 1", "SELECT CURRENT_TIMESTAMP()"}:
        raise ValueError("Probe permits only documented allowlisted read-only queries")
    conn_name = os.environ.get("SNOWFLAKE_CONNECTION_NAME", "xlab")
    durations = []
    with snowflake.connector.connect(connection_name=conn_name, session_parameters={"QUERY_TAG": "SNOWFLAKE_XLAB_LATENCY"}) as con:
        with con.cursor() as cur:
            for _ in range(repeats):
                start = perf_counter()
                cur.execute(query)
                cur.fetchall()
                durations.append((perf_counter() - start) * 1000)
    return {"environment": "live_snowflake", "query": query, "connection_name": conn_name,
            "warning": "Client end-to-end query latency, NOT Snowflake Online Feature Store REST latency.",
            **latency_summary(durations)}
