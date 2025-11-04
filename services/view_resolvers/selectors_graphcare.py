"""
L2 View Resolvers - GraphCare Custom Selectors (ko_type Workaround)

Custom Cypher queries for GraphCare graphs that use ko_type instead of kind.
Adapts to Quinn's corpus analysis output structure:
  - U4_Knowledge_Object with ko_type (spec, adr, guide, runbook, reference)
  - U4_Code_Artifact with language property
  - Relationships: U4_DOCUMENTS, U4_IMPLEMENTS, U4_DEPENDS_ON, etc.

Author: Kai "Chief Engineer"
Date: 2025-11-04
Context: Workaround while Nora adds kind property to production graphs
"""

# Architecture View - Code structure + docs
# Since GraphCare graphs don't have explicit Service nodes,
# we show code artifacts grouped by module/path with their documentation
ARCHITECTURE_GRAPHCARE = """
MATCH (ca:U4_Code_Artifact)
WHERE ca.scope_ref = $scope_org
OPTIONAL MATCH (ko:U4_Knowledge_Object)-[:U4_DOCUMENTS]->(ca)
WHERE ko.ko_type IN ['spec', 'adr']
OPTIONAL MATCH (ca)-[:U4_DEPENDS_ON]->(dep:U4_Code_Artifact)
WITH ca, collect(DISTINCT ko) AS docs, collect(DISTINCT dep) AS dependencies
RETURN ca.path AS path,
       ca.name AS name,
       ca.language AS language,
       ca.artifact_type AS type,
       docs,
       dependencies
ORDER BY ca.path
LIMIT 50
"""

# API Reference View - Code artifacts that look like endpoints/handlers
# Heuristic: functions/classes with names containing api, endpoint, handler, route
API_REFERENCE_GRAPHCARE = """
MATCH (ca:U4_Code_Artifact)
WHERE ca.scope_ref = $scope_org
  AND (ca.name =~ '.*[Aa]pi.*'
    OR ca.name =~ '.*[Ee]ndpoint.*'
    OR ca.name =~ '.*[Hh]andler.*'
    OR ca.name =~ '.*[Rr]oute.*'
    OR ca.path =~ '.*/api/.*'
    OR ca.path =~ '.*/routes/.*'
    OR ca.path =~ '.*/endpoints/.*')
OPTIONAL MATCH (ko:U4_Knowledge_Object)-[:U4_DOCUMENTS]->(ca)
WHERE ko.ko_type = 'reference'
OPTIONAL MATCH (schema:U4_Knowledge_Object)-[:U4_DOCUMENTS]->(ca)
WHERE schema.ko_type = 'spec' AND schema.name =~ '.*[Ss]chema.*'
RETURN ca.name AS name,
       ca.path AS path,
       ca.description AS description,
       ca.language AS language,
       collect(DISTINCT ko) AS documentation,
       collect(DISTINCT schema) AS schemas
ORDER BY ca.path
LIMIT 30
"""

# Coverage View - Node counts by type + language distribution
COVERAGE_GRAPHCARE = """
MATCH (n)
WHERE n.scope_ref = $scope_org
WITH labels(n) AS labs, n
WITH labs[0] AS node_type, n
WITH node_type,
     count(n) AS count,
     collect(DISTINCT n.language) AS languages,
     collect(DISTINCT n.ko_type) AS ko_types
OPTIONAL MATCH (t)-[:U4_TESTS]->(c)
WHERE c.scope_ref = $scope_org
WITH node_type, count, languages, ko_types, count(t) AS test_count
RETURN node_type,
       count,
       languages,
       ko_types,
       test_count
ORDER BY count DESC
"""

# Index View - All knowledge objects + code artifacts (browseable catalog)
INDEX_GRAPHCARE = """
MATCH (n)
WHERE n.scope_ref = $scope_org
  AND (n:U4_Knowledge_Object OR n:U4_Code_Artifact)
WITH n, labels(n) AS labs
RETURN n.name AS name,
       CASE
         WHEN n:U4_Knowledge_Object THEN n.ko_type
         WHEN n:U4_Code_Artifact THEN n.language
         ELSE 'unknown'
       END AS type_or_language,
       n.path AS path,
       labs[0] AS node_label,
       n.description AS description
ORDER BY node_label, name
LIMIT 100
"""

# Code Dependencies View - Show import/dependency graph
CODE_DEPENDENCIES_GRAPHCARE = """
MATCH (ca:U4_Code_Artifact)-[r:U4_DEPENDS_ON]->(dep:U4_Code_Artifact)
WHERE ca.scope_ref = $scope_org
RETURN ca.name AS source,
       ca.path AS source_path,
       dep.name AS target,
       dep.path AS target_path,
       type(r) AS relationship
ORDER BY ca.path
LIMIT 50
"""

# Documentation Coverage View - Which code has docs, which doesn't
DOC_COVERAGE_GRAPHCARE = """
MATCH (ca:U4_Code_Artifact)
WHERE ca.scope_ref = $scope_org
OPTIONAL MATCH (ko:U4_Knowledge_Object)-[:U4_DOCUMENTS]->(ca)
WITH ca, count(ko) AS doc_count
RETURN ca.path AS path,
       ca.name AS name,
       ca.language AS language,
       CASE WHEN doc_count > 0 THEN 'documented' ELSE 'undocumented' END AS status,
       doc_count
ORDER BY doc_count ASC, ca.path
LIMIT 50
"""

# Registry mapping view_type → selector (GraphCare version)
SELECTORS_GRAPHCARE = {
    "architecture": ARCHITECTURE_GRAPHCARE,
    "api-reference": API_REFERENCE_GRAPHCARE,
    "coverage": COVERAGE_GRAPHCARE,
    "index": INDEX_GRAPHCARE,
    "code-dependencies": CODE_DEPENDENCIES_GRAPHCARE,
    "doc-coverage": DOC_COVERAGE_GRAPHCARE
}


def get_selector_graphcare(view_type: str) -> str:
    """
    Get Cypher selector for GraphCare graphs (ko_type based).

    Use this for graphs created by GraphCare corpus analysis
    that use ko_type instead of kind property.

    Args:
        view_type: One of: architecture, api-reference, coverage,
                   index, code-dependencies, doc-coverage

    Returns:
        Cypher query string with $scope_org parameter

    Raises:
        ValueError: If view_type not recognized
    """
    if view_type not in SELECTORS_GRAPHCARE:
        raise ValueError(
            f"Unknown view_type: {view_type}. "
            f"Available: {list(SELECTORS_GRAPHCARE.keys())}"
        )
    return SELECTORS_GRAPHCARE[view_type]


def is_graphcare_graph(graph_name: str) -> bool:
    """
    Heuristic to detect if graph is from GraphCare (uses ko_type).

    In future, could query graph for sample node and check properties.
    For now, simple naming heuristic.

    Args:
        graph_name: Name of graph (e.g., "scopelock")

    Returns:
        True if likely a GraphCare graph
    """
    # For now, assume any non-mindprotocol graph is GraphCare
    # More robust: query graph for U4_Knowledge_Object and check for ko_type
    return graph_name not in ['mindprotocol', 'mind_protocol', 'core']
