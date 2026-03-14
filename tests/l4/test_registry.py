"""
Tests for L4 Registry module.

DOCS: docs/l4/registry/VALIDATION_Registry.md
"""

import pytest
import base64
import json
import time
from l4.registry import (
    # Citizen
    CitizenRegistration,
    CitizenRecord,
    generate_citizen_id,
    hash_jwt,
    create_citizen_nodes,
    citizen_to_record,
    # Org
    OrgRegistration,
    OrgRecord,
    generate_org_id,
    create_org_nodes,
    org_to_record,
    # Endpoint
    EndpointValidationResult,
    validate_endpoint_url,
    create_endpoint_node,
    update_endpoint_url,
    # Hash verification
    VerificationStatus,
    VerificationResult,
    compute_hash,
    verify_hash,
    create_verification_hash,
    # JWT signature verification
    JWTVerificationStatus,
    JWTVerificationResult,
    decode_jwt_parts,
    verify_jwt_claims,
    verify_jwt_signature,
    # Combined routing verification
    RoutingVerificationResult,
    verify_and_get_endpoint,
)
from l4.schema import ActorNode, SpaceNode, ThingNode, NarrativeNode, LinkBase


def make_test_jwt(payload: dict, header: dict = None) -> str:
    """Create a test JWT token (unsigned, for testing format)."""
    if header is None:
        header = {"typ": "JWT", "alg": "RS256"}

    def b64encode(data):
        return base64.urlsafe_b64encode(
            json.dumps(data).encode()
        ).rstrip(b"=").decode()

    return f"{b64encode(header)}.{b64encode(payload)}.fake_signature"


