"""
Append-only ledger for wallet custody operations.

The ledger captures attestations and transfer signatures without exposing
private key material. Each entry is written as a JSON line to the configured
ledger path.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

logger = logging.getLogger(__name__)


@dataclass
class LedgerEntry:
    """Representation of an attested custody action."""

    entry_type: str
    wallet_id: str
    payload: Mapping[str, Any]
    created_at: str

    @classmethod
    def create(
        cls, entry_type: str, wallet_id: str, payload: Mapping[str, Any]
    ) -> "LedgerEntry":
        return cls(
            entry_type=entry_type,
            wallet_id=wallet_id,
            payload=dict(payload),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self))


class Ledger:
    """Simple append-only ledger backed by a JSONL file."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, entry: LedgerEntry) -> None:
        line = entry.to_json()
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        logger.debug("Ledger appended: %s %s", entry.entry_type, entry.wallet_id)
