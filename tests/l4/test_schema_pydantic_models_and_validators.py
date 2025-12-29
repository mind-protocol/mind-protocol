"""
Tests for L4 schema module.

DOCS: docs/l4/schema/HEALTH_Schema.md
"""

import pytest
from pydantic import ValidationError

from l4.schema import (
    NodeType,
    MomentStatus,
    NodeBase,
    MomentBase,
    ActorNode,
    NarrativeNode,
    SpaceNode,
    ThingNode,
    LinkBase,
    ValidationResult,
    validate_node,
    validate_link,
    validate_graph,
    check_invariants,
    SCHEMA_VERSION,
    PROTOCOL_VERSION,
    VersionCompatibility,
    check_version_compatibility,
)


class TestNodeTypes:
    """Test node type enum and values."""

    def test_node_type_values(self):
        """All 5 canonical types exist."""
        assert NodeType.ACTOR.value == "actor"
        assert NodeType.MOMENT.value == "moment"
        assert NodeType.NARRATIVE.value == "narrative"
        assert NodeType.SPACE.value == "space"
        assert NodeType.THING.value == "thing"
        assert len(NodeType) == 5

    def test_moment_status_values(self):
        """Moment status enum values."""
        assert MomentStatus.POSSIBLE.value == "possible"
        assert MomentStatus.ACTIVE.value == "active"
        assert MomentStatus.COMPLETED.value == "completed"