class TestCitizenRegistration:
    """Tests for citizen registration."""

    def test_generate_citizen_id_format(self):
        """Citizen IDs should have correct format."""
        cid = generate_citizen_id()
        assert cid.startswith("citizen_")
        assert len(cid) == len("citizen_") + 12

    def test_generate_citizen_id_unique(self):
        """Each generated ID should be unique."""
        ids = [generate_citizen_id() for _ in range(100)]
        assert len(set(ids)) == 100

    def test_hash_jwt(self):
        """JWT hashing should be deterministic."""
        jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test"
        hash1 = hash_jwt(jwt)
        hash2 = hash_jwt(jwt)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex

    def test_create_citizen_nodes_basic(self):
        """Create citizen nodes with minimal data."""
        test_jwt = make_test_jwt({"sub": "test", "iss": "org_test123"})
        reg = CitizenRegistration(
            name="Test Citizen",
            org_id="org_test123",
            jwt=test_jwt,
        )

        citizen_node, property_nodes, links, identity_hash = create_citizen_nodes(reg)

        # Check main node
        assert isinstance(citizen_node, ActorNode)
        assert citizen_node.type == "citizen"
        assert citizen_node.name == "Test Citizen"
        assert "org_test123" in citizen_node.synthesis

        # Check property nodes exist
        assert len(property_nodes) >= 5  # name, org, status, registered_date, identity_hash
        types = [n.type for n in property_nodes if hasattr(n, 'type')]
        assert "name" in types
        assert "org_membership" in types
        assert "status" in types
        assert "registered_date" in types
        assert "identity_hash" in types

        # Check identity hash node has correct content
        hash_nodes = [n for n in property_nodes if hasattr(n, 'type') and n.type == "identity_hash"]
        assert len(hash_nodes) == 1
        assert hash_nodes[0].content == identity_hash

        # Check links
        assert len(links) >= 5

    def test_create_citizen_nodes_with_wallet(self):
        """Create citizen nodes with wallet."""
        test_jwt = make_test_jwt({"sub": "test"})
        reg = CitizenRegistration(
            name="Wallet Citizen",
            org_id="org_test123",
            jwt=test_jwt,
            wallet="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        )

        citizen_node, property_nodes, links, _ = create_citizen_nodes(reg)

        # Check wallet node exists
        wallet_nodes = [n for n in property_nodes if hasattr(n, 'type') and n.type == "wallet"]
        assert len(wallet_nodes) == 1
        assert wallet_nodes[0].content == reg.wallet

    def test_create_citizen_nodes_with_capabilities(self):
        """Create citizen nodes with capabilities."""
        test_jwt = make_test_jwt({"sub": "test"})
        reg = CitizenRegistration(
            name="Capable Citizen",
            org_id="org_test123",
            jwt=test_jwt,
            capabilities=["read", "write", "admin"],
        )

        citizen_node, property_nodes, links, _ = create_citizen_nodes(reg)

        # Check capabilities node exists
        cap_nodes = [n for n in property_nodes if hasattr(n, 'type') and n.type == "capabilities"]
        assert len(cap_nodes) == 1
        assert "read" in cap_nodes[0].content
        assert "write" in cap_nodes[0].content
        assert "admin" in cap_nodes[0].content

    def test_create_citizen_with_custom_id(self):
        """Create citizen with specified ID."""
        test_jwt = make_test_jwt({"sub": "test"})
        reg = CitizenRegistration(
            name="Custom ID",
            org_id="org_test",
            jwt=test_jwt,
        )

        citizen_node, _, _, _ = create_citizen_nodes(reg, citizen_id="citizen_custom123")
        assert citizen_node.id == "citizen_custom123"

    def test_identity_hash_deterministic(self):
        """Identity hash should be deterministic for same JWT and citizen_id."""
        test_jwt = make_test_jwt({"sub": "test"})
        reg = CitizenRegistration(
            name="Hash Test",
            org_id="org_test",
            jwt=test_jwt,
        )

        _, _, _, hash1 = create_citizen_nodes(reg, citizen_id="citizen_test123")
        _, _, _, hash2 = create_citizen_nodes(reg, citizen_id="citizen_test123")
        assert hash1 == hash2

    def test_identity_hash_different_for_different_ids(self):
        """Identity hash should differ for different citizen IDs."""
        test_jwt = make_test_jwt({"sub": "test"})
        reg = CitizenRegistration(
            name="Hash Test",
            org_id="org_test",
            jwt=test_jwt,
        )

        _, _, _, hash1 = create_citizen_nodes(reg, citizen_id="citizen_test1")
        _, _, _, hash2 = create_citizen_nodes(reg, citizen_id="citizen_test2")
        assert hash1 != hash2


class TestOrgRegistration:
    """Tests for org registration."""

    def test_generate_org_id_format(self):
        """Org IDs should have correct format."""
        oid = generate_org_id()
        assert oid.startswith("org_")
        assert len(oid) == len("org_") + 12

    def test_generate_org_id_unique(self):
        """Each generated ID should be unique."""
        ids = [generate_org_id() for _ in range(100)]
        assert len(set(ids)) == 100

    def test_create_org_nodes_basic(self):
        """Create org nodes with required data."""
        reg = OrgRegistration(
            name="Test Org",
            org_type="project",
            wallet="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
            endpoint_url="wss://api.testorg.com/ws",
            jwt_public_key="-----BEGIN PUBLIC KEY-----\nMIIBIjAN...",
        )

        org_node, property_nodes, links = create_org_nodes(reg)

        # Check main node
        assert isinstance(org_node, SpaceNode)
        assert org_node.type == "org"
        assert org_node.name == "Test Org"

        # Check required property nodes
        types = [n.type for n in property_nodes if hasattr(n, 'type')]
        assert "name" in types
        assert "org_type" in types
        assert "universe" in types
        assert "status" in types
        assert "registered_date" in types
        assert "wallet" in types
        assert "endpoint" in types
        assert "jwt_public_key" in types

        # Check links
        assert len(links) == len(property_nodes)

    def test_org_node_is_space_type(self):
        """Org should be a space node, not actor."""
        reg = OrgRegistration(
            name="Space Org",
            org_type="community",
            wallet="wallet123",
            endpoint_url="wss://test.com/ws",
            jwt_public_key="key123",
        )

        org_node, _, _ = create_org_nodes(reg)
        assert org_node.node_type.value == "space"


class TestEndpointValidation:
    """Tests for endpoint URL validation."""

    def test_valid_wss_url(self):
        """Valid wss:// URLs should pass."""
        result = validate_endpoint_url("wss://api.example.com/ws")
        assert result.is_valid
        assert result.error is None

    def test_valid_wss_url_with_port(self):
        """Valid wss:// URLs with port should pass."""
        result = validate_endpoint_url("wss://api.example.com:8080/ws")
        assert result.is_valid

    def test_invalid_ws_url(self):
        """Non-secure ws:// should fail."""
        result = validate_endpoint_url("ws://api.example.com/ws")
        assert not result.is_valid
        assert "wss://" in result.error

    def test_invalid_http_url(self):
        """HTTP URLs should fail."""
        result = validate_endpoint_url("https://api.example.com/ws")
        assert not result.is_valid

    def test_empty_url(self):
        """Empty URL should fail."""
        result = validate_endpoint_url("")
        assert not result.is_valid
        assert "required" in result.error.lower()

    def test_create_endpoint_node_valid(self):
        """Creating endpoint with valid URL should succeed."""
        node = create_endpoint_node("org_test", "wss://test.com/ws")
        assert isinstance(node, ThingNode)
        assert node.type == "endpoint"
        assert node.uri == "wss://test.com/ws"

    def test_create_endpoint_node_invalid(self):
        """Creating endpoint with invalid URL should raise."""
        with pytest.raises(ValueError):
            create_endpoint_node("org_test", "http://invalid.com")


class TestHashVerification:
    """Tests for hash verification."""

    def test_compute_hash_deterministic(self):
        """Hash computation should be deterministic."""
        jwt = "test_jwt_token"
        node_id = "citizen_123"

        hash1 = compute_hash(jwt, node_id)
        hash2 = compute_hash(jwt, node_id)
        assert hash1 == hash2

    def test_compute_hash_different_inputs(self):
        """Different inputs should produce different hashes."""
        jwt = "test_jwt"

        hash1 = compute_hash(jwt, "node_1")
        hash2 = compute_hash(jwt, "node_2")
        assert hash1 != hash2

    def test_compute_hash_length(self):
        """Hash should be SHA256 hex (64 chars)."""
        h = compute_hash("jwt", "node")
        assert len(h) == 64

    def test_create_verification_hash(self):
        """Verification hash should match compute_hash."""
        jwt = "my_jwt"
        cid = "citizen_abc"

        vh = create_verification_hash(jwt, cid)
        ch = compute_hash(jwt, cid)
        assert vh == ch

    def test_verify_hash_not_found(self):
        """Verification should fail if node not in registry."""
        def lookup(node_id):
            return None  # Not found

        result = verify_hash("somehash", "node_123", lookup)
        assert result.status == VerificationStatus.NOT_FOUND
        assert not result.is_valid

    def test_verify_hash_valid(self):
        """Verification should succeed with matching hash."""
        expected_hash = "abc123"

        def lookup(node_id):
            return (expected_hash, "org_123", "active")

        result = verify_hash(expected_hash, "node_123", lookup)
        assert result.status == VerificationStatus.VALID
        assert result.is_valid
        assert result.org_id == "org_123"

    def test_verify_hash_invalid(self):
        """Verification should fail with non-matching hash."""
        def lookup(node_id):
            return ("different_hash", "org_123", "active")

        result = verify_hash("wrong_hash", "node_123", lookup)
        assert result.status == VerificationStatus.INVALID
        assert not result.is_valid

    def test_verify_hash_suspended(self):
        """Verification should fail for suspended entities."""
        def lookup(node_id):
            return ("correct_hash", "org_123", "suspended")

        result = verify_hash("correct_hash", "node_123", lookup)
        assert result.status == VerificationStatus.SUSPENDED
        assert not result.is_valid


class TestVerificationResult:
    """Tests for VerificationResult."""

    def test_is_valid_property(self):
        """is_valid should be True only for VALID status."""
        valid = VerificationResult(status=VerificationStatus.VALID)
        assert valid.is_valid

        invalid = VerificationResult(status=VerificationStatus.INVALID)
        assert not invalid.is_valid

        not_found = VerificationResult(status=VerificationStatus.NOT_FOUND)
        assert not not_found.is_valid


class TestLinkProperties:
    """Tests for link properties in registry nodes."""

    def test_citizen_link_hierarchy(self):
        """Citizen property links should have hierarchy=1.0 (property belongs to citizen)."""
        test_jwt = make_test_jwt({"sub": "test"})
        reg = CitizenRegistration(
            name="Test",
            org_id="org_1",
            jwt=test_jwt,
        )

        _, _, links, _ = create_citizen_nodes(reg)

        for link in links:
            assert link.hierarchy == 1.0, f"Link {link.id} should have hierarchy=1.0"

    def test_immutable_properties_have_high_permanence(self):
        """Immutable properties (name, registered_date, hash) should have high permanence."""
        test_jwt = make_test_jwt({"sub": "test"})
        reg = CitizenRegistration(
            name="Test",
            org_id="org_1",
            jwt=test_jwt,
        )

        citizen_node, property_nodes, links, _ = create_citizen_nodes(reg)

        # Find registered_date and hash links
        for link in links:
            if "registered" in link.id or "hash" in link.id:
                assert link.permanence == 1.0, f"{link.id} should be immutable"

    def test_mutable_properties_have_lower_permanence(self):
        """Mutable properties (status) should have lower permanence."""
        test_jwt = make_test_jwt({"sub": "test"})
        reg = CitizenRegistration(
            name="Test",
            org_id="org_1",
            jwt=test_jwt,
        )

        _, _, links, _ = create_citizen_nodes(reg)

        for link in links:
            if "status" in link.id:
                assert link.permanence < 1.0, "Status should be mutable"


class TestJWTDecoding:
    """Tests for JWT decoding functions."""

    def test_decode_valid_jwt(self):
        """Valid JWT should decode correctly."""
        payload = {"sub": "user123", "iss": "org_test"}
        jwt = make_test_jwt(payload)

        header, decoded_payload, sig = decode_jwt_parts(jwt)

        assert header is not None
        assert header["alg"] == "RS256"
        assert decoded_payload is not None
        assert decoded_payload["sub"] == "user123"
        assert decoded_payload["iss"] == "org_test"
        assert sig == "fake_signature"

    def test_decode_invalid_jwt_format(self):
        """Invalid JWT format should return None."""
        header, payload, sig = decode_jwt_parts("not.a.valid.jwt.with.too.many.parts")
        assert header is None
        assert payload is None

    def test_decode_jwt_missing_parts(self):
        """JWT with missing parts should return None."""
        header, payload, sig = decode_jwt_parts("only_one_part")
        assert header is None


class TestJWTClaimsVerification:
    """Tests for JWT claims verification."""

    def test_valid_claims(self):
        """Valid claims should pass."""
        payload = {
            "sub": "user",
            "iss": "org_test",
            "iat": time.time() - 60,  # Issued 1 minute ago
            "exp": time.time() + 3600,  # Expires in 1 hour
        }

        is_valid, error = verify_jwt_claims(payload, expected_issuer="org_test")
        assert is_valid
        assert error is None

    def test_expired_jwt(self):
        """Expired JWT should fail."""
        payload = {
            "sub": "user",
            "exp": time.time() - 3600,  # Expired 1 hour ago
        }

        is_valid, error = verify_jwt_claims(payload)
        assert not is_valid
        assert "expired" in error.lower()

    def test_not_yet_valid_jwt(self):
        """JWT with future iat should fail."""
        payload = {
            "sub": "user",
            "iat": time.time() + 3600,  # Issued in the future
        }

        is_valid, error = verify_jwt_claims(payload)
        assert not is_valid
        assert "not yet valid" in error.lower()

    def test_wrong_issuer(self):
        """JWT with wrong issuer should fail."""
        payload = {
            "sub": "user",
            "iss": "wrong_org",
        }

        is_valid, error = verify_jwt_claims(payload, expected_issuer="expected_org")
        assert not is_valid
        assert "issuer" in error.lower()


class TestJWTSignatureVerification:
    """Tests for JWT signature verification."""

    def test_verify_jwt_org_not_found(self):
        """Should fail if org not in registry."""
        jwt = make_test_jwt({"sub": "user", "iss": "org_test"})

        def lookup(org_id):
            return None  # Org not found

        result = verify_jwt_signature(jwt, "org_test", lookup)
        assert result.status == JWTVerificationStatus.ORG_NOT_FOUND
        assert not result.is_valid

    def test_verify_jwt_missing_public_key(self):
        """Should fail if org has no public key."""
        jwt = make_test_jwt({"sub": "user", "iss": "org_test"})

        def lookup(org_id):
            return ""  # Empty public key

        result = verify_jwt_signature(jwt, "org_test", lookup)
        assert result.status == JWTVerificationStatus.MISSING_PUBLIC_KEY

    def test_verify_jwt_valid_format(self):
        """Valid JWT format and claims should pass (signature checked by membrane)."""
        payload = {
            "sub": "user",
            "iss": "org_test",
            "iat": time.time() - 60,
            "exp": time.time() + 3600,
        }
        jwt = make_test_jwt(payload)

        def lookup(org_id):
            return "-----BEGIN PUBLIC KEY-----\nMIIBIjAN..."

        result = verify_jwt_signature(jwt, "org_test", lookup)
        assert result.status == JWTVerificationStatus.VALID
        assert result.is_valid
        assert result.claims["sub"] == "user"

    def test_verify_jwt_invalid_format(self):
        """Invalid JWT format should fail."""
        def lookup(org_id):
            return "public_key"

        result = verify_jwt_signature("not_a_jwt", "org_test", lookup)
        assert result.status == JWTVerificationStatus.INVALID_FORMAT

    def test_verify_jwt_expired(self):
        """Expired JWT should fail."""
        payload = {
            "sub": "user",
            "iss": "org_test",
            "exp": time.time() - 3600,  # Expired
        }
        jwt = make_test_jwt(payload)

        def lookup(org_id):
            return "public_key"

        result = verify_jwt_signature(jwt, "org_test", lookup)
        assert result.status == JWTVerificationStatus.EXPIRED


class TestRoutingVerification:
    """Tests for combined routing verification."""

    def test_verify_and_get_endpoint_success(self):
        """Valid sender should get destination endpoint."""
        def lookup(sender_id, dest_org_id):
            return ("correct_hash", "org_sender", "active", "wss://dest.com/ws")

        result = verify_and_get_endpoint(
            identity_hash="correct_hash",
            sender_id="citizen_123",
            dest_org_id="org_dest",
            graph_lookup=lookup,
        )

        assert result.is_valid
        assert result.can_route
        assert result.dest_endpoint == "wss://dest.com/ws"
        assert result.sender_org_id == "org_sender"

    def test_verify_and_get_endpoint_sender_not_found(self):
        """Unknown sender should fail."""
        def lookup(sender_id, dest_org_id):
            return None

        result = verify_and_get_endpoint(
            identity_hash="hash",
            sender_id="unknown_citizen",
            dest_org_id="org_dest",
            graph_lookup=lookup,
        )

        assert result.status == VerificationStatus.NOT_FOUND
        assert not result.is_valid
        assert not result.can_route

    def test_verify_and_get_endpoint_hash_mismatch(self):
        """Mismatched hash should fail."""
        def lookup(sender_id, dest_org_id):
            return ("stored_hash", "org_sender", "active", "wss://dest.com/ws")

        result = verify_and_get_endpoint(
            identity_hash="wrong_hash",
            sender_id="citizen_123",
            dest_org_id="org_dest",
            graph_lookup=lookup,
        )

        assert result.status == VerificationStatus.INVALID
        assert not result.is_valid

    def test_verify_and_get_endpoint_sender_suspended(self):
        """Suspended sender should fail."""
        def lookup(sender_id, dest_org_id):
            return ("correct_hash", "org_sender", "suspended", "wss://dest.com/ws")

        result = verify_and_get_endpoint(
            identity_hash="correct_hash",
            sender_id="citizen_123",
            dest_org_id="org_dest",
            graph_lookup=lookup,
        )

        assert result.status == VerificationStatus.SUSPENDED
        assert not result.is_valid

    def test_verify_and_get_endpoint_no_dest_endpoint(self):
        """Missing destination endpoint should be flagged."""
        def lookup(sender_id, dest_org_id):
            return ("correct_hash", "org_sender", "active", None)

        result = verify_and_get_endpoint(
            identity_hash="correct_hash",
            sender_id="citizen_123",
            dest_org_id="org_dest",
            graph_lookup=lookup,
        )

        # Sender is valid, but can't route
        assert result.is_valid
        assert not result.can_route
        assert "no endpoint" in result.error.lower()
