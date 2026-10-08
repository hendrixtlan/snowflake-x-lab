"""Small but real GPU-capable implicit two-tower model. Cloud GPU submission is a separate gated step."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .metrics import ranking_scores
from .ranking import split_interactions


def train_two_tower(events: pd.DataFrame, tracks_count: int | None = None,
                    epochs: int = 4, dim: int = 32, seed: int = 42,
                    device: str = "auto", k: int = 10) -> dict:
    try:
        import torch
        from torch import nn
    except ImportError as e:
        raise RuntimeError("Install pip install -e '.[gpu]' to run real torch training") from e
    if epochs < 1 or dim < 1 or k < 1:
        raise ValueError("invalid hyperparameters")
    torch.manual_seed(seed)
    np.random.seed(seed)
    train, test = split_interactions(events)
    unique_users = sorted(events.user_id.unique().tolist())
    unique_items = sorted(events.track_id.unique().tolist())
    user_map = {x: i for i, x in enumerate(unique_users)}
    item_map = {x: i for i, x in enumerate(unique_items)}
    n_users, n_items = len(user_map), len(item_map)
    if tracks_count is not None and tracks_count != n_items:
        raise ValueError("tracks_count must equal observed catalog size")
    actual = test.groupby("user_id")["track_id"].apply(set).to_dict()
    seen = train.groupby("user_id")["track_id"].apply(set).to_dict()
    pos_users = np.asarray([user_map[u] for u in train.user_id], dtype=np.int64)
    pos_items = np.asarray([item_map[t] for t in train.track_id], dtype=np.int64)
    gpu = "cuda" if (device == "auto" and torch.cuda.is_available()) else ("cpu" if device == "auto" else device)
    if gpu.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA explicitly requested but not available")

    class Towers(nn.Module):
        def __init__(self):
            super().__init__()
            self.user_emb = nn.Embedding(n_users, dim)
            self.item_emb = nn.Embedding(n_items, dim)
            nn.init.normal_(self.user_emb.weight, std=.08)
            nn.init.normal_(self.item_emb.weight, std=.08)
        def forward(self, u, pos, neg):
            a = self.user_emb(u)
            return (a * self.item_emb(pos)).sum(1), (a * self.item_emb(neg)).sum(1)

    net = Towers().to(gpu)
    optimizer = torch.optim.AdamW(net.parameters(), lr=.015, weight_decay=.0001)
    rng = np.random.default_rng(seed)
    history = []
    # BPR pairwise loss with sampled unobserved negatives.
    for _ in range(epochs):
        permutation = rng.permutation(len(pos_users))
        epoch_losses = []
        for batch in np.array_split(permutation, max(1, int(np.ceil(len(permutation) / 512)))):
            u = torch.tensor(pos_users[batch], device=gpu)
            p = torch.tensor(pos_items[batch], device=gpu)
            negatives = rng.integers(0, n_items, len(batch))
            # Avoid known positives for each user; potential false negatives are discussed in docs.
            for j, idx in enumerate(batch):
                known = {item_map[t] for t in seen[unique_users[pos_users[idx]]]}
                if len(known) >= n_items:
                    raise ValueError("no unobserved negatives available")
                while int(negatives[j]) in known:
                    negatives[j] = rng.integers(0, n_items)
            neg = torch.tensor(negatives, device=gpu)
            positive, negative = net(u, p, neg)
            loss = torch.nn.functional.softplus(negative - positive).mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_losses.append(float(loss.detach().cpu()))
        history.append(round(float(np.mean(epoch_losses)), 5))

    net.eval()
    with torch.no_grad():
        item_vectors = net.item_emb.weight.detach()
        users_idx = torch.tensor([user_map[u] for u in actual], device=gpu)
        scores = (net.user_emb(users_idx) @ item_vectors.T).cpu().numpy()
    rankings = {}
    for i, u in enumerate(actual):
        row = scores[i].copy()
        for t in seen[u]:
            row[item_map[t]] = -np.inf
        best = np.argsort(-row)[:k]
        rankings[int(u)] = [int(unique_items[j]) for j in best]
    return {"model": "implicit_bpr_two_tower", "device": gpu, "parameters": sum(p.numel() for p in net.parameters()),
            "train_rows": len(train), "epochs": epochs, "loss_by_epoch": history, "k": k,
            "holdout": "leave_last_positive_per_user", "known_limitation": "Sampled negatives may be unlabeled positives; also see popularity benchmark's global as-of leakage caveat.",
            **ranking_scores(actual, rankings, k)}
