from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Sequence

from .build_graph import docs as docs_graph
from .build_graph import manifests, py as py_graph, shell as shell_graph, ts_js
from .graph import SimpleDiGraph


@dataclass
class Asset:
    path: Path
    kind: str
    category: str
    size: int
    mtime: float


class AssetIndex:
    def __init__(self, repo: Path) -> None:
        self.repo = repo.resolve()
        self.roots: set[Path] = set()

    def iter_assets(self) -> Iterator[Asset]:
        repo = self.repo
        for path in repo.rglob("*"):
            if path.is_file() and ".git" not in path.parts:
                rel = path.relative_to(repo)
                kind = self._detect_kind(rel)
                category = self._detect_category(rel)
                stat = path.stat()
                yield Asset(
                    path=rel,
                    kind=kind,
                    category=category,
                    size=stat.st_size,
                    mtime=stat.st_mtime,
                )

    def build_graph(self, assets: Sequence[Asset]) -> SimpleDiGraph:
        graph = SimpleDiGraph()
        repo = self.repo

        for asset in assets:
            graph.add_node(asset.path)

        ts_edges = ts_js.build_edges(repo)
        py_edges = py_graph.build_edges(repo)
        doc_edges = docs_graph.build_edges(repo)
        manifest_edges = manifests.build_edges(repo)
        shell_edges = shell_graph.build_edges(repo)

        for edge in ts_edges + py_edges + doc_edges + manifest_edges + shell_edges:
            if graph.has_node(edge[0]) and graph.has_node(edge[1]):
                graph.add_edge(*edge)

        self._populate_roots(graph)

        return graph

    def _populate_roots(self, graph: SimpleDiGraph) -> None:
        repo = self.repo
        roots: set[Path] = set()

        for page in repo.glob("app/**/*.tsx"):
            if page.name in {"page.tsx", "layout.tsx", "route.tsx", "page.ts", "layout.ts"}:
                roots.add(page.relative_to(repo))
        for page in repo.glob("app/**/*.ts"):
            if page.name in {"page.ts", "layout.ts", "route.ts"}:
                roots.add(page.relative_to(repo))
        for api_route in repo.glob("app/api/**/route.ts"):
            roots.add(api_route.relative_to(repo))

        package_json = repo / "package.json"
        if package_json.exists():
            roots.add(package_json.relative_to(repo))
            with package_json.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            scripts = data.get("scripts", {})
            for command in scripts.values():
                for match in re.finditer(
                    r"(?P<path>(?:\./)?[\w./-]+\.(?:js|ts|tsx|mjs|cjs|sh|py))",
                    command,
                ):
                    candidate = (repo / match.group("path")).resolve()
                    if candidate.exists() and candidate.is_file():
                        roots.add(candidate.relative_to(repo))

        service_yaml = repo / "orchestration/services/mpsv3/services.yaml"
        if service_yaml.exists():
            roots.add(service_yaml.relative_to(repo))

        docs_inventory = repo / "docs/DOCUMENTATION_INVENTORY.md"
        if docs_inventory.exists():
            roots.add(docs_inventory.relative_to(repo))
        docs_manifest = repo / "tools/doc_ingestion/full_manifest.json"
        if docs_manifest.exists():
            roots.add(docs_manifest.relative_to(repo))

        for cli in repo.glob("*.py"):
            if cli.name.endswith(".py") and cli.stat().st_mode & 0o111:
                roots.add(cli.relative_to(repo))

        known_clis = [
            "run_consciousness_system.py",
            "monitor_entity_evolution.py",
        ]
        for cli in known_clis:
            path = repo / cli
            if path.exists():
                roots.add(path.relative_to(repo))

        self.roots = {node for node in roots if graph.has_node(node)}

    @staticmethod
    def _detect_kind(rel_path: Path) -> str:
        suffix = rel_path.suffix.lower()
        if suffix in {".ts", ".tsx", ".js", ".jsx"}:
            return "ts"
        if suffix == ".py":
            return "python"
        if suffix in {".md", ".mdx"}:
            return "markdown"
        if suffix in {".json", ".yaml", ".yml"}:
            return "config"
        return "other"

    @staticmethod
    def _detect_category(rel_path: Path) -> str:
        parts = rel_path.parts
        if parts and parts[0] == "app":
            return "frontend"
        if parts and parts[0] == "orchestration":
            return "orchestration"
        if parts and parts[0] == "docs":
            return "docs"
        if parts and parts[0] == "tools":
            return "tools"
        return "other"
