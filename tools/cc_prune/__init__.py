"""Repo pruning helper CLI."""

__all__ = [
    "main",
]


def main() -> None:
    from .cli import main as _main

    _main()
