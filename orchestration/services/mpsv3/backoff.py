"""
MPSv3 Backoff State - Exponential backoff with quarantine.

Prevents crash loops by increasing delay between restart attempts.
Quarantines services that exceed max retries.

Author: Atlas
Date: 2025-10-25
"""

import random


class QuarantineRequired(Exception):
    """Raised when service exceeds max retries and should be quarantined."""
    pass


class BackoffState:
    """Exponential backoff with jitter and quarantine."""

    def __init__(self, max_retries: int = 5):
        self.attempts = 0
        self.max_retries = max_retries
        self.base_delay = 1.0  # seconds
        self.max_delay = 60.0
        self.jitter = 0.2  # ±20%

    def next_delay(self) -> float:
        """Calculate next delay with exponential backoff and jitter.

        Raises QuarantineRequired if max retries exceeded.
        """
        if self.attempts >= self.max_retries:
            raise QuarantineRequired(f"Exceeded {self.max_retries} attempts")

        # Exponential: 1s, 2s, 4s, 8s, 16s, 32s, max 60s
        delay = min(self.base_delay * (2 ** self.attempts), self.max_delay)

        # Add jitter to prevent thundering herd
        jitter_amount = random.uniform(-self.jitter * delay, self.jitter * delay)
        delay_with_jitter = max(0.1, delay + jitter_amount)  # Minimum 0.1s

        self.attempts += 1
        return delay_with_jitter

    def reset(self):
        """Reset backoff counter (after successful start or clean exit)."""
        self.attempts = 0
