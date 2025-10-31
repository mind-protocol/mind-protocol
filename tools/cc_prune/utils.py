from __future__ import annotations

import os
from collections import deque
from pathlib import Path
from typing import Iterable, Set

from .graph import SimpleDiGraph


def reachable_nodes(graph: SimpleDiGraph, roots: Iterable[Path]) -> Set[Path]:
    visited: set[Path] = set()
    queue: deque[Path] = deque()

    for root in roots:
        if graph.has_node(root):
            queue.append(root)
            visited.add(root)

    while queue:
        node = queue.popleft()
        for neighbor in graph.successors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return visited


def normalize_path(path: Path) -> Path:
    return Path(str(path).replace("\\", "/"))


def safe_relpath(path: Path, start: Path) -> Path:
    try:
        return path.relative_to(start)
    except ValueError:
        return Path(os.path.relpath(path, start))
