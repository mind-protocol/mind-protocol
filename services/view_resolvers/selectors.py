"""
L2 View Resolvers - Cypher Selectors (Phase A: Select)

Minimal Cypher queries to grab KO neighborhoods for each view type.
All rooted in U4_* universal types for portability across repos/languages.

Author: Mel "Bridgekeeper"
Date: 2025-11-04
"""

# Architecture View - Services, layers, dependencies
ARCHITECTURE = """
MATCH (s:U4_Knowledge_Object {kind:'Service'})-[:U4_IMPLEMENTS]->(ca:U4_Code_Artifact)
WHERE ca.path STARTS WITH $scope_path
OPTIONAL MATCH (s)-[:DEPENDS_ON]->(t:U4_Knowledge_Object {kind:'Service'})
OPTIONAL MATCH (s)-[:IN_LAYER]->(ly:Layer)
RETURN s, collect(DISTINCT t) AS deps, ly
"""

# API Reference View - Endpoints/RPCs + schemas
API_REFERENCE = """
MATCH (ep:U4_Knowledge_Object)-[:U4_IMPLEMENTS]->(ca:U4_Code_Artifact)
WHERE (ep.kind = 'Endpoint' OR ep.kind = 'RPC') AND ca.path STARTS WITH $scope_path
OPTIONAL MATCH (ep)-[:U4_DOCUMENTS]->(sch:U4_Knowledge_Object {kind:'Schema'})
RETURN ep, ca, collect(DISTINCT sch) AS schemas
"""

# Coverage View - Node counts by type + test coverage
COVERAGE = """
MATCH (n) WHERE n.scope_ref = $scope_org
WITH labels(n) AS labs, n
WITH labs[0] AS type, count(n) AS count
OPTIONAL MATCH (t:Test)-[:COVERS]->(c:U4_Code_Artifact) WHERE c.scope_ref = $scope_org
WITH type, count, count(t) AS tests
RETURN type, count, tests
"""

# Index View - Browseable KO catalog
INDEX = """
MATCH (k:U4_Knowledge_Object)
WHERE k.scope_ref = $scope_org AND k.path STARTS WITH $scope_path
RETURN k.name AS name, k.kind AS kind, k.path AS path
ORDER BY name
"""

# Registry mapping view_type → selector
SELECTORS = {
    "architecture": ARCHITECTURE,
    "api-reference": API_REFERENCE,
    "coverage": COVERAGE,
    "index": INDEX
}


def get_selector(view_type: str) -> str:
    """Get Cypher selector for view type"""
    if view_type not in SELECTORS:
        raise ValueError(f"Unknown view_type: {view_type}. Available: {list(SELECTORS.keys())}")
    return SELECTORS[view_type]
