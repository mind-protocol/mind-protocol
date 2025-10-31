from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Tuple


def build_edges(repo: Path) -> List[Tuple[Path, Path]]:
    edges: list[tuple[Path, Path]] = []
    for file in repo.rglob("*.py"):
        if ".git" in file.parts:
            continue
        rel_src = file.relative_to(repo)
        try:
            tree = ast.parse(file.read_text(encoding="utf-8"))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target = _resolve(alias.name, file, repo)
                    if target is not None:
                        edges.append((rel_src, target))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                target = _resolve(module, file, repo, level=node.level)
                if target is not None:
                    edges.append((rel_src, target))
    return edges


def _resolve(module: str, file: Path, repo: Path, level: int = 0) -> Path | None:
    if module.startswith("."):
        level = module.count(".")
        module = module[level:]
    if level:
        parent = file.parent
        for _ in range(level):
            parent = parent.parent
        base = parent
    else:
        base = repo
    if not module:
        candidate = base / "__init__.py"
        if candidate.exists():
            return candidate.relative_to(repo)
        return None
    relative = module.replace(".", "/")
    candidate = (base / relative).resolve()
    if candidate.is_file():
        return candidate.relative_to(repo)
    if (candidate / "__init__.py").exists():
        return (candidate / "__init__.py").relative_to(repo)
    py_candidate = candidate.with_suffix(".py")
    if py_candidate.exists():
        return py_candidate.relative_to(repo)
    return None
