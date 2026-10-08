"""Generate deterministic, synthetic event data (not real listeners)."""
from pathlib import Path
import numpy as np
import pandas as pd

GENRES = ["electronic", "jazz", "rock", "pop", "hiphop", "classical", "latin", "ambient"]


def generate(out: str = "data", users: int = 250, tracks: int = 120, events: int = 12000, seed: int = 42) -> dict[str, Path]:
    if min(users, tracks, events) <= 0:
        raise ValueError("users, tracks and events must be positive")
    rng = np.random.default_rng(seed)
    folder = Path(out)
    folder.mkdir(parents=True, exist_ok=True)
    user_pref = rng.integers(0, len(GENRES), users)
    track_genre = rng.integers(0, len(GENRES), tracks)
    track_ids = rng.integers(0, tracks, events)
    user_ids = rng.integers(0, users, events)
    match = user_pref[user_ids] == track_genre[track_ids]
    completion = np.clip(rng.beta(2, 2, events) + 0.35 * match - 0.15 * (~match), 0, 1)
    skip = (completion < 0.25).astype(int)
    times = pd.Timestamp("2026-01-01") + pd.to_timedelta(rng.integers(0, 90 * 86400, events), unit="s")
    catalog = pd.DataFrame({"track_id": np.arange(tracks), "title": [f"Synthetic Track {i}" for i in range(tracks)], "genre": [GENRES[g] for g in track_genre]})
    profiles = pd.DataFrame({"user_id": np.arange(users), "preferred_genre": [GENRES[g] for g in user_pref]})
    listens = pd.DataFrame({"event_id": np.arange(events), "user_id": user_ids, "track_id": track_ids, "played_at": times, "completion_rate": completion.round(4), "skipped": skip})
    paths = {"tracks": folder / "tracks.csv", "users": folder / "users.csv", "listening_events": folder / "listening_events.csv"}
    catalog.to_csv(paths["tracks"], index=False)
    profiles.to_csv(paths["users"], index=False)
    listens.sort_values(["played_at", "event_id"]).to_csv(paths["listening_events"], index=False)
    return paths
