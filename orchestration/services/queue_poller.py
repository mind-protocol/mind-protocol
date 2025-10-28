# SPDX-License-Identifier: Apache-2.0
"""
Queue Poller (Retired)

Historically tailed `.stimuli/queue.jsonl` and forwarded entries to the control
API. The membrane is now the only ingestion surface, so the daemon no longer
runs. Executing this module performs a one-shot migration of any lingering
queue entries to the membrane and then exits.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Iterable

from orchestration.services.signals_collector import (
    ensure_membrane_envelope,
    send_envelope_over_ws,
)

QUEUE = Path(".stimuli/queue.jsonl")
ARCHIVE = Path(".stimuli/queue.jsonl.migrated")


def _load_legacy_queue() -> Iterable[dict]:
    if not QUEUE.exists():
        return []

    try:
        raw_lines = QUEUE.read_text(encoding="utf-8").splitlines()
    except Exception as exc:  # pragma: no cover - filesystem issues
        logging.error("[queue_poller] Unable to read legacy queue: %s", exc)
        return []

    payloads = []
    for idx, raw in enumerate(raw_lines, start=1):
        if not raw.strip():
            continue
        try:
            payloads.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            logging.warning("[queue_poller] Skipping malformed JSON on line %s: %s", idx, exc)
    return payloads


def migrate_queue() -> int:
    """
    Convert legacy queue entries into membrane.inject envelopes.

    Returns number of envelopes published successfully.
    """
    published = 0
    payloads = list(_load_legacy_queue())
    if not payloads:
        logging.info("[queue_poller] No legacy queue entries found")
        return 0

    for payload in payloads:
        envelope = ensure_membrane_envelope(payload)
        if send_envelope_over_ws(envelope):
            published += 1
        else:
            logging.warning("[queue_poller] Publish failed; leaving remaining entries untouched")
            break

    if published:
        try:
            QUEUE.rename(ARCHIVE)
            logging.info("[queue_poller] Legacy queue archived to %s", ARCHIVE)
        except Exception as exc:  # pragma: no cover - rename issues
            logging.warning("[queue_poller] Failed to archive legacy queue: %s", exc)
    return published


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.info(
        "[queue_poller] Service retired — this helper performs a one-time migration "
        "of .stimuli/queue.jsonl entries to the membrane bus."
    )
    published = migrate_queue()
    logging.info("[queue_poller] Migration complete (%s envelopes published)", published)
    return 0


if __name__ == "__main__":
    sys.exit(main())
