import pandas as pd
from music_lab.generate import generate
from music_lab.model import features, train_evaluate


def test_generation_and_ml(tmp_path):
    paths = generate(str(tmp_path), users=40, tracks=25, events=600, seed=7)
    assert all(p.exists() for p in paths.values())
    data = {k: pd.read_csv(p) for k, p in paths.items()}
    assert len(data["listening_events"]) == 600
    assert data["listening_events"].completion_rate.between(0, 1).all()
    score = train_evaluate(data["listening_events"], data["users"], data["tracks"])
    assert score["rows"] == 600
    assert 0 <= score["model"]["log_loss"]


def test_prior_counts_do_not_use_future_events(tmp_path):
    paths = generate(str(tmp_path), users=30, tracks=15, events=250, seed=9)
    data = {k: pd.read_csv(p) for k, p in paths.items()}
    df = features(data["listening_events"], data["users"], data["tracks"])
    assert (df["previous_user_plays"] >= 0).all()
    assert (df["previous_track_plays"] >= 0).all()
    assert df.groupby("user_id")["previous_user_plays"].first().eq(0).all()
