from __future__ import annotations

import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping

from .asset_index import Asset
from .graph import SimpleDiGraph


@dataclass
class CandidateScore:
    path: Path
    score: float
    reason_codes: list[str]
    features: dict[str, float]


class CandidateScorer:
    def __init__(self, graph: SimpleDiGraph, assets: Mapping[Path, Asset]) -> None:
        self.graph = graph
        self.assets = assets

    def score(
        self, candidates: Iterable[Path], quantile: float = 0.85
    ) -> Dict[Path, CandidateScore]:
        scores: dict[Path, CandidateScore] = {}
        feature_rows: list[tuple[Path, dict[str, float], list[str]]] = []

        now = time.time()
        ages = [now - asset.mtime for asset in self.assets.values()]
        if ages:
            mean_age = sum(ages) / len(ages)
            var_age = sum((age - mean_age) ** 2 for age in ages) / len(ages)
            std_age = math.sqrt(var_age) if var_age else 1.0
        else:
            mean_age = 0.0
            std_age = 1.0

        for candidate in candidates:
            asset = self.assets.get(candidate)
            if not asset:
                continue
            in_degree = self.graph.in_degree(candidate)
            age = now - asset.mtime
            age_z = (age - mean_age) / std_age if std_age else 0.0
            is_docs = asset.category == "docs"
            is_docs_orphan = bool(is_docs and in_degree == 0)
            reason_codes: list[str] = []
            feature_vector = {
                "no_inbound": 1.0 if in_degree == 0 else 0.0,
                "age_z": age_z,
                "backup": 1.0 if _is_backup(candidate) else 0.0,
                "docs": 1.0 if is_docs else 0.0,
                "docs_orphan": 1.0 if is_docs_orphan else 0.0,
            }
            if in_degree == 0:
                reason_codes.append("no_inbound")
            if feature_vector["backup"]:
                reason_codes.append("backup")
            if feature_vector["docs"]:
                reason_codes.append("docs")
            if feature_vector["docs_orphan"]:
                reason_codes.append("docs_orphan")
            feature_rows.append((candidate, feature_vector, reason_codes))

        weights = {
            "no_inbound": 2.0,
            "age_z": 0.6,
            "backup": 0.8,
            "docs": 0.9,
            "docs_orphan": 1.2,
        }
        norm = math.sqrt(sum(value**2 for value in weights.values()))
        weights = {key: value / norm for key, value in weights.items()}

        raw_scores = []
        for candidate, feats, reason_codes in feature_rows:
            linear = sum(weights[name] * feats[name] for name in feats)
            probability = 1 / (1 + math.exp(-linear))
            raw_scores.append(probability)
            scores[candidate] = CandidateScore(
                path=candidate,
                score=probability,
                reason_codes=reason_codes,
                features=feats,
            )

        if not raw_scores:
            return scores

        sorted_scores = sorted(raw_scores)
        index = int(len(sorted_scores) * quantile)
        if index >= len(sorted_scores):
            index = len(sorted_scores) - 1
        threshold = sorted_scores[index]

        filtered = {
            path: score
            for path, score in scores.items()
            if score.score >= threshold
        }
        return filtered


def _is_backup(path: Path) -> bool:
    name = path.name.lower()
    return (
        name.endswith(".bak")
        or name.endswith(".bak.ts")
        or name.endswith(".bak.py")
        or name.endswith(".bak.tsx")
        or "backup" in name
    )
