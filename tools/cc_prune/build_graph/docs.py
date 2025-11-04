from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

LINK_RE = re.compile(r"\[[^\]]*\]\((?P<target>[^)]+)\)")
HTML_LINK_RE = re.compile(r"(?:href|src)=\"(?P<target>[^\"]+)\"")


def build_edges(repo: Path) -> List[Tuple[Path, Path]]:
    edges: list[tuple[Path, Path]] = []
    for file in repo.rglob("*.md"):
        edges.extend(_edges_for_file(file, repo))
    for file in repo.rglob("*.mdx"):
        edges.extend(_edges_for_file(file, repo))
    return edges


def _edges_for_file(file: Path, repo: Path) -> List[Tuple[Path, Path]]:
    try:
        text = file.read_text(encoding="utf-8")
    except Exception as exc:
        logger.error(f"Failed to read documentation file {file}: {exc}")
        return []
    rel_src = file.relative_to(repo)
    targets = []
    targets.extend(match.group("target") for match in LINK_RE.finditer(text))
    targets.extend(match.group("target") for match in HTML_LINK_RE.finditer(text))
    edges: list[tuple[Path, Path]] = []
    for target in targets:
        if target.startswith("http") or target.startswith("#"):
            continue
        target = target.split("#", 1)[0]
        candidate = (file.parent / target).resolve()
        if candidate.exists() and candidate.is_file():
            edges.append((rel_src, candidate.relative_to(repo)))
    return edges
