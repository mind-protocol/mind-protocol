from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Mapping

from .asset_index import Asset
from .graph import SimpleDiGraph, write_gexf
from .scoring import CandidateScore


class BundleBuilder:
    def __init__(
        self,
        repo: Path,
        out_dir: Path,
        graph: SimpleDiGraph,
        scored_candidates: Mapping[Path, CandidateScore],
        assets: Mapping[Path, Asset],
        reachable: Iterable[Path],
        roots: Iterable[Path],
    ) -> None:
        self.repo = repo
        self.out_dir = out_dir
        self.graph = graph
        self.scored_candidates = scored_candidates
        self.assets = assets
        self.reachable = set(reachable)
        self.roots = list(roots)

    def write(self) -> None:
        bundle_dir = self.out_dir
        bundle_dir.mkdir(parents=True, exist_ok=True)
        self._write_candidates_json()
        self._write_candidates_csv()
        self._write_summary_md()
        self._write_graph()
        self._write_snippets()

    def _write_candidates_json(self) -> None:
        manifest = {
            str(path): {
                "score": score.score,
                "reason_codes": score.reason_codes,
                "features": score.features,
            }
            for path, score in self.scored_candidates.items()
        }
        with (self.out_dir / "candidates.json").open("w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, sort_keys=True)

    def _write_candidates_csv(self) -> None:
        csv_path = self.out_dir / "candidates.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["path", "score", "reason_codes", "in_degree", "out_degree"])
            for path, score in sorted(
                self.scored_candidates.items(), key=lambda item: item[1].score, reverse=True
            ):
                writer.writerow(
                    [
                        str(path),
                        f"{score.score:.4f}",
                        ";".join(score.reason_codes),
                        self.graph.in_degree(path),
                        self.graph.out_degree(path),
                    ]
                )

    def _write_summary_md(self) -> None:
        summary_path = self.out_dir / "SUMMARY.md"
        lines = [
            "# cc-prune Mark Report",
            "",
            f"Total nodes: {self.graph.number_of_nodes()}",
            f"Total edges: {self.graph.number_of_edges()}",
            f"Roots: {len(self.roots)}",
            f"Reachable nodes: {len(self.reachable)}",
            f"Candidates: {len(self.scored_candidates)}",
            "",
            "## Top Candidates",
            "",
        ]
        for path, score in sorted(
            self.scored_candidates.items(), key=lambda item: item[1].score, reverse=True
        )[:20]:
            lines.append(f"- `{path}` — score {score.score:.3f} ({', '.join(score.reason_codes)})")
        summary_path.write_text("\n".join(lines), encoding="utf-8")

    def _write_graph(self) -> None:
        graph_path = self.out_dir / "graph.gexf"
        write_gexf(self.graph, graph_path)

    def _write_snippets(self) -> None:
        snippets_dir = self.out_dir / "snippets"
        snippets_dir.mkdir(parents=True, exist_ok=True)
        for path in self.scored_candidates:
            file_path = self.repo / path
            if not file_path.exists():
                continue
            try:
                text = file_path.read_text(encoding="utf-8")
            except Exception:
                continue
            snippet = "\n".join(text.splitlines()[:40])
            (snippets_dir / (path.name + ".txt")).write_text(snippet, encoding="utf-8")
