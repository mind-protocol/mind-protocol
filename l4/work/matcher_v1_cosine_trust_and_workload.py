"""Matcher V1: cosine similarity + trust weighting + workload penalty."""

from dataclasses import dataclass
import math
import re

MATCH_THRESHOLD = 0.6
WORKLOAD_PENALTY = 0.2


@dataclass(frozen=True)
class CandidateProfile:
    citizen_id: str
    status: str
    capabilities_text: str
    trust_score: float
    active_memberships: int


@dataclass(frozen=True)
class MatchScore:
    citizen_id: str
    similarity: float
    trust_weight: float
    workload_factor: float
    score: float


WORD_RE = re.compile(r"[a-zA-Z0-9_-]+")


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in WORD_RE.findall(text)]


def _term_frequency(tokens: list[str]) -> dict[str, float]:
    counts: dict[str, float] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0.0) + 1.0
    return counts


def cosine_similarity(text_a: str, text_b: str) -> float:
    a = _term_frequency(_tokens(text_a))
    b = _term_frequency(_tokens(text_b))
    if not a or not b:
        return 0.0

    shared = set(a).intersection(b)
    dot = sum(a[t] * b[t] for t in shared)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rank_candidates_for_position(
    position_requirements: str,
    candidates: list[CandidateProfile],
    threshold: float = MATCH_THRESHOLD,
) -> list[MatchScore]:
    ranked: list[MatchScore] = []

    for candidate in candidates:
        if candidate.status != "active":
            continue

        similarity = cosine_similarity(position_requirements, candidate.capabilities_text)
        if similarity < threshold:
            continue

        trust_weight = max(0.0, min(1.0, candidate.trust_score / 100.0))
        workload_factor = 1.0 / (1.0 + (WORKLOAD_PENALTY * max(0, candidate.active_memberships)))
        score = similarity * trust_weight * workload_factor

        ranked.append(
            MatchScore(
                citizen_id=candidate.citizen_id,
                similarity=similarity,
                trust_weight=trust_weight,
                workload_factor=workload_factor,
                score=score,
            )
        )

    return sorted(ranked, key=lambda item: item.score, reverse=True)
