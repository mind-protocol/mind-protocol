"""Generate protocol edges for @implements annotations."""
from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_PATH = ROOT / ".artifacts/implements_edges.json"


@dataclass
class Implementation:
    file: str
    symbol: str
    identifiers: List[str]


def _iter_python_files() -> Iterable[Path]:
    for path in ROOT.rglob("*.py"):
        if any(part.startswith(".") for part in path.relative_to(ROOT).parts if part not in {"."}):
            continue
        yield path


def _collect_from_file(path: Path) -> List[Implementation]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    implementations: List[Implementation] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        ids: List[str] = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and getattr(decorator.func, "id", "") == "implements":
                for arg in decorator.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        ids.append(arg.value)
        if ids:
            implementations.append(
                Implementation(
                    file=str(path.relative_to(ROOT)),
                    symbol=node.name,
                    identifiers=ids,
                )
            )
    return implementations


def discover() -> List[Implementation]:
    discovered: List[Implementation] = []
    for path in _iter_python_files():
        discovered.extend(_collect_from_file(path))
    return discovered


def main() -> None:
    implementations = discover()
    payload = {
        "edges": [
            {
                "file": impl.file,
                "symbol": impl.symbol,
                "ids": impl.identifiers,
            }
            for impl in implementations
        ]
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
