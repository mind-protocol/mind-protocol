"""Law integration primitives."""
from __future__ import annotations

from typing import Callable, Iterable


def implements(*ids: str) -> Callable[[Callable], Callable]:
    """Attach L4 identifiers to a callable or class."""

    def deco(obj: Callable) -> Callable:
        setattr(obj, "__l4_ids__", tuple(ids))
        return obj

    return deco


def iter_implements(collection: Iterable[Callable]) -> Iterable[tuple[Callable, tuple[str, ...]]]:
    for item in collection:
        identifiers = getattr(item, "__l4_ids__", None)
        if identifiers:
            yield item, tuple(identifiers)
