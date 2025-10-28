"""
Install membrane Git hooks into the local repository.

Ensures commit/push operations only succeed when executed by the Git Runner.
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
from pathlib import Path
from typing import Iterable, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
HOOKS: Iterable[Tuple[str, str, str]] = (
    ("pre-commit", "pre-commit", "pre-commit.ps1"),
    ("pre-push", "pre-push", "pre-push.ps1"),
)


def install_hooks(force: bool = False) -> None:
    git_dir = REPO_ROOT / ".git"
    if not git_dir.exists():
        raise SystemExit("This script must be run within a Git repository (no .git/ found).")

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    for hook_name, unix_template, ps_template in HOOKS:
        _copy_template(hooks_dir, hook_name, unix_template, force, is_windows=False)
        _copy_template(hooks_dir, f"{hook_name}.ps1", ps_template, force, is_windows=True)


def _copy_template(
    hooks_dir: Path,
    target_name: str,
    template_name: str,
    force: bool,
    *,
    is_windows: bool,
) -> None:
    source = TEMPLATE_DIR / template_name
    if not source.exists():
        raise SystemExit(f"Missing hook template: {source}")

    target = hooks_dir / target_name
    if target.exists() and not force:
        return

    shutil.copyfile(source, target)
    if not is_windows:
        mode = target.stat().st_mode
        target.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install Git runner enforcement hooks.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing hooks.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    install_hooks(force=args.force)
    print("✅ Git hooks installed. Commits/pushes now require Git Runner.")


if __name__ == "__main__":  # pragma: no cover
    main()
