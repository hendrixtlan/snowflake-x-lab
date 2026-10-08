"""Time-aware implicit-feedback retrieval benchmark with a popularity baseline."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .metrics import ranking_scores


def split_interactions(events: pd.DataFrame, min_history: int = 3):
    """Leave-last-positive-out per user; no future interactions used in candidate ranking."""
    df = events.sort_values(["played_at", "event_id"]).copy()
    positives = df.loc[(df["completion_rate"] >= .75) & (df["skipped"] == 0)].copy()
    groups = positives.groupby("user_id")
    enough = groups["track_id"].transform("size") >= min_history
    positives = positives.loc[enough]
    positives = positives.drop_duplicates(subset=["user_id", "track_id"], keep="first")
    counts = positives.groupby("user_id")["track_id"].transform("size")
    positives = positives.loc[counts >= min_history]
    test = positives.groupby("user_id", sort=False).tail(1)
    train = positives.drop(test.index)
    if train.empty or test.empty:
        raise ValueError("insufficient positive user histories")
    return train, test


def popularity_benchmark(events: pd.DataFrame, k: int = 10) -> dict:
    train, test = split_interactions(events)
    universe = sorted(events.track_id.unique().tolist())
    pop = train.groupby("track_id").size().sort_values(ascending=False)
    order = list(pop.index) + [t for t in universe if t not in pop.index]
    hist = train.groupby("user_id")["track_id"].apply(set).to_dict()
    expected = test.groupby("user_id")["track_id"].apply(set).to_dict()
    rankings = {int(u): [int(t) for t in order if t not in hist[u]][:k] for u in expected}
    score = ranking_scores(expected, rankings, k)
    return {"model": "popularity_without_seen_items", "holdout": "leave_last_positive_per_user",
            "caution": "Global popularity aggregates other users beyond each target user's holdout timestamp; use true as-of snapshots for strict production temporal evaluation.",
            "k": k, **score}
