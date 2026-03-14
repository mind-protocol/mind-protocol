"""Spawner V1 for creating a basic citizen seeded from position requirements."""

from dataclasses import dataclass
import re
import uuid

STRANGER_TRUST = 0.0


@dataclass(frozen=True)
class SpawnedCitizen:
    citizen_id: str
    name: str
    seeded_capabilities: list[str]
    trust_score: float
    origin_position_id: str
    origin_org_id: str


WORD_RE = re.compile(r"[a-zA-Z0-9_-]+")


def _extract_seed_capabilities(requirements: str) -> list[str]:
    tokens = [t.lower() for t in WORD_RE.findall(requirements)]
    unique = []
    for token in tokens:
        if len(token) < 4:
            continue
        if token not in unique:
            unique.append(token)
    return unique[:12]


def spawn_basic_citizen_for_position(
    position_id: str,
    org_id: str,
    requirements: str,
    name_prefix: str = "Spawned",
) -> SpawnedCitizen:
    if not position_id or not org_id:
        raise ValueError("position_id and org_id are required")

    citizen_id = f"citizen_{uuid.uuid4().hex[:12]}"
    capabilities = _extract_seed_capabilities(requirements)

    return SpawnedCitizen(
        citizen_id=citizen_id,
        name=f"{name_prefix}-{citizen_id[-4:]}",
        seeded_capabilities=capabilities,
        trust_score=STRANGER_TRUST,
        origin_position_id=position_id,
        origin_org_id=org_id,
    )
