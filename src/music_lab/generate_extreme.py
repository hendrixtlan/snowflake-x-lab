"""Synthetic multi-tenant, seasonal-drift music/ticket stream, no real customer data."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd

GENRES = ["electronic", "jazz", "latin", "ambient", "rock", "classical"]


def generate_extreme(out: str = "data/extreme", n_events: int = 30000, n_users: int = 500,
                     n_items: int = 300, tenants: int = 3, seed: int = 42) -> dict:
    if min(n_events, n_users, n_items, tenants) < 1:
        raise ValueError("positive dataset sizes are required")
    if n_events > 1_000_000:
        raise ValueError("cap at one million generated events per invocation")
    root = Path(out)
    root.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    catalog = []
    for t in range(tenants):
        for i in range(n_items):
            cat = GENRES[i % len(GENRES)]
            catalog.append({"tenant_id": f"t{t+1}", "content_id": f"item-{i}",
                            "title": f"Synthetic {cat} Event {i}", "genre": cat,
                            "description": f"Synthetic event {i} featuring {cat}, live music and tickets",
                            "base_price": round(float(rng.uniform(20, 160)), 2)})
    pd.DataFrame(catalog).to_csv(root / "catalog.csv", index=False)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    output = root / "stream_events.jsonl"
    digest = hashlib.sha256()
    count_type = {"listen": 0, "ticket_view": 0, "ticket_purchase": 0, "skip": 0}
    with output.open("w", encoding="utf8") as f:
        for i in range(n_events):
            tenant = f"t{1 + i % tenants}"
            uid = f"{tenant}_u{int(rng.integers(n_users))}"
            item = int(rng.integers(n_items))
            genre = GENRES[item % len(GENRES)]
            seasonal = (i / n_events) > .7
            # Introduce temporal distribution shift after 70% of stream.
            p_purchase = .04 + (.12 if seasonal and genre == "latin" else 0)
            event_type = str(rng.choice(["listen", "ticket_view", "ticket_purchase", "skip"],
                       p=[.58-p_purchase, .34, p_purchase, .08]))
            count_type[event_type] += 1
            event = {"tenant_id": tenant, "event_id": f"event-{i}",
                     "user_id": uid, "content_id": f"item-{item}",
                     "event_ts": (start + timedelta(milliseconds=i*100)).strftime("%Y-%m-%dT%H:%M:%S.%f"),
                     "event_type": event_type,
                     "completion_rate": round(float(rng.beta(3, 2) if event_type == "listen" else 0), 4)}
            line = json.dumps(event, separators=(",", ":")) + "\n"
            digest.update(line.encode())
            f.write(line)
    meta = {"environment": "synthetic_data", "n_events": n_events, "users_per_tenant": n_users,
            "items_per_tenant": n_items, "tenants": tenants, "seed": seed,
            "distribution_shift": "latin ticket purchase rate increased after 70%", "event_types": count_type,
            "sha256_stream_events": digest.hexdigest()}
    (root / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
    return meta


if __name__ == "__main__":
    print(json.dumps(generate_extreme(), indent=2))
