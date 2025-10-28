# SPDX-License-Identifier: Apache-2.0
"""
Stimulus Injection Service (Retired)

Historically exposed `/inject` over HTTP and wrote to `.stimuli/queue.jsonl` so
auxiliary services could feed the consciousness engines. The membrane now acts
as the sole control surface, so this service has been decommissioned.

Running this module simply logs the deprecation notice to ensure any lingering
supervisor configuration highlights the new workflow instead of silently
failing.
"""

from __future__ import annotations

import logging
import sys

NOTICE = (
    "[stimulus_injection] Service retired — publish `membrane.inject` envelopes "
    "over ws://127.0.0.1:8000/api/ws instead of calling /inject."
)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.warning(NOTICE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
