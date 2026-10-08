"""Ranking and latency metrics. All functions are deterministic, with explicit definitions."""
from __future__ import annotations
import math
import numpy as np


def latency_summary(milliseconds: list[float]) -> dict:
    if not milliseconds:
        raise ValueError("no latency samples")
    a = np.asarray(milliseconds, dtype=float)
    if np.any(~np.isfinite(a)) or np.any(a < 0):
        raise ValueError("latency values must be finite and non-negative")
    return {"count": len(a), "p50_ms": round(float(np.percentile(a, 50)), 3),
            "p95_ms": round(float(np.percentile(a, 95)), 3),
            "p99_ms": round(float(np.percentile(a, 99)), 3),
            "max_ms": round(float(np.max(a)), 3)}


def ranking_scores(actual: dict[int, set[int]], ranked: dict[int, list[int]], k: int = 10) -> dict:
    """Macro recall@K, NDCG@K and catalog coverage; no empty-target users in denominator."""
    if k < 1:
        raise ValueError("k must be positive")
    recalls, ndcgs, found = [], [], set()
    for user, positives in actual.items():
        if not positives:
            continue
        recs = list(dict.fromkeys(ranked.get(user, [])[:k]))
        found.update(recs)
        hits = sum(item in positives for item in recs)
        recalls.append(hits / len(positives))
        gain = sum((1.0 / math.log2(i + 2)) for i, item in enumerate(recs) if item in positives)
        ideal = sum(1.0 / math.log2(i + 2) for i in range(min(k, len(positives))))
        ndcgs.append(gain / ideal)
    if not recalls:
        raise ValueError("no ground truth users")
    return {"users": len(recalls), "recall_at_k": round(float(np.mean(recalls)), 5),
            "ndcg_at_k": round(float(np.mean(ndcgs)), 5), "unique_items_recommended": len(found)}


def bootstrap_mean_ci(samples: list[float], seed: int = 42, n: int = 500, alpha: float = 0.05) -> list[float]:
    if not samples or n <= 0 or not 0 < alpha < 1:
        raise ValueError("invalid bootstrap configuration")
    x = np.asarray(samples, dtype=float)
    rng = np.random.default_rng(seed)
    boot = rng.choice(x, (n, len(x)), replace=True).mean(axis=1)
    return [round(float(v), 5) for v in np.quantile(boot, [alpha / 2, 1 - alpha / 2])]
