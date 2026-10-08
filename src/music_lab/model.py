"""Local baseline and time-ordered holdout evaluation (no future-feature leakage)."""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, log_loss
from sklearn.ensemble import HistGradientBoostingClassifier


def features(events: pd.DataFrame, users: pd.DataFrame, tracks: pd.DataFrame) -> pd.DataFrame:
    df = events.merge(users, on="user_id", validate="many_to_one").merge(tracks, on="track_id", validate="many_to_one")
    df = df.sort_values(["played_at", "event_id"]).reset_index(drop=True)
    df["genre_match"] = (df["preferred_genre"] == df["genre"]).astype(int)
    df["hour"] = pd.to_datetime(df["played_at"]).dt.hour
    df["day_of_week"] = pd.to_datetime(df["played_at"]).dt.dayofweek
    df["previous_user_plays"] = df.groupby("user_id").cumcount()
    df["previous_track_plays"] = df.groupby("track_id").cumcount()
    df["completed"] = (df["completion_rate"] >= 0.75).astype(int)
    return df


def train_evaluate(events: pd.DataFrame, users: pd.DataFrame, tracks: pd.DataFrame) -> dict:
    df = features(events, users, tracks)
    cut = int(len(df) * 0.8)
    if cut < 20 or len(df) - cut < 2:
        raise ValueError("At least 25 listening events are required")
    cols = ["genre_match", "hour", "day_of_week", "previous_user_plays", "previous_track_plays"]
    xtrain, xtest = df.iloc[:cut][cols], df.iloc[cut:][cols]
    ytrain, ytest = df.iloc[:cut]["completed"], df.iloc[cut:]["completed"]
    if ytrain.nunique() < 2:
        raise ValueError("Training data must contain both target classes")
    model = HistGradientBoostingClassifier(max_iter=90, max_leaf_nodes=12, random_state=42)
    model.fit(xtrain, ytrain)
    pred = model.predict_proba(xtest)[:, 1]
    baseline = np.repeat(float(ytrain.mean()), len(ytest))
    def scores(proba):
        result = {"log_loss": round(float(log_loss(ytest, proba, labels=[0, 1])), 5)}
        result["roc_auc"] = round(float(roc_auc_score(ytest, proba)), 5) if ytest.nunique() == 2 else None
        return result
    return {"rows": len(df), "training_rows": cut, "test_rows": len(ytest), "baseline": scores(baseline), "model": scores(pred), "evaluation": "chronological event holdout; synthetic data; not yet a top-K recommender"}
