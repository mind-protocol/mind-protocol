"""Protocol-level /call V1 simulator: two-party synchronous decision flow."""

from dataclasses import dataclass
from enum import Enum


class CallOutcome(str, Enum):
    ACCEPTED = "accepted"
    REFUSED = "refused"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class CallResult:
    outcome: CallOutcome
    turns_executed: int
    transcript: list[str]


YES_TOKENS = {"yes", "accept", "accepted", "i accept"}
NO_TOKENS = {"no", "refuse", "refused", "i refuse"}


def _parse_decision(message: str) -> CallOutcome | None:
    lower = message.strip().lower()
    if any(token in lower for token in YES_TOKENS):
        return CallOutcome.ACCEPTED
    if any(token in lower for token in NO_TOKENS):
        return CallOutcome.REFUSED
    return None


def run_call_v1(
    caller_messages: list[str],
    callee_messages: list[str],
    max_turns: int = 6,
) -> CallResult:
    if max_turns < 1:
        raise ValueError("max_turns must be >= 1")

    transcript: list[str] = []
    turns_executed = 0

    for turn in range(max_turns):
        turns_executed += 1
        if turn % 2 == 0:
            index = turn // 2
            message = caller_messages[index] if index < len(caller_messages) else ""
            transcript.append(f"caller: {message}")
            continue

        index = turn // 2
        message = callee_messages[index] if index < len(callee_messages) else ""
        transcript.append(f"callee: {message}")

        decision = _parse_decision(message)
        if decision:
            return CallResult(decision, turns_executed, transcript)

    return CallResult(CallOutcome.TIMEOUT, turns_executed, transcript)
