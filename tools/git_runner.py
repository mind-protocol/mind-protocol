"""
Minimal Git Runner CLI obeying membrane discipline.

Provides `commit` and `pr` commands invoked by orchestration/tool mesh.
Installs Git hooks automatically to block manual IDE commits/pushes.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

from tools.git_hooks import install as hook_install

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_git(args: List[str], *, env_override: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["GIT_RUNNER"] = "1"
    if env_override:
        env.update(env_override)
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True, text=True, env=env, capture_output=False
    )


def ensure_hooks_installed() -> None:
    hook_install.install_hooks(force=False)


def command_commit(args: argparse.Namespace) -> None:
    ensure_hooks_installed()

    paths = args.paths or []
    if paths:
        run_git(["add", *paths])
    else:
        run_git(["add", "."])

    message = args.message.strip()
    if "[git-runner]" not in message:
        message = f"{message}\n\n[git-runner]"
    run_git(["commit", "-m", message])

    if args.push:
        run_git(["push"])


def command_pr(args: argparse.Namespace) -> None:
    ensure_hooks_installed()
    branch = args.branch or os.environ.get("GIT_RUNNER_BRANCH", "(current branch)")
    print("⚠️  PR command stub. Requested branch:", branch)


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Git Runner CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    commit = sub.add_parser("commit", help="Create a commit via Git Runner")
    commit.add_argument("--message", required=True, help="Commit message body")
    commit.add_argument("--paths", nargs="*", help="Paths to stage (defaults to all)")
    commit.add_argument("--push", action="store_true", help="Push after committing")
    commit.set_defaults(func=command_commit)

    pr = sub.add_parser("pr", help="Placeholder for PR workflow")
    pr.add_argument("--branch", help="Branch to raise PR from")
    pr.set_defaults(func=command_pr)

    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    args.func(args)


if __name__ == "__main__":
    main()
