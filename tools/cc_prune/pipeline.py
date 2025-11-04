from __future__ import annotations

import datetime as dt
import json
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

logger = logging.getLogger(__name__)

from .asset_index import AssetIndex
from .graph import SimpleDiGraph
from .review_bundle import BundleBuilder
from .scoring import CandidateScorer
from . import utils


@dataclass
class Pipeline:
    repo: Path

    def mark(self, out_dir: Path, quantile: float = 0.85) -> None:
        repo = self.repo
        out_dir = out_dir.resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        index = AssetIndex(repo)
        assets = list(index.iter_assets())
        graph = index.build_graph(assets)
        roots = index.roots

        reachable = utils.reachable_nodes(graph, roots)
        candidates = [node for node in graph.nodes if node not in reachable]

        scorer = CandidateScorer(graph=graph, assets={a.path: a for a in assets})
        scored = scorer.score(candidates, quantile=quantile)

        bundle = BundleBuilder(
            repo=repo,
            out_dir=out_dir,
            graph=graph,
            scored_candidates=scored,
            assets={a.path: a for a in assets},
            reachable=reachable,
            roots=roots,
        )
        bundle.write()

        print(f"Marked {len(scored)} candidates. Bundle written to {out_dir}")

    def review(
        self,
        bundle_dir: Path,
        codex_script: Path,
        auto_approve: bool = False,
    ) -> None:
        bundle_dir = bundle_dir.resolve()
        manifest_file = bundle_dir / "candidates.json"
        if not manifest_file.exists():
            raise FileNotFoundError(
                f"Bundle manifest not found: {manifest_file}. Run mark first."
            )

        with manifest_file.open("r", encoding="utf-8") as fh:
            candidates = json.load(fh)

        decisions_path = bundle_dir / "review_decisions.json"
        if decisions_path.exists():
            print(f"Existing decisions found at {decisions_path}, overwriting.")

        if auto_approve:
            decisions = self._auto_decide(candidates)
        else:
            decisions = self._invoke_codex(
                codex_script=codex_script,
                bundle_dir=bundle_dir,
                manifest=candidates,
            )

        with decisions_path.open("w", encoding="utf-8") as fh:
            json.dump(decisions, fh, indent=2, sort_keys=True)

        print(f"Review decisions written to {decisions_path}")

    def sweep(
        self,
        bundle_dir: Path,
        archive_root: Path,
        dry_run: bool = False,
    ) -> None:
        bundle_dir = bundle_dir.resolve()
        decisions_path = bundle_dir / "review_decisions.json"
        if not decisions_path.exists():
            raise FileNotFoundError(
                f"Decisions file not found: {decisions_path}. Run review first."
            )

        with decisions_path.open("r", encoding="utf-8") as fh:
            decisions: Mapping[str, Mapping[str, Any]] = json.load(fh)

        archive_root = archive_root.resolve()
        if not dry_run:
            archive_root.mkdir(parents=True, exist_ok=True)

        now = dt.datetime.utcnow()
        archive_month = archive_root / now.strftime("%Y-%m")
        if not dry_run:
            archive_month.mkdir(parents=True, exist_ok=True)

        repo = self.repo

        plan: list[tuple[str, Path, Path | None]] = []
        for rel_path, payload in decisions.items():
            decision = payload.get("decision")
            target = repo / rel_path
            if decision == "approve":
                plan.append(("delete", target, None))
            elif decision == "archive":
                archive_dest = archive_month / rel_path
                plan.append(("archive", target, archive_dest))
            else:
                plan.append(("keep", target, None))

        archived_rel_paths: list[Path] = []
        for action, target, archive_dest in plan:
            if action == "keep":
                print(f"KEEP  {target}")
                continue
            if not target.exists():
                print(f"SKIP  {target} (missing)")
                continue
            if action == "delete":
                print(f"DEL   {target}")
                if not dry_run:
                    subprocess.run(["git", "rm", str(target.relative_to(repo))], check=True)
            elif action == "archive" and archive_dest is not None:
                archive_dest.parent.mkdir(parents=True, exist_ok=True)
                print(f"ARCH  {target} -> {archive_dest}")
                if not dry_run:
                    archive_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(target), str(archive_dest))
                    subprocess.run(
                        ["git", "add", str(archive_dest.relative_to(repo))],
                        check=True,
                    )
                    subprocess.run(
                        ["git", "rm", str(target.relative_to(repo))],
                        check=True,
                    )
                archived_rel_paths.append(target.relative_to(repo))

        if archived_rel_paths:
            self._update_doc_manifests(archived_rel_paths, dry_run=dry_run)
            self._update_doc_inventory(archived_rel_paths, dry_run=dry_run)

    def _invoke_codex(
        self,
        codex_script: Path,
        bundle_dir: Path,
        manifest: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        if not codex_script.exists():
            print("Codex script not found; falling back to auto-approve mode.")
            return self._auto_decide(manifest)

        cmd = [
            os.fspath(codex_script),
            "--bundle",
            os.fspath(bundle_dir),
        ]
        print(f"Invoking Codex: {' '.join(cmd)}")
        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:  # pragma: no cover - best effort
            print("Codex invocation failed; stderr follows:")
            print(exc.stderr)
            print("Falling back to auto-approve mode.")
            return self._auto_decide(manifest)

        stdout = proc.stdout.strip()
        try:
            data = json.loads(stdout)
            if not isinstance(data, Mapping):
                raise ValueError("Codex response must be a JSON object")
            return data
        except json.JSONDecodeError:  # pragma: no cover - best effort
            print("Codex response was not valid JSON; falling back to auto mode.")
            return self._auto_decide(manifest)

    def _auto_decide(self, manifest: Mapping[str, Any]) -> Mapping[str, Any]:
        decisions: dict[str, Any] = {}
        for rel_path, payload in manifest.items():
            score = payload.get("score", 0.0)
            reason_codes = payload.get("reason_codes", [])
            decision = "keep"
            if score >= 0.72 and "backup" in reason_codes:
                decision = "approve"
            elif score >= 0.6 and ("docs" in reason_codes or "docs_orphan" in reason_codes):
                decision = "archive"
            elif score >= 0.78 and "no_inbound" in reason_codes:
                decision = "approve"
            decisions[rel_path] = {
                "decision": decision,
                "notes": "auto-decided",
                "score": score,
                "reason_codes": reason_codes,
            }
        return decisions

    def _update_doc_manifests(self, archived: list[Path], dry_run: bool) -> None:
        manifest_path = self.repo / "tools/doc_ingestion/full_manifest.json"
        if not manifest_path.exists():
            return
        try:
            with manifest_path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as exc:
            logger.error(f"Failed to read/parse manifest at {manifest_path}: {exc}")
            return
        files = data.get("files")
        if not isinstance(files, list):
            return

        archived_norm = {
            self._normalize_path_string(str(path)) for path in archived
        }
        removed = 0
        filtered: list[Any] = []
        for entry in files:
            if not isinstance(entry, str):
                filtered.append(entry)
                continue
            normalized = self._normalize_path_string(entry)
            if any(normalized.endswith(rel) for rel in archived_norm):
                removed += 1
                continue
            filtered.append(entry)

        if not removed:
            return

        print(
            "Doc manifest updates: removed",
            removed,
            "entries referencing archived files",
        )
        if dry_run:
            return

        data["files"] = filtered
        manifest_path.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def _update_doc_inventory(self, archived: list[Path], dry_run: bool) -> None:
        inventory_path = self.repo / "docs/DOCUMENTATION_INVENTORY.md"
        if not inventory_path.exists():
            return
        try:
            text = inventory_path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.error(f"Failed to read inventory at {inventory_path}: {exc}")
            return

        archived_norm = {
            self._normalize_path_string(str(path)) for path in archived
        }
        lines = text.splitlines()
        removed = 0
        filtered_lines: list[str] = []
        for line in lines:
            normalized_line = self._normalize_path_string(line)
            if any(rel in normalized_line for rel in archived_norm):
                removed += 1
                continue
            filtered_lines.append(line)

        if not removed:
            return

        print(
            "Documentation inventory updates: removed",
            removed,
            "entries referencing archived files",
        )
        if dry_run:
            return

        inventory_path.write_text("\n".join(filtered_lines) + "\n", encoding="utf-8")

    @staticmethod
    def _normalize_path_string(value: str) -> str:
        value = value.strip("\"")
        try:
            value = value.encode("utf-8").decode("unicode_escape")
            try:
                value = value.encode("latin-1").decode("utf-8")
            except UnicodeDecodeError:
                pass
        except UnicodeDecodeError:
            pass
        return value.replace("\\", "/")
