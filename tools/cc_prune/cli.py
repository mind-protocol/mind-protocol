from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from .pipeline import Pipeline


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="cc-prune",
        description="Identify and sweep unused repository assets",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Repository root (defaults to current working directory)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    mark_parser = subparsers.add_parser(
        "mark", help="Scan the repository and mark deletion candidates"
    )
    mark_parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Directory to place the review bundle",
    )
    mark_parser.add_argument(
        "--quantile",
        type=float,
        default=0.85,
        help="Quantile threshold for candidate scoring (0-1)",
    )

    review_parser = subparsers.add_parser(
        "review", help="Request Codex review for previously marked candidates"
    )
    review_parser.add_argument(
        "--bundle",
        type=Path,
        required=True,
        help="Path to the bundle directory created by the mark step",
    )
    review_parser.add_argument(
        "--codex-script",
        type=Path,
        default=Path("sdk/providers/run_codex.py"),
        help="Path to the Codex invocation script",
    )
    review_parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Skip Codex invocation and auto approve highest-confidence candidates",
    )

    sweep_parser = subparsers.add_parser(
        "sweep", help="Apply Codex decisions to the working tree"
    )
    sweep_parser.add_argument(
        "--bundle",
        type=Path,
        required=True,
        help="Path to the bundle directory that contains review_decisions.json",
    )
    sweep_parser.add_argument(
        "--archive-root",
        type=Path,
        default=Path("archive"),
        help="Root directory to store archived files",
    )
    sweep_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report planned actions without modifying the working tree",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    pipeline = Pipeline(repo=args.repo)

    if args.command == "mark":
        pipeline.mark(out_dir=args.out, quantile=args.quantile)
    elif args.command == "review":
        pipeline.review(
            bundle_dir=args.bundle,
            codex_script=args.codex_script,
            auto_approve=args.auto_approve,
        )
    elif args.command == "sweep":
        pipeline.sweep(
            bundle_dir=args.bundle,
            archive_root=args.archive_root,
            dry_run=args.dry_run,
        )
    else:
        raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
