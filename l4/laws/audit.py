"""
Compliance audit for L4 ecosystem participants.

DOCS: docs/l4/laws/VALIDATION_Laws.md

Audits an org by sampling its stimuli and running compliance checks.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Callable, Tuple

from .compliance import Stimulus, ComplianceResult, check_stimulus_compliance


@dataclass
class AuditReport:
    """Result of a full compliance audit for an org."""

    org_id: str
    total_checked: int
    compliant_count: int
    violation_counts: Dict[str, int] = field(default_factory=dict)
    results: List[ComplianceResult] = field(default_factory=list)

    @property
    def compliance_rate(self) -> float:
        """Fraction of stimuli that passed compliance (0.0 to 1.0)."""
        if self.total_checked == 0:
            return 1.0
        return self.compliant_count / self.total_checked

    @property
    def is_fully_compliant(self) -> bool:
        return self.compliant_count == self.total_checked


def audit_org(
    org_id: str,
    stimuli: List[Stimulus],
    sender_exists: Callable[[str], bool],
    verify_identity: Callable[[str, str], bool],
) -> AuditReport:
    """
    Run a compliance audit on a list of stimuli from an org.

    The caller is responsible for fetching the stimuli sample.
    This function checks each stimulus and aggregates the results.

    Args:
        org_id: The org being audited.
        stimuli: Sample of stimuli to check.
        sender_exists: Registry lookup callable (see check_stimulus_compliance).
        verify_identity: Hash verification callable (see check_stimulus_compliance).

    Returns:
        AuditReport with per-stimulus results and aggregate violation counts.
    """
    results: List[ComplianceResult] = []
    violation_counts: Dict[str, int] = {}

    for stimulus in stimuli:
        result = check_stimulus_compliance(
            stimulus,
            sender_exists=sender_exists,
            verify_identity=verify_identity,
        )
        results.append(result)

        for violation in result.violations:
            # Extract law ID (e.g. "L1" from "L1: Schema violation...")
            law_id = violation.split(":")[0]
            violation_counts[law_id] = violation_counts.get(law_id, 0) + 1

    compliant_count = sum(1 for r in results if r.compliant)

    return AuditReport(
        org_id=org_id,
        total_checked=len(stimuli),
        compliant_count=compliant_count,
        violation_counts=violation_counts,
        results=results,
    )
