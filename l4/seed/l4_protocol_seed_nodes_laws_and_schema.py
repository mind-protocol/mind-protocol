"""
L4 Protocol seed data — the laws and definitions as nodes.

DOCS: docs/l4/laws/PATTERNS_Laws.md

This is the source of truth. These nodes are loaded into the L4 graph
and can be queried by any participant to understand the protocol.
"""

from l4.schema import SpaceNode, NarrativeNode, NodeType

# =============================================================================
# PROTOCOL SPACE
# =============================================================================

L4_PROTOCOL = SpaceNode(
    id="l4_protocol",
    name="Mind Protocol",
    type="protocol",
    synthesis="Mind Protocol v1.0.0 — L4 law layer defining ecosystem obligations",
    content="""
Mind Protocol is infrastructure for AI agent communication.

This space contains:
- The 8 laws (ecosystem obligations)
- Schema definitions
- Version tracking

All participants must follow these laws to participate in the ecosystem.
""",
)

# =============================================================================
# VERSIONS
# =============================================================================

SCHEMA_VERSION_NODE = NarrativeNode(
    id="l4_schema_version",
    name="Schema Version",
    type="version",
    synthesis="Mind Protocol Schema v1.8.1",
    content="1.8.1",
)

PROTOCOL_VERSION_NODE = NarrativeNode(
    id="l4_protocol_version",
    name="Protocol Version",
    type="version",
    synthesis="Mind Protocol v1.0.0",
    content="1.0.0",
)

# =============================================================================
# THE 8 LAWS
# =============================================================================

LAW_L1 = NarrativeNode(
    id="l4_law_l1",
    name="L1: Respect Schema",
    type="law",
    synthesis="L1 — All graphs must use the canonical schema: 5 node types, single link type",
    content="""
LAW L1: RESPECT SCHEMA

All graphs in the Mind Protocol ecosystem must use the canonical schema:
- 5 node types: actor, moment, narrative, space, thing
- 1 link type: link (all semantics in properties)
- No custom node types allowed
- No custom link types allowed

Subtypes are allowed via the `type` field on nodes.

This enables interoperability — any graph can understand any other graph's structure.

ENFORCEMENT: Schema validation on all operations.
VIOLATION: Rejected at graph level.
""",
)

LAW_L2 = NarrativeNode(
    id="l4_law_l2",
    name="L2: Register to Exist",
    type="law",
    synthesis="L2 — Must register in L4 registry to participate in ecosystem",
    content="""
LAW L2: REGISTER TO EXIST

To participate in cross-org communication, you must be registered in L4:
- Citizens must be registered under an Org
- Orgs must have a registered endpoint
- Registration = existence in the protocol

Unregistered entities cannot send or receive cross-org stimuli.

ENFORCEMENT: Registry lookup before routing.
VIOLATION: Stimulus rejected with "Unknown sender" or "Unknown target".
""",
)

LAW_L3 = NarrativeNode(
    id="l4_law_l3",
    name="L3: No Direct DB Access",
    type="law",
    synthesis="L3 — Cannot query or modify another graph directly; stimulus only",
    content="""
LAW L3: NO DIRECT DB ACCESS

You never touch another graph's database:
- No cross-org Cypher queries
- No direct database connections
- All communication via stimulus through membrane

Your graph is sovereign. So is everyone else's.

ENFORCEMENT: Network architecture — no route exists.
VIOLATION: Connection refused.
""",
)

LAW_L4 = NarrativeNode(
    id="l4_law_l4",
    name="L4: Cross-org via Membrane",
    type="law",
    synthesis="L4 — All cross-org communication routes through membrane",
    content="""
LAW L4: CROSS-ORG VIA MEMBRANE

All cross-org communication routes through the membrane network:
- No direct org-to-org connections
- Membrane handles routing, validation, fees
- Same-org communication can be direct

Your code should only know about membrane, never about other orgs directly.

ENFORCEMENT: Network topology.
VIOLATION: No route exists for direct connections.
""",
)

LAW_L5 = NarrativeNode(
    id="l4_law_l5",
    name="L5: Hash-based Identity",
    type="law",
    synthesis="L5 — Prove identity via hash = SHA256(JWT × node_id), never send token",
    content="""
LAW L5: HASH-BASED IDENTITY

Identity is proven via hash, never by sending the token:
- Compute: hash = SHA256(JWT × node_id)
- Send: hash in stimulus
- Verify: receiver checks against registry

Never send your JWT. Store it securely. Only expose the hash.

ENFORCEMENT: Hash verification at membrane.
VIOLATION: Rejected with "Invalid identity" or "Token exposure forbidden".
""",
)

LAW_L6 = NarrativeNode(
    id="l4_law_l6",
    name="L6: Receiver Validates",
    type="law",
    synthesis="L6 — Cross-org stimulus requires explicit receiver acceptance",
    content="""
LAW L6: RECEIVER VALIDATES

Cross-org stimulus requires explicit acceptance by receiver:
- Receiver decides whether to process
- Trust mode determines response filtering (public/sanitized/trust)
- Default should be reject unless explicitly accepted

Consent is fundamental. No one can force you to accept their stimulus.

ENFORCEMENT: Receiver-side logic.
VIOLATION: Stimulus dropped or rejected.
""",
)

