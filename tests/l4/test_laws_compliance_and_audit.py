"""
Tests for L4 Laws: compliance checking and audit.

DOCS: docs/l4/laws/VALIDATION_Laws.md

Covers all 9 validation invariants:
- V1: Schema compliance (all nodes/links pass validation)
- V2: Registered senders (sender_id exists in registry)
- V3: No direct DB access (architecture — structural assertion)
- V4: Membrane routing (architecture — structural assertion)
- V5: No raw JWT in stimulus payload
- V6: Valid identity hash
- V7: Receiver consent (structural — acceptance flag present)
- V8: Fees paid (>= 1% of value on cross-org)
- V9: WebSocket only (architecture — structural assertion)
"""

import base64
import json

import pytest

from l4.laws import (
    Stimulus,
    ComplianceResult,
    check_stimulus_compliance,
    AuditReport,
    audit_org,
    LAWS,
    MIN_FEE_RATE,
    MAX_FEE_RATE,
    REQUIRED_SCHEMA_VERSION,
)
from l4.schema import SCHEMA_VERSION, NodeType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_valid_node(node_id: str = "node_1", node_type: str = "actor") -> dict:
    """Build a minimal valid node dict."""
    return {
        "id": node_id,
        "name": f"Test {node_id}",
        "node_type": node_type,
        "synthesis": f"Test node {node_id}",
    }


def _make_valid_link(link_id: str = "link_1") -> dict:
    """Build a minimal valid link dict."""
    return {
        "id": link_id,
        "node_a": "node_a",
        "node_b": "node_b",
    }


def _make_test_jwt() -> str:
    """Create a realistic-looking JWT string (header.payload.signature)."""
    header = base64.urlsafe_b64encode(
        json.dumps({"typ": "JWT", "alg": "RS256"}).encode()
    ).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(
        json.dumps({"sub": "citizen_abc", "iss": "org_1"}).encode()
    ).rstrip(b"=").decode()
    return f"{header}.{payload}.fake_signature_data"


def _sender_exists_true(sender_id: str) -> bool:
    return True


def _sender_exists_false(sender_id: str) -> bool:
    return False


def _verify_identity_true(identity_hash: str, sender_id: str) -> bool:
    return True


def _verify_identity_false(identity_hash: str, sender_id: str) -> bool:
    return False


def _make_compliant_stimulus() -> Stimulus:
    """Build a fully compliant same-org stimulus."""
    return Stimulus(
        sender_id="citizen_abc123",
        identity_hash="a1b2c3d4e5f6",
        nodes=[_make_valid_node()],
        links=[_make_valid_link()],
        source_org="org_1",
        target_org="org_1",
        fee=0.0,
        value=100.0,
    )


def _make_cross_org_stimulus(fee: float = 1.0, value: float = 100.0) -> Stimulus:
    """Build a cross-org stimulus with the given fee and value."""
    return Stimulus(
        sender_id="citizen_abc123",
        identity_hash="a1b2c3d4e5f6",
        nodes=[_make_valid_node()],
        links=[_make_valid_link()],
        source_org="org_1",
        target_org="org_2",
        fee=fee,
        value=value,
    )


# ===========================================================================
# Constants
# ===========================================================================


class TestLawConstants:
    """Test law definitions and fee constraints."""

    def test_laws_has_8_entries(self):
        assert len(LAWS) == 8

    def test_laws_keys_are_l1_through_l8(self):
        expected = {f"L{i}" for i in range(1, 9)}
        assert set(LAWS.keys()) == expected

    def test_fee_rates(self):
        assert MIN_FEE_RATE == 0.01
        assert MAX_FEE_RATE == 0.05
        assert MIN_FEE_RATE < MAX_FEE_RATE

    def test_required_schema_version_matches_current(self):
        assert REQUIRED_SCHEMA_VERSION == SCHEMA_VERSION


# ===========================================================================
# V1: Schema Compliance
# ===========================================================================