class TestNodeBase:
    """Test NodeBase model."""

    def test_create_valid_node(self):
        """Create a valid node with required fields."""
        node = NodeBase(
            id="test-1",
            name="Test Node",
            node_type=NodeType.ACTOR,
            synthesis="A test node",
        )
        assert node.id == "test-1"
        assert node.name == "Test Node"
        assert node.node_type == NodeType.ACTOR
        assert node.weight == 1.0  # default
        assert node.energy == 0.0  # default

    def test_weight_must_be_non_negative(self):
        """Weight must be >= 0."""
        with pytest.raises(ValidationError) as exc_info:
            NodeBase(
                id="test",
                name="Test",
                node_type=NodeType.ACTOR,
                synthesis="Test",
                weight=-1.0,
            )
        assert "weight" in str(exc_info.value)

    def test_energy_must_be_non_negative(self):
        """Energy must be >= 0."""
        with pytest.raises(ValidationError) as exc_info:
            NodeBase(
                id="test",
                name="Test",
                node_type=NodeType.ACTOR,
                synthesis="Test",
                energy=-0.5,
            )
        assert "energy" in str(exc_info.value)

    def test_embedding_must_be_1536_dims(self):
        """Embedding must have exactly 1536 dimensions."""
        with pytest.raises(ValidationError) as exc_info:
            NodeBase(
                id="test",
                name="Test",
                node_type=NodeType.ACTOR,
                synthesis="Test",
                embedding=[0.1] * 100,  # Wrong size
            )
        assert "1536" in str(exc_info.value)

    def test_no_custom_fields(self):
        """Extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            NodeBase(
                id="test",
                name="Test",
                node_type=NodeType.ACTOR,
                synthesis="Test",
                custom_field="not allowed",
            )
        assert "extra" in str(exc_info.value).lower()

    def test_subtype_is_optional(self):
        """Subtype (type field) is optional."""
        node = NodeBase(
            id="test",
            name="Test",
            node_type=NodeType.ACTOR,
            synthesis="Test",
            type="citizen",
        )
        assert node.type == "citizen"


class TestMomentBase:
    """Test MomentBase model."""

    def test_moment_has_status(self):
        """Moments have status field."""
        moment = MomentBase(
            id="moment-1",
            name="Test Moment",
            synthesis="A test moment",
        )
        assert moment.status == MomentStatus.POSSIBLE
        assert moment.node_type == NodeType.MOMENT

    def test_moment_duration_computed(self):
        """Duration is computed from timestamps."""
        moment = MomentBase(
            id="moment-1",
            name="Test",
            synthesis="Test",
            started_at_s=1000,
            completed_at_s=1500,
        )
        assert moment.duration_s == 500

    def test_moment_duration_none_if_incomplete(self):
        """Duration is None if not completed."""
        moment = MomentBase(
            id="moment-1",
            name="Test",
            synthesis="Test",
            started_at_s=1000,
        )
        assert moment.duration_s is None


class TestSpecificNodeTypes:
    """Test specific node type models."""

    def test_actor_node(self):
        """ActorNode has correct node_type."""
        actor = ActorNode(
            id="actor-1",
            name="Test Actor",
            synthesis="An actor",
        )
        assert actor.node_type == NodeType.ACTOR

    def test_narrative_node(self):
        """NarrativeNode has correct node_type."""
        narrative = NarrativeNode(
            id="narr-1",
            name="Test Narrative",
            synthesis="A narrative",
        )
        assert narrative.node_type == NodeType.NARRATIVE

    def test_space_node(self):
        """SpaceNode has correct node_type."""
        space = SpaceNode(
            id="space-1",
            name="Test Space",
            synthesis="A space",
        )
        assert space.node_type == NodeType.SPACE

    def test_thing_node(self):
        """ThingNode has correct node_type and uri field."""
        thing = ThingNode(
            id="thing-1",
            name="Test Thing",
            synthesis="A thing",
            uri="https://example.com",
        )
        assert thing.node_type == NodeType.THING
        assert thing.uri == "https://example.com"


class TestLinkBase:
    """Test LinkBase model."""

    def test_create_valid_link(self):
        """Create a valid link with required fields."""
        link = LinkBase(
            id="link-1",
            node_a="node-1",
            node_b="node-2",
        )
        assert link.id == "link-1"
        assert link.polarity == (0.5, 0.5)
        assert link.hierarchy == 0.0
        assert link.permanence == 0.5

    def test_polarity_must_be_in_range(self):
        """Polarity values must be in [0, 1]."""
        with pytest.raises(ValidationError) as exc_info:
            LinkBase(
                id="link-1",
                node_a="a",
                node_b="b",
                polarity=(1.5, 0.5),  # Out of range
            )
        assert "polarity" in str(exc_info.value).lower()

    def test_hierarchy_must_be_in_range(self):
        """Hierarchy must be in [-1, 1]."""
        with pytest.raises(ValidationError) as exc_info:
            LinkBase(
                id="link-1",
                node_a="a",
                node_b="b",
                hierarchy=2.0,  # Out of range
            )
        assert "hierarchy" in str(exc_info.value).lower()

    def test_permanence_must_be_in_range(self):
        """Permanence must be in [0, 1]."""
        with pytest.raises(ValidationError) as exc_info:
            LinkBase(
                id="link-1",
                node_a="a",
                node_b="b",
                permanence=-0.5,  # Out of range
            )
        assert "permanence" in str(exc_info.value).lower()

    def test_emotions_in_range(self):
        """Emotion axes must be in [-1, 1]."""
        with pytest.raises(ValidationError) as exc_info:
            LinkBase(
                id="link-1",
                node_a="a",
                node_b="b",
                joy_sadness=2.0,  # Out of range
            )
        assert "joy_sadness" in str(exc_info.value).lower()

    def test_forward_coloration_weight(self):
        """Forward coloration weight computed correctly."""
        link = LinkBase(
            id="link-1",
            node_a="a",
            node_b="b",
            permanence=0.3,
        )
        assert link.forward_coloration_weight == 0.7

    def test_emotions_property(self):
        """Emotions property returns all axes."""
        link = LinkBase(
            id="link-1",
            node_a="a",
            node_b="b",
            joy_sadness=0.5,
            trust_disgust=-0.3,
        )
        emotions = link.emotions
        assert emotions["joy_sadness"] == 0.5
        assert emotions["trust_disgust"] == -0.3


class TestValidation:
    """Test validation functions."""

    def test_validate_valid_node(self):
        """Valid node passes validation."""
        result = validate_node({
            "id": "test",
            "name": "Test",
            "node_type": "actor",
            "synthesis": "Test",
        })
        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_invalid_node(self):
        """Invalid node fails validation."""
        result = validate_node({
            "id": "test",
            "name": "Test",
            "node_type": "invalid_type",
            "synthesis": "Test",
        })
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_valid_link(self):
        """Valid link passes validation."""
        result = validate_link({
            "id": "link-1",
            "node_a": "a",
            "node_b": "b",
        })
        assert result.is_valid

    def test_validate_invalid_link(self):
        """Invalid link fails validation."""
        result = validate_link({
            "id": "link-1",
            "node_a": "a",
            "node_b": "b",
            "hierarchy": 5.0,  # Out of range
        })
        assert not result.is_valid

    def test_validate_graph_reference_integrity(self):
        """Graph validation checks reference integrity."""
        nodes = [
            {"id": "a", "name": "A", "node_type": "actor", "synthesis": "A"},
            {"id": "b", "name": "B", "node_type": "actor", "synthesis": "B"},
        ]
        links = [
            {"id": "link-1", "node_a": "a", "node_b": "c"},  # 'c' doesn't exist
        ]
        results = validate_graph(nodes, links)
        # Last result is the link validation
        link_result = results[-1]
        assert not link_result.is_valid
        assert "node_b" in str(link_result.errors)


class TestVersions:
    """Test version tracking."""

    def test_schema_version_format(self):
        """Schema version is valid semver."""
        parts = SCHEMA_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_version_compatibility_exact(self):
        """Same version is exact match."""
        result = check_version_compatibility("1.8.1", "1.8.1")
        assert result == VersionCompatibility.EXACT_MATCH

    def test_version_compatibility_minor_diff(self):
        """Minor version difference is compatible."""
        result = check_version_compatibility("1.8.1", "1.9.0")
        assert result == VersionCompatibility.MINOR_DIFF

    def test_version_compatibility_major_diff(self):
        """Major version difference is incompatible."""
        result = check_version_compatibility("1.8.1", "2.0.0")
        assert result == VersionCompatibility.MAJOR_DIFF


class TestInvariants:
    """Test invariant checking."""

    def test_check_negative_weight(self):
        """Negative weight is caught."""
        nodes = [{"id": "a", "weight": -1.0}]
        violations = check_invariants(nodes, [])
        assert any("weight < 0" in v for v in violations)

    def test_check_negative_energy(self):
        """Negative energy is caught."""
        nodes = [{"id": "a", "energy": -0.5}]
        violations = check_invariants(nodes, [])
        assert any("energy < 0" in v for v in violations)

    def test_check_hierarchy_out_of_range(self):
        """Hierarchy out of range is caught."""
        links = [{"id": "l", "hierarchy": 2.0}]
        violations = check_invariants([], links)
        assert any("hierarchy out of range" in v for v in violations)