LAW_L7 = NarrativeNode(
    id="l4_law_l7",
    name="L7: Membrane Fees",
    type="law",
    synthesis="L7 — Cross-org transactions pay 1-5% fee to protocol",
    content="""
LAW L7: MEMBRANE FEES

Cross-org transactions pay a fee to the protocol:
- Fee range: 1-5% of transaction value
- Same-org transactions: free
- Fee supports protocol infrastructure

If different org ID, pay the fee. Same company, different orgs = fee applies.

ENFORCEMENT: Fee deduction before routing.
VIOLATION: Rejected with "Insufficient funds".
""",
)

LAW_L8 = NarrativeNode(
    id="l4_law_l8",
    name="L8: WebSocket Only",
    type="law",
    synthesis="L8 — Communication via WebSocket push, no REST or polling",
    content="""
LAW L8: WEBSOCKET ONLY

Protocol communication is WebSocket-based:
- No REST endpoints for protocol operations
- No polling — push only
- Client initiates connection, L4 pushes events

The system is alive. Things happen, you get notified. Don't ask "anything new?" repeatedly.

ENFORCEMENT: API design — no REST routes exist.
VIOLATION: 404 / no route.
""",
)

# =============================================================================
# SCHEMA DEFINITIONS
# =============================================================================

SCHEMA_NODE_TYPES = NarrativeNode(
    id="l4_schema_node_types",
    name="Schema: Node Types",
    type="schema_definition",
    synthesis="The 5 canonical node types: actor, moment, narrative, space, thing",
    content="""
NODE TYPES (enum, fixed)

1. ACTOR — Entities that act
   - Role: Pump (injects energy)
   - Examples: citizens, agents, verifiers
   - Subtypes: player, npc, system

2. MOMENT — Events in time
   - Role: Router + Branch Point
   - Only type where branching occurs
   - Subtypes: event, decision, action

3. NARRATIVE — Concepts and beliefs
   - Role: Attractor
   - Created by crystallization
   - Subtypes: issue, objective, task, belief, pattern, documentation

4. SPACE — Containers
   - Role: Context container
   - Bidirectional flow
   - Subtypes: area, module, directory, org

5. THING — Actual artifacts
   - Role: Fast passthrough
   - Tends toward weight=0
   - Subtypes: file, uri, artifact, wallet, endpoint
""",
)

SCHEMA_LINK_PROPERTIES = NarrativeNode(
    id="l4_schema_link_properties",
    name="Schema: Link Properties",
    type="schema_definition",
    synthesis="Link semantic axes: polarity, hierarchy, permanence",
    content="""
LINK PROPERTIES (single link type, semantics in properties)

SEMANTIC AXES:
- polarity: [a→b, b→a] flow strength, each in [0, 1]
- hierarchy: -1 = contains, +1 = elaborates
- permanence: 0 = speculative, 1 = definitive

PHYSICS:
- weight: importance [0, ∞)
- energy: current activation [0, ∞)

DERIVED:
- forward_coloration_weight = 1 - permanence
""",
)

# =============================================================================
# ALL PROTOCOL NODES
# =============================================================================

PROTOCOL_NODES = [
    L4_PROTOCOL,
    SCHEMA_VERSION_NODE,
    PROTOCOL_VERSION_NODE,
    LAW_L1,
    LAW_L2,
    LAW_L3,
    LAW_L4,
    LAW_L5,
    LAW_L6,
    LAW_L7,
    LAW_L8,
    SCHEMA_NODE_TYPES,
    SCHEMA_LINK_PROPERTIES,
]

# Links from protocol space to all contents
PROTOCOL_LINKS = [
    {"node_a": "l4_protocol", "node_b": "l4_schema_version", "hierarchy": -1, "permanence": 1.0},
    {"node_a": "l4_protocol", "node_b": "l4_protocol_version", "hierarchy": -1, "permanence": 1.0},
    {"node_a": "l4_protocol", "node_b": "l4_law_l1", "hierarchy": -1, "permanence": 1.0},
    {"node_a": "l4_protocol", "node_b": "l4_law_l2", "hierarchy": -1, "permanence": 1.0},
    {"node_a": "l4_protocol", "node_b": "l4_law_l3", "hierarchy": -1, "permanence": 1.0},
    {"node_a": "l4_protocol", "node_b": "l4_law_l4", "hierarchy": -1, "permanence": 1.0},
    {"node_a": "l4_protocol", "node_b": "l4_law_l5", "hierarchy": -1, "permanence": 1.0},
    {"node_a": "l4_protocol", "node_b": "l4_law_l6", "hierarchy": -1, "permanence": 1.0},
    {"node_a": "l4_protocol", "node_b": "l4_law_l7", "hierarchy": -1, "permanence": 1.0},
    {"node_a": "l4_protocol", "node_b": "l4_law_l8", "hierarchy": -1, "permanence": 1.0},
    {"node_a": "l4_protocol", "node_b": "l4_schema_node_types", "hierarchy": -1, "permanence": 1.0},
    {"node_a": "l4_protocol", "node_b": "l4_schema_link_properties", "hierarchy": -1, "permanence": 1.0},
]


def get_protocol_seed_data():
    """Get all protocol nodes and links for seeding L4 graph."""
    return {
        "nodes": [node.model_dump() for node in PROTOCOL_NODES],
        "links": PROTOCOL_LINKS,
    }
