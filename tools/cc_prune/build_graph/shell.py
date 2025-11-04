from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

FILE_PATTERN = re.compile(r"(?P<path>(?:\./)?[\w./-]+\.(?:sh|py|ts|js|tsx|jsx|json))")


def build_edges(repo: Path) -> List[Tuple[Path, Path]]:
    edges: list[tuple[Path, Path]] = []
    for file in repo.rglob("*.sh"):
        edges.extend(_edges_for_file(file, repo))
    for file in repo.rglob("*.py"):
        edges.extend(_subprocess_edges(file, repo))
    return edges


def _edges_for_file(file: Path, repo: Path) -> List[Tuple[Path, Path]]:
    try:
        text = file.read_text(encoding="utf-8")
    except Exception as exc:
        logger.error(f"Failed to read shell script {file}: {exc}")
        return []
    rel_src = file.relative_to(repo)
    edges: list[tuple[Path, Path]] = []
    for match in FILE_PATTERN.finditer(text):
        candidate = (file.parent / match.group("path")).resolve()
        if candidate.exists() and candidate.is_file():
            edges.append((rel_src, candidate.relative_to(repo)))
    return edges


def _subprocess_edges(file: Path, repo: Path) -> List[Tuple[Path, Path]]:
    try:
        text = file.read_text(encoding="utf-8")
    except Exception as exc:
        logger.error(f"Failed to read Python script for subprocess analysis {file}: {exc}")
        return []
    rel_src = file.relative_to(repo)
    edges: list[tuple[Path, Path]] = []
    for match in FILE_PATTERN.finditer(text):
        candidate = (file.parent / match.group("path")).resolve()
        if candidate.exists() and candidate.is_file():
            edges.append((rel_src, candidate.relative_to(repo)))
    return edges
