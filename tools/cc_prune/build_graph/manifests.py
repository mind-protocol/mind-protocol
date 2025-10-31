from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None

SAFE_EXTS = {".json", ".yaml", ".yml"}


def build_edges(repo: Path) -> List[Tuple[Path, Path]]:
    edges: list[tuple[Path, Path]] = []
    for ext in SAFE_EXTS:
        for file in repo.rglob(f"*{ext}"):
            edges.extend(_edges_for_file(file, repo))
    return edges


def _edges_for_file(file: Path, repo: Path) -> List[Tuple[Path, Path]]:
    rel_src = file.relative_to(repo)
    targets: list[Path] = []
    if file.suffix == ".json":
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            targets.extend(_extract_paths(data, file))
        except Exception:
            return []
    else:
        if yaml is None:
            return []
        try:
            data = yaml.safe_load(file.read_text(encoding="utf-8"))
        except Exception:
            return []
        targets.extend(_extract_paths(data, file))
    edges: list[tuple[Path, Path]] = []
    for target in targets:
        if target.exists() and target.is_file():
            edges.append((rel_src, target.relative_to(repo)))
    return edges


def _extract_paths(data: object, file: Path) -> List[Path]:
    found: list[Path] = []
    if isinstance(data, dict):
        for value in data.values():
            found.extend(_extract_paths(value, file))
    elif isinstance(data, list):
        for item in data:
            found.extend(_extract_paths(item, file))
    elif isinstance(data, str):
        candidate = data.strip()
        if not candidate or candidate.startswith("http") or "\n" in candidate:
            return []
        if any(ch.isspace() for ch in candidate):
            return []
        candidate_path = (file.parent / candidate).resolve()
        found.append(candidate_path)
    return found
