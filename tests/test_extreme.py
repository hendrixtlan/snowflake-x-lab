import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from music_lab.metrics import ranking_scores, latency_summary, bootstrap_mean_ci
from music_lab.streaming import ExactlyOnceState, Event, benchmark
from music_lab.bandit import LinUCB, off_policy_estimate, simulate
from music_lab.ranking import popularity_benchmark
from music_lab.two_tower import train_two_tower
from music_lab.security import Principal, Resource, authorize, run_boundary_suite
from music_lab.generate import generate
from music_lab.generate_extreme import generate_extreme


def test_metrics_correctness():
    s = ranking_scores({1: {3, 4}}, {1: [3, 2, 1]}, k=3)
    assert s["recall_at_k"] == .5
    assert 0 < s["ndcg_at_k"] < 1
    assert latency_summary([1, 2, 3])["p99_ms"] > 2.9
    assert len(bootstrap_mean_ci([1, 2, 3])) == 2
    with pytest.raises(ValueError):
        latency_summary([])


def test_exactly_once_with_duplicate_and_cross_tenant():
    state = ExactlyOnceState(allowed_lateness_ms=100)
    assert state.apply(Event("a", "1", 12, 100, 101))
    assert not state.apply(Event("a", "1", 12, 100, 102))
    assert state.apply(Event("b", "1", 12, 100, 103))
    assert state.duplicates == 1
    assert state.counts[("a", 12)] == 1
    assert state.counts[("b", 12)] == 1
    assert benchmark(200, seed=5)["committed_once"] == 200


def test_bandit_off_policy():
    policy = LinUCB(3, 2)
    x = np.array([1., 0.])
    policy.update(0, x, 1)
    assert policy.choose(x) in (0, 1, 2)
    scores = off_policy_estimate(np.array([1., 0., 1.]), np.array([.5]*3), np.array([.5]*3))
    assert scores["ips"] == pytest.approx(2/3, abs=.0001)
    assert scores["effective_sample_size"] == 3
    assert simulate(100, seed=4)["rounds"] == 100
    with pytest.raises(ValueError):
        off_policy_estimate(np.array([1.]), np.array([0.]), np.array([1.]))


def test_tenant_access_denied():
    p = Principal("t1", "A", "analyst")
    assert authorize(p, Resource("t1", "x"))
    assert not authorize(p, Resource("t2", "x"))
    assert not authorize(p, Resource("t1", "x", "restricted"))
    assert run_boundary_suite()["passed"] == 4


def test_generated_multitenant_stream_is_repeatable(tmp_path):
    a = generate_extreme(str(tmp_path / "a"), n_events=200, seed=4)
    b = generate_extreme(str(tmp_path / "b"), n_events=200, seed=4)
    assert a["sha256_stream_events"] == b["sha256_stream_events"]
    with open(tmp_path / "a" / "stream_events.jsonl") as f:
        rows = [json.loads(line) for line in f]
    assert len({(r["tenant_id"], r["event_id"]) for r in rows}) == 200
    assert all(r["user_id"].startswith(r["tenant_id"] + "_") for r in rows)


def test_retrieval_models(tmp_path):
    paths = generate(str(tmp_path), users=15, tracks=17, events=800, seed=12)
    df = pd.read_csv(paths["listening_events"])
    pop = popularity_benchmark(df, k=5)
    assert 0 <= pop["recall_at_k"] <= 1
    torch = pytest.importorskip("torch")
    out = train_two_tower(df, epochs=2, dim=8, device="cpu", k=5)
    assert out["device"] == "cpu"
    assert 0 <= out["recall_at_k"] <= 1
    assert len(out["loss_by_epoch"]) == 2
