from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, MutableMapping, MutableSet, Set, Tuple


@dataclass
class SimpleDiGraph:
    _succ: MutableMapping[Path, MutableSet[Path]] = field(default_factory=dict)
    _pred: MutableMapping[Path, MutableSet[Path]] = field(default_factory=dict)

    def add_node(self, node: Path) -> None:
        self._succ.setdefault(node, set())
        self._pred.setdefault(node, set())

    def add_edge(self, u: Path, v: Path) -> None:
        self.add_node(u)
        self.add_node(v)
        self._succ[u].add(v)
        self._pred[v].add(u)

    @property
    def nodes(self) -> Set[Path]:
        return set(self._succ.keys())

    def edges(self) -> Iterator[Tuple[Path, Path]]:
        for u, vs in self._succ.items():
            for v in vs:
                yield (u, v)

    def successors(self, node: Path) -> Set[Path]:
        return set(self._succ.get(node, set()))

    def in_degree(self, node: Path) -> int:
        return len(self._pred.get(node, set()))

    def out_degree(self, node: Path) -> int:
        return len(self._succ.get(node, set()))

    def number_of_nodes(self) -> int:
        return len(self._succ)

    def number_of_edges(self) -> int:
        return sum(len(vs) for vs in self._succ.values())

    def has_node(self, node: Path) -> bool:
        return node in self._succ


def write_gexf(graph: SimpleDiGraph, path: Path) -> None:
    nodes = list(graph.nodes)
    node_indices = {node: idx for idx, node in enumerate(nodes)}
    lines = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        "<gexf xmlns=\"http://www.gexf.net/1.2draft\" version=\"1.2\">",
        "  <graph mode=\"static\" defaultedgetype=\"directed\">",
        "    <nodes>",
    ]
    for node in nodes:
        label = str(node).replace("\\", "/")
        lines.append(f"      <node id=\"{node_indices[node]}\" label=\"{label}\" />")
    lines.append("    </nodes>")
    lines.append("    <edges>")
    for idx, (u, v) in enumerate(graph.edges()):
        lines.append(
            f"      <edge id=\"{idx}\" source=\"{node_indices[u]}\" target=\"{node_indices[v]}\" />"
        )
    lines.append("    </edges>")
    lines.append("  </graph>")
    lines.append("</gexf>")
    path.write_text("\n".join(lines), encoding="utf-8")
