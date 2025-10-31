from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

IMPORT_RE = re.compile(
    r"import\s+(?:[^'\"]+\s+from\s+)?['\"](?P<path>[^'\"]+)['\"]",
    re.MULTILINE,
)
REQUIRE_RE = re.compile(r"require\(['\"](?P<path>[^'\"]+)['\"]\)")
DYNAMIC_IMPORT_RE = re.compile(r"import\(['\"](?P<path>[^'\"]+)['\"]\)")

EXTENSIONS = [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json"]


def build_edges(repo: Path) -> List[Tuple[Path, Path]]:
    edges: list[tuple[Path, Path]] = []
    for file in repo.rglob("*.ts"):
        edges.extend(_edges_for_file(file, repo))
    for file in repo.rglob("*.tsx"):
        edges.extend(_edges_for_file(file, repo))
    for file in repo.rglob("*.js"):
        edges.extend(_edges_for_file(file, repo))
    for file in repo.rglob("*.jsx"):
        edges.extend(_edges_for_file(file, repo))
    return edges


def _edges_for_file(file: Path, repo: Path) -> List[Tuple[Path, Path]]:
    try:
        text = file.read_text(encoding="utf-8")
    except Exception:
        return []
    rel_src = file.relative_to(repo)
    matches = []
    matches.extend(IMPORT_RE.findall(text))
    matches.extend(REQUIRE_RE.findall(text))
    matches.extend(DYNAMIC_IMPORT_RE.findall(text))
    edges: list[tuple[Path, Path]] = []
    for match in matches:
        resolved = _resolve_import(match, file, repo)
        if resolved is None:
            continue
        edges.append((rel_src, resolved))
    return edges


def _resolve_import(module: str, file: Path, repo: Path) -> Path | None:
    if module.startswith("http"):
        return None
    if module.startswith("@"):
        if module.startswith("@/"):
            candidate = repo / "app" / module[2:]
            resolved = _resolve_with_extensions(candidate)
            if resolved:
                return resolved.relative_to(repo)
        return None
    if module.startswith("./") or module.startswith("../"):
        candidate = (file.parent / module).resolve()
        resolved = _resolve_with_extensions(candidate)
        if resolved:
            return resolved.relative_to(repo)
        return None
    candidate = (repo / module).resolve()
    resolved = _resolve_with_extensions(candidate)
    if resolved:
        return resolved.relative_to(repo)
    return None


def _resolve_with_extensions(candidate: Path) -> Path | None:
    if candidate.is_file():
        return candidate
    for ext in EXTENSIONS:
        path = candidate.with_suffix(ext)
        if path.exists():
            return path
    index_candidate = candidate / "index.ts"
    if index_candidate.exists():
        return index_candidate
    index_candidate = candidate / "index.tsx"
    if index_candidate.exists():
        return index_candidate
    index_candidate = candidate / "index.js"
    if index_candidate.exists():
        return index_candidate
    return None
