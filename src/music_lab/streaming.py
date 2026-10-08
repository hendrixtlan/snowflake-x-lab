"""Fault-injected, bounded-memory replay benchmark; local simulation, NOT Snowpipe performance."""
from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
from time import perf_counter
import random
from .metrics import latency_summary


@dataclass(frozen=True)
class Event:
    tenant_id: str
    event_id: str
    user_id: int
    event_ms: int
    ingest_ms: int
    positive: bool = True


class ExactlyOnceState:
    """In-memory logical idempotency and late-event accounting for one replay run."""
    def __init__(self, allowed_lateness_ms: int = 2000):
        self.seen: set[tuple[str, str]] = set()
        self.counts: dict[tuple[str, int], int] = defaultdict(int)
        self.duplicates = 0
        self.late = 0
        self.max_event_ms = -1
        self.allowed_lateness_ms = allowed_lateness_ms
        self.accepted = 0

    def apply(self, event: Event) -> bool:
        key = (event.tenant_id, event.event_id)
        if key in self.seen:
            self.duplicates += 1
            return False
        self.seen.add(key)
        if self.max_event_ms >= 0 and event.event_ms < self.max_event_ms - self.allowed_lateness_ms:
            self.late += 1
        self.max_event_ms = max(self.max_event_ms, event.event_ms)
        self.counts[(event.tenant_id, event.user_id)] += int(event.positive)
        self.accepted += 1
        return True


def make_events(n: int, seed: int = 42, duplicate_probability: float = .03,
                disorder_ms: int = 3000) -> list[Event]:
    if n <= 0 or not 0 <= duplicate_probability <= 1 or disorder_ms < 0:
        raise ValueError("invalid event generation parameters")
    rng = random.Random(seed)
    output = []
    for i in range(n):
        tenant = f"t{(i % 3) + 1}"
        source_time = i * 10
        jitter = rng.randint(-disorder_ms, disorder_ms)
        output.append(Event(tenant, f"evt-{i}", i % 113, source_time, max(0, source_time + jitter)))
        if rng.random() < duplicate_probability:
            output.append(output[-1])
    output.sort(key=lambda x: x.ingest_ms)
    return output


def benchmark(n: int = 10000, seed: int = 42) -> dict:
    events = make_events(n, seed)
    state = ExactlyOnceState()
    latencies = []
    t0 = perf_counter()
    for event in events:
        if state.apply(event):
            latencies.append(max(0, event.ingest_ms - event.event_ms))
    elapsed = perf_counter() - t0
    assert state.accepted == n, "missing logical events after replay"
    return {"environment": "local_simulation_not_snowflake", "unique_input_events": n,
            "delivered_events": len(events), "committed_once": state.accepted,
            "deduplicated": state.duplicates, "late_arrivals": state.late,
            "injection_delay_ms": latency_summary(latencies),
            "simulation_events_per_s": round(len(events) / max(elapsed, 1e-9), 1),
            "warning": "Injection delay and local CPU throughput are NOT Snowpipe ingest-to-query or serving metrics."}