class TestV1SchemaCompliance:
    """V1: All nodes/links in a stimulus must pass schema validation."""

    def test_valid_nodes_pass(self):
        stimulus = _make_compliant_stimulus()
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        assert result.compliant
        assert result.violations == []

    def test_invalid_node_type_fails(self):
        stimulus = Stimulus(
            sender_id="citizen_abc",
            identity_hash="hash123",
            nodes=[{
                "id": "bad_node",
                "name": "Bad",
                "node_type": "invalid_type",
                "synthesis": "Bad node",
            }],
            links=[],
            source_org="org_1",
            target_org="org_1",
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        assert not result.compliant
        l1_violations = [v for v in result.violations if v.startswith("L1")]
        assert len(l1_violations) > 0

    def test_node_missing_required_field_fails(self):
        stimulus = Stimulus(
            sender_id="citizen_abc",
            identity_hash="hash123",
            nodes=[{"id": "no_type"}],  # missing node_type
            links=[],
            source_org="org_1",
            target_org="org_1",
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        assert not result.compliant
        l1_violations = [v for v in result.violations if v.startswith("L1")]
        assert len(l1_violations) > 0

    def test_invalid_link_fails(self):
        stimulus = Stimulus(
            sender_id="citizen_abc",
            identity_hash="hash123",
            nodes=[],
            links=[{"id": "bad_link"}],  # missing node_a, node_b
            source_org="org_1",
            target_org="org_1",
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        assert not result.compliant
        l1_violations = [v for v in result.violations if v.startswith("L1")]
        assert len(l1_violations) > 0

    def test_multiple_schema_errors_all_reported(self):
        stimulus = Stimulus(
            sender_id="citizen_abc",
            identity_hash="hash123",
            nodes=[
                {"id": "bad1", "name": "B1", "node_type": "invalid", "synthesis": "x"},
                {"id": "bad2"},  # missing node_type
            ],
            links=[],
            source_org="org_1",
            target_org="org_1",
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        assert not result.compliant
        l1_violations = [v for v in result.violations if v.startswith("L1")]
        assert len(l1_violations) >= 2

    def test_empty_payload_passes_schema(self):
        stimulus = Stimulus(
            sender_id="citizen_abc",
            identity_hash="hash123",
            nodes=[],
            links=[],
            source_org="org_1",
            target_org="org_1",
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        # No schema violations (no nodes/links to validate)
        l1_violations = [v for v in result.violations if v.startswith("L1")]
        assert l1_violations == []

    def test_all_five_node_types_pass(self):
        """All 5 canonical node types must be accepted."""
        nodes = [
            _make_valid_node("n1", "actor"),
            _make_valid_node("n2", "moment"),
            _make_valid_node("n3", "narrative"),
            _make_valid_node("n4", "space"),
            _make_valid_node("n5", "thing"),
        ]
        stimulus = Stimulus(
            sender_id="citizen_abc",
            identity_hash="hash123",
            nodes=nodes,
            links=[],
            source_org="org_1",
            target_org="org_1",
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l1_violations = [v for v in result.violations if v.startswith("L1")]
        assert l1_violations == []


# ===========================================================================
# V2: Registered Senders
# ===========================================================================


class TestV2RegisteredSenders:
    """V2: stimulus.sender_id must exist in the registry."""

    def test_registered_sender_passes(self):
        stimulus = _make_compliant_stimulus()
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l2_violations = [v for v in result.violations if v.startswith("L2")]
        assert l2_violations == []

    def test_unregistered_sender_fails(self):
        stimulus = _make_compliant_stimulus()
        result = check_stimulus_compliance(
            stimulus, _sender_exists_false, _verify_identity_true
        )
        assert not result.compliant
        l2_violations = [v for v in result.violations if v.startswith("L2")]
        assert len(l2_violations) == 1
        assert "not registered" in l2_violations[0]

    def test_sender_id_included_in_violation_message(self):
        stimulus = Stimulus(
            sender_id="citizen_unknown_999",
            identity_hash="hash123",
            source_org="org_1",
            target_org="org_1",
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_false, _verify_identity_true
        )
        l2_violations = [v for v in result.violations if v.startswith("L2")]
        assert "citizen_unknown_999" in l2_violations[0]


# ===========================================================================
# V3 / V4: Architecture-enforced (No direct DB, Membrane routing)
# ===========================================================================


class TestV3V4ArchitecturalLaws:
    """V3 and V4 are enforced by architecture, not runtime code.

    These tests verify the structural assertion: L3, L4 exist as law
    definitions but have no runtime compliance check (by design).
    """

    def test_l3_exists_in_law_definitions(self):
        assert "L3" in LAWS
        assert "DB" in LAWS["L3"] or "direct" in LAWS["L3"].lower()

    def test_l4_exists_in_law_definitions(self):
        assert "L4" in LAWS
        assert "membrane" in LAWS["L4"].lower()

    def test_no_l3_or_l4_violations_in_compliance_check(self):
        """Compliance checker must never produce L3 or L4 violations."""
        stimulus = _make_compliant_stimulus()
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        for v in result.violations:
            assert not v.startswith("L3"), "L3 is architectural, not runtime"
            assert not v.startswith("L4"), "L4 is architectural, not runtime"


# ===========================================================================
# V5: No Raw JWT in Stimulus
# ===========================================================================


class TestV5NoRawJWT:
    """V5: No raw JWT token must appear in any stimulus payload field."""

    def test_clean_stimulus_passes(self):
        stimulus = _make_compliant_stimulus()
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l5_violations = [v for v in result.violations if "L5" in v and "JWT" in v]
        assert l5_violations == []

    def test_jwt_in_node_content_detected(self):
        jwt = _make_test_jwt()
        stimulus = Stimulus(
            sender_id="citizen_abc",
            identity_hash="hash123",
            nodes=[{
                "id": "leaked",
                "name": "Leaked",
                "node_type": "narrative",
                "synthesis": "some synthesis",
                "content": f"Here is my token: {jwt}",
            }],
            links=[],
            source_org="org_1",
            target_org="org_1",
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l5_jwt = [v for v in result.violations if "L5" in v and "JWT" in v]
        assert len(l5_jwt) >= 1

    def test_jwt_in_node_synthesis_detected(self):
        jwt = _make_test_jwt()
        stimulus = Stimulus(
            sender_id="citizen_abc",
            identity_hash="hash123",
            nodes=[{
                "id": "leaked",
                "name": "Leaked",
                "node_type": "narrative",
                "synthesis": f"token: {jwt}",
                "content": "clean content",
            }],
            links=[],
            source_org="org_1",
            target_org="org_1",
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l5_jwt = [v for v in result.violations if "L5" in v and "JWT" in v]
        assert len(l5_jwt) >= 1

    def test_jwt_in_link_synthesis_detected(self):
        jwt = _make_test_jwt()
        stimulus = Stimulus(
            sender_id="citizen_abc",
            identity_hash="hash123",
            nodes=[],
            links=[{
                "id": "leaked_link",
                "node_a": "a",
                "node_b": "b",
                "synthesis": f"contains jwt: {jwt}",
            }],
            source_org="org_1",
            target_org="org_1",
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l5_jwt = [v for v in result.violations if "L5" in v and "JWT" in v]
        assert len(l5_jwt) >= 1

    def test_non_jwt_dotted_string_not_flagged(self):
        """Version strings like '1.8.1' must not trigger the JWT detector."""
        stimulus = Stimulus(
            sender_id="citizen_abc",
            identity_hash="hash123",
            nodes=[{
                "id": "version_node",
                "name": "Version",
                "node_type": "narrative",
                "synthesis": "schema version 1.8.1",
                "content": "Compatible with v1.8.1",
            }],
            links=[],
            source_org="org_1",
            target_org="org_1",
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l5_jwt = [v for v in result.violations if "L5" in v and "JWT" in v]
        assert l5_jwt == []

    def test_hash_only_string_not_flagged(self):
        """A SHA256 hex hash must not trigger the JWT detector."""
        stimulus = Stimulus(
            sender_id="citizen_abc",
            identity_hash="hash123",
            nodes=[{
                "id": "hash_node",
                "name": "Hash",
                "node_type": "narrative",
                "synthesis": "identity hash for verification",
                "content": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6abcd",
            }],
            links=[],
            source_org="org_1",
            target_org="org_1",
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l5_jwt = [v for v in result.violations if "L5" in v and "JWT" in v]
        assert l5_jwt == []


# ===========================================================================
# V6: Valid Identity Hash
# ===========================================================================


class TestV6ValidHash:
    """V6: Identity hash must match registered identity."""

    def test_valid_hash_passes(self):
        stimulus = _make_compliant_stimulus()
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l5_hash = [v for v in result.violations if "L5" in v and "hash" in v.lower()]
        assert l5_hash == []

    def test_invalid_hash_fails(self):
        stimulus = _make_compliant_stimulus()
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_false
        )
        assert not result.compliant
        l5_hash = [v for v in result.violations if "L5" in v and "hash" in v.lower()]
        assert len(l5_hash) == 1


# ===========================================================================
# V7: Receiver Consent (Structural)
# ===========================================================================


class TestV7ReceiverConsent:
    """V7: Cross-org stimulus requires explicit receiver acceptance.

    Receiver validation (L6) is enforced by the receiver's code, not
    by the compliance checker. This test verifies L6 exists as a law
    and that no runtime L6 violations are produced.
    """

    def test_l6_exists_in_law_definitions(self):
        assert "L6" in LAWS
        assert "receiver" in LAWS["L6"].lower() or "validates" in LAWS["L6"].lower()

    def test_no_l6_violations_in_compliance_check(self):
        """Compliance checker does not enforce L6 — receivers do."""
        stimulus = _make_cross_org_stimulus(fee=1.0, value=100.0)
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l6_violations = [v for v in result.violations if v.startswith("L6")]
        assert l6_violations == []


# ===========================================================================
# V8: Fees Paid
# ===========================================================================


class TestV8FeesPaid:
    """V8: Cross-org transactions must pay >= 1% of transaction value."""

    def test_exact_minimum_fee_passes(self):
        value = 100.0
        fee = value * MIN_FEE_RATE  # exactly 1%
        stimulus = _make_cross_org_stimulus(fee=fee, value=value)
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l7_violations = [v for v in result.violations if v.startswith("L7")]
        assert l7_violations == []

    def test_fee_above_minimum_passes(self):
        stimulus = _make_cross_org_stimulus(fee=5.0, value=100.0)
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l7_violations = [v for v in result.violations if v.startswith("L7")]
        assert l7_violations == []

    def test_fee_below_minimum_fails(self):
        stimulus = _make_cross_org_stimulus(fee=0.5, value=100.0)  # 0.5% < 1%
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        assert not result.compliant
        l7_violations = [v for v in result.violations if v.startswith("L7")]
        assert len(l7_violations) == 1

    def test_zero_fee_on_cross_org_fails(self):
        stimulus = _make_cross_org_stimulus(fee=0.0, value=100.0)
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l7_violations = [v for v in result.violations if v.startswith("L7")]
        assert len(l7_violations) == 1

    def test_same_org_no_fee_required(self):
        """Same-org stimuli do not require fees."""
        stimulus = Stimulus(
            sender_id="citizen_abc",
            identity_hash="hash123",
            nodes=[_make_valid_node()],
            links=[],
            source_org="org_1",
            target_org="org_1",  # same org
            fee=0.0,
            value=1000.0,
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l7_violations = [v for v in result.violations if v.startswith("L7")]
        assert l7_violations == []

    def test_zero_value_cross_org_no_fee_required(self):
        """Zero-value cross-org stimulus: min fee = 0, so fee=0 is fine."""
        stimulus = _make_cross_org_stimulus(fee=0.0, value=0.0)
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l7_violations = [v for v in result.violations if v.startswith("L7")]
        assert l7_violations == []

    def test_large_value_requires_proportional_fee(self):
        value = 10_000.0
        bad_fee = value * MIN_FEE_RATE - 0.01  # just under 1%
        stimulus = _make_cross_org_stimulus(fee=bad_fee, value=value)
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l7_violations = [v for v in result.violations if v.startswith("L7")]
        assert len(l7_violations) == 1


# ===========================================================================
# V9: WebSocket Only (Structural)
# ===========================================================================


class TestV9WebSocketOnly:
    """V9: L4 API has no REST endpoints.

    This is enforced by architecture (API design), not runtime compliance.
    """

    def test_l8_exists_in_law_definitions(self):
        assert "L8" in LAWS
        assert "websocket" in LAWS["L8"].lower()

    def test_no_l8_violations_in_compliance_check(self):
        stimulus = _make_compliant_stimulus()
        result = check_stimulus_compliance(
            stimulus, _sender_exists_true, _verify_identity_true
        )
        l8_violations = [v for v in result.violations if v.startswith("L8")]
        assert l8_violations == []


# ===========================================================================
# ComplianceResult
# ===========================================================================


class TestComplianceResult:
    """Test ComplianceResult dataclass behavior."""

    def test_compliant_result(self):
        result = ComplianceResult(compliant=True, violations=[])
        assert result.compliant
        assert result.violations == []

    def test_non_compliant_result(self):
        result = ComplianceResult(
            compliant=False, violations=["L1: bad node"]
        )
        assert not result.compliant
        assert len(result.violations) == 1

    def test_multiple_violations(self):
        result = ComplianceResult(
            compliant=False,
            violations=["L1: bad node", "L2: unknown sender", "L7: fee too low"],
        )
        assert not result.compliant
        assert len(result.violations) == 3


# ===========================================================================
# Stimulus dataclass
# ===========================================================================


class TestStimulusDataclass:
    """Test Stimulus dataclass defaults and construction."""

    def test_defaults(self):
        s = Stimulus(sender_id="abc", identity_hash="hash")
        assert s.nodes == []
        assert s.links == []
        assert s.source_org == ""
        assert s.target_org == ""
        assert s.fee == 0.0
        assert s.value == 0.0

    def test_full_construction(self):
        s = Stimulus(
            sender_id="citizen_1",
            identity_hash="deadbeef",
            nodes=[_make_valid_node()],
            links=[_make_valid_link()],
            source_org="org_a",
            target_org="org_b",
            fee=5.0,
            value=100.0,
        )
        assert s.sender_id == "citizen_1"
        assert len(s.nodes) == 1
        assert len(s.links) == 1
        assert s.source_org == "org_a"


# ===========================================================================
# Combined violations
# ===========================================================================


class TestMultipleLawViolations:
    """Test that violations from different laws accumulate correctly."""

    def test_schema_and_sender_violations_both_reported(self):
        stimulus = Stimulus(
            sender_id="unknown_citizen",
            identity_hash="hash123",
            nodes=[{"id": "bad"}],  # missing node_type → L1
            links=[],
            source_org="org_1",
            target_org="org_1",
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_false, _verify_identity_true
        )
        assert not result.compliant
        law_ids = {v.split(":")[0] for v in result.violations}
        assert "L1" in law_ids
        assert "L2" in law_ids

    def test_all_enforceable_laws_can_fail_together(self):
        jwt = _make_test_jwt()
        stimulus = Stimulus(
            sender_id="unknown",
            identity_hash="wrong_hash",
            nodes=[{
                "id": "bad_node",
                "content": f"jwt={jwt}",
            }],  # L1: missing fields, L5: JWT leak
            links=[],
            source_org="org_1",
            target_org="org_2",  # cross-org
            fee=0.0,  # L7: no fee
            value=100.0,
        )
        result = check_stimulus_compliance(
            stimulus, _sender_exists_false, _verify_identity_false
        )
        assert not result.compliant
        law_ids = {v.split(":")[0] for v in result.violations}
        assert "L1" in law_ids  # schema
        assert "L2" in law_ids  # unregistered
        assert "L5" in law_ids  # JWT and/or hash
        assert "L7" in law_ids  # fee


# ===========================================================================
# Audit
# ===========================================================================


class TestAuditOrg:
    """Test full compliance audit for an org."""

    def test_all_compliant(self):
        stimuli = [_make_compliant_stimulus() for _ in range(5)]
        report = audit_org(
            "org_1", stimuli, _sender_exists_true, _verify_identity_true
        )
        assert report.org_id == "org_1"
        assert report.total_checked == 5
        assert report.compliant_count == 5
        assert report.is_fully_compliant
        assert report.compliance_rate == 1.0
        assert report.violation_counts == {}

    def test_some_violations(self):
        good = _make_compliant_stimulus()
        bad = Stimulus(
            sender_id="unknown",
            identity_hash="hash",
            nodes=[],
            links=[],
            source_org="org_1",
            target_org="org_1",
        )
        stimuli = [good, bad, good]
        report = audit_org(
            "org_1", stimuli, _sender_exists_false, _verify_identity_true
        )
        # All 3 fail L2 because sender_exists always returns False
        assert report.total_checked == 3
        assert report.compliant_count == 0
        assert not report.is_fully_compliant
        assert report.compliance_rate == 0.0
        assert "L2" in report.violation_counts

    def test_mixed_compliance_with_selective_lookup(self):
        """Use a selective sender_exists that only recognizes some senders."""
        known_senders = {"citizen_abc123"}

        def selective_lookup(sender_id: str) -> bool:
            return sender_id in known_senders

        known_stimulus = _make_compliant_stimulus()  # sender_id = citizen_abc123
        unknown_stimulus = Stimulus(
            sender_id="citizen_unknown",
            identity_hash="hash",
            nodes=[_make_valid_node()],
            links=[],
            source_org="org_1",
            target_org="org_1",
        )

        stimuli = [known_stimulus, unknown_stimulus]
        report = audit_org(
            "org_1", stimuli, selective_lookup, _verify_identity_true
        )
        assert report.total_checked == 2
        assert report.compliant_count == 1
        assert report.compliance_rate == 0.5

    def test_empty_audit(self):
        report = audit_org(
            "org_1", [], _sender_exists_true, _verify_identity_true
        )
        assert report.total_checked == 0
        assert report.compliant_count == 0
        assert report.is_fully_compliant
        assert report.compliance_rate == 1.0  # vacuously true

    def test_violation_counts_aggregate(self):
        """Multiple violations of the same law get counted."""
        bad_stimuli = [
            Stimulus(
                sender_id=f"unknown_{i}",
                identity_hash="hash",
                nodes=[],
                links=[],
                source_org="org_1",
                target_org="org_1",
            )
            for i in range(3)
        ]
        report = audit_org(
            "org_1", bad_stimuli, _sender_exists_false, _verify_identity_true
        )
        assert report.violation_counts.get("L2", 0) == 3

    def test_audit_results_list_matches_stimuli(self):
        stimuli = [_make_compliant_stimulus() for _ in range(3)]
        report = audit_org(
            "org_1", stimuli, _sender_exists_true, _verify_identity_true
        )
        assert len(report.results) == 3
        for r in report.results:
            assert isinstance(r, ComplianceResult)
            assert r.compliant

    def test_cross_org_fee_violation_in_audit(self):
        """Audit catches L7 fee violations."""
        stimulus = _make_cross_org_stimulus(fee=0.0, value=500.0)
        report = audit_org(
            "org_1", [stimulus], _sender_exists_true, _verify_identity_true
        )
        assert not report.is_fully_compliant
        assert "L7" in report.violation_counts


# ===========================================================================
# AuditReport dataclass
# ===========================================================================


class TestAuditReportDataclass:
    """Test AuditReport properties."""

    def test_compliance_rate_partial(self):
        report = AuditReport(
            org_id="org_1",
            total_checked=10,
            compliant_count=7,
        )
        assert report.compliance_rate == 0.7

    def test_is_fully_compliant_true(self):
        report = AuditReport(
            org_id="org_1",
            total_checked=5,
            compliant_count=5,
        )
        assert report.is_fully_compliant

    def test_is_fully_compliant_false(self):
        report = AuditReport(
            org_id="org_1",
            total_checked=5,
            compliant_count=4,
        )
        assert not report.is_fully_compliant
