"""Build a lightweight import graph for the repository.

The script emits JSON with:
- module/file metadata,
- internal edges (imports that resolve to in-repo modules),
- external imports (unresolved or third-party), and
- reachability of modules from detected entrypoints.

The goal is to provide offline evidence for strangler refactors.  The JSON is
intentionally simple so follow-up tooling (triage, health report) can reuse it.
"""
from __future__ import annotations

import ast
import json
import sys
import datetime as dt
from collections import defaultdict
from importlib import util as importlib_util
from pathlib import Path
from typing import Dict, Iterable, List, Set

ROOT = Path(__file__).resolve().parents[2]

SKIP_DIR_NAMES = {"__pycache__", ".git", ".venv", "node_modules", "build", "dist"}


def iter_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        yield path


def module_name_from_path(path: Path) -> str:
    rel = path.relative_to(ROOT)
    parts = list(rel.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][:-3]
    return ".".join(parts)


def package_name_for(path: Path, module_name: str) -> str:
    if path.name == "__init__.py":
        return module_name
    if "." in module_name:
        return module_name.rsplit(".", 1)[0]
    return module_name


def resolve_from_import(module_name: str, path: Path, node: ast.ImportFrom) -> List[str]:
    package = package_name_for(path, module_name)
    anchor = "." * node.level + (node.module or "")
    resolved_targets: List[str] = []
    try:
        base = importlib_util.resolve_name(anchor or ".", package or module_name)
    except (ImportError, ValueError):
        base = None
    if base is None:
        return []
    # When importing attributes, attempt to resolve to a module if possible.
    for alias in node.names:
        if alias.name == "*":
            resolved_targets.append(base)
            continue
        candidate = f"{base}.{alias.name}" if base else alias.name
        resolved_targets.append(candidate)
    if not resolved_targets:
        resolved_targets.append(base)
    return resolved_targets


def parse_imports(path: Path, module_name: str) -> Set[str]:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return set()
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return set()

    imports: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.update(resolve_from_import(module_name, path, node))
    return imports


def detect_entrypoints(files: Iterable[Path]) -> List[str]:
    entrypoints: List[str] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if "if __name__ == \"__main__\":" in text:
            entrypoints.append(str(path.relative_to(ROOT).as_posix()))
    return sorted(set(entrypoints))


def main() -> None:
    python_files = list(iter_python_files(ROOT))
    module_map: Dict[str, str] = {}
    for path in python_files:
        module_map[module_name_from_path(path)] = str(path.relative_to(ROOT).as_posix())

    nodes = []
    adjacency: Dict[str, Set[str]] = defaultdict(set)
    external_imports: Dict[str, Set[str]] = defaultdict(set)

    for path in python_files:
        module_name = module_name_from_path(path)
        file_key = str(path.relative_to(ROOT).as_posix())
        imports = parse_imports(path, module_name)
        for target in imports:
            resolved = module_map.get(target)
            if resolved:
                adjacency[file_key].add(resolved)
            else:
                # Try parent modules (e.g., importing package but using submodule attributes)
                parent = target
                while "." in parent:
                    parent = parent.rsplit(".", 1)[0]
                    resolved_parent = module_map.get(parent)
                    if resolved_parent:
                        adjacency[file_key].add(resolved_parent)
                        break
                else:
                    external_imports[file_key].add(target)
        nodes.append(
            {
                "file": file_key,
                "module": module_name,
                "internal_imports": sorted(adjacency.get(file_key, set())),
                "external_imports": sorted(external_imports.get(file_key, set())),
            }
        )

    entrypoints = detect_entrypoints(python_files)

    reachable: Dict[str, List[str]] = {}
    for entry in entrypoints:
        visited = set()
        stack = [entry]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            stack.extend(adjacency.get(current, set()))
        reachable[entry] = sorted(visited)

    payload = {
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "root": str(ROOT),
        "entrypoints": entrypoints,
        "nodes": nodes,
        "reachable": reachable,
    }
    json.dump(payload, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
