"""LinUCB and off-policy estimators; deliberately separate policy and logging propensities."""
from __future__ import annotations
import numpy as np


class LinUCB:
    def __init__(self, n_actions: int, dim: int, alpha: float = 0.5):
        if n_actions < 2 or dim < 1 or alpha < 0:
            raise ValueError("invalid bandit parameters")
        self.n_actions, self.dim, self.alpha = n_actions, dim, alpha
        self.a = np.stack([np.eye(dim) for _ in range(n_actions)])
        self.b = np.zeros((n_actions, dim))

    def choose(self, features: np.ndarray) -> int:
        x = np.asarray(features, dtype=float)
        if x.shape != (self.dim,):
            raise ValueError("feature dimension mismatch")
        scores = []
        for i in range(self.n_actions):
            theta = np.linalg.solve(self.a[i], self.b[i])
            width = np.sqrt(x @ np.linalg.solve(self.a[i], x))
            scores.append(x @ theta + self.alpha * width)
        return int(np.argmax(scores))

    def update(self, action: int, x: np.ndarray, reward: float) -> None:
        if not 0 <= action < self.n_actions or not 0 <= reward <= 1:
            raise ValueError("invalid action or reward")
        x = np.asarray(x, dtype=float)
        if x.shape != (self.dim,):
            raise ValueError("feature dimension mismatch")
        self.a[action] += np.outer(x, x)
        self.b[action] += reward * x


def off_policy_estimate(rewards: np.ndarray, logging_propensities: np.ndarray,
                        target_probabilities: np.ndarray, clip: float = 20) -> dict:
    """IPS/SNIPS for logged actions. Evaluates *only* when support/positivity holds."""
    r, p, q = [np.asarray(a, dtype=float) for a in (rewards, logging_propensities, target_probabilities)]
    if not len(r) or r.shape != p.shape or p.shape != q.shape:
        raise ValueError("arrays must have matching nonempty shape")
    if (p <= 0).any() or (p > 1).any() or (q < 0).any() or (q > 1).any():
        raise ValueError("propensities must be in (0,1], target probabilities in [0,1]")
    if (r < 0).any() or (r > 1).any() or clip < 1:
        raise ValueError("invalid reward or clip")
    w = np.minimum(q / p, clip)
    mass = float(w.sum())
    return {"ips": round(float(np.mean(w * r)), 5),
            "snips": round(float((w @ r) / mass), 5) if mass else None,
            "effective_sample_size": round(float(mass ** 2 / (w @ w)), 2) if (w @ w) else 0,
            "clipped_fraction": round(float(np.mean(q / p > clip)), 5),
            "n": len(r)}


def simulate(n: int = 3000, seed: int = 42) -> dict:
    if n <= 1:
        raise ValueError("need at least 2 rounds")
    rng = np.random.default_rng(seed)
    policy = LinUCB(n_actions=3, dim=3)
    earned, oracle = [], []
    for _ in range(n):
        x = rng.normal(size=3)
        hidden = np.array([.65 * x[0] - .3 * x[1], .7 * x[1], -.4 * x[0] + .8 * x[2]])
        probs = 1 / (1 + np.exp(-hidden))
        action = policy.choose(x)
        reward = float(rng.random() < probs[action])
        policy.update(action, x, reward)
        earned.append(reward)
        oracle.append(float(max(probs)))
    return {"environment": "synthetic_contextual_bandit", "rounds": n,
            "empirical_reward": round(float(np.mean(earned)), 4),
            "expected_oracle_reward": round(float(np.mean(oracle)), 4),
            "pseudo_regret_upper_reference": round(float(np.mean(oracle) - np.mean(earned)), 4)}
