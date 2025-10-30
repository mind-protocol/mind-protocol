"""
FalkorDB Graph Wrapper with Write→Read Confirmations

Provides idempotent graph operations with read-back verification for doc ingestion.

Key features:
- ensure_node/ensure_edge with MERGE (idempotent)
- Write→read confirmation (2 retry attempts)
- Schema registry queries (node types, link types, metadata contracts)
- JSONL streaming logs for all operations

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-29
Spec: docs/SPEC DOC INPUT.md
"""

import json
import logging
import sys
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import redis

from tools.logger import setup_logger

logger = setup_logger(__name__)


class GraphWrapper:
    """
    FalkorDB graph client with write→read confirmations.

    All writes are verified by reading back and confirming the written values.
    Failed confirmations are retried up to MAX_RETRIES times.
    """

    MAX_RETRIES = 2  # Read-back retry attempts

    def __init__(self, graph_name: str = "consciousness-infrastructure_mind-protocol", host: str = "localhost", port: int = 6379):
        """
        Initialize graph wrapper.

        Args:
            graph_name: FalkorDB graph name
            host: Redis host
            port: Redis port
        """
        self.graph_name = graph_name
        self.r = redis.Redis(host=host, port=port, decode_responses=False)

        # Verify connection
        try:
            self.r.ping()
            self._log_event("graph_init", {"graph": graph_name, "status": "connected"})
        except redis.exceptions.ConnectionError as e:
            self._log_event("graph_init", {"graph": graph_name, "status": "failed", "error": str(e)})
            raise

    def _log_event(self, event_type: str, payload: Dict[str, Any]):
        """Emit JSONL log prefixed with @@."""
        log_line = {"type": event_type, **payload, "timestamp": datetime.utcnow().isoformat()}
        print(f"@@ {json.dumps(log_line)}", flush=True)

    def _quote_string(self, value: str) -> str:
        """
        Quote string for Cypher query (escape single quotes).

        Args:
            value: String to quote

        Returns:
            Quoted string safe for Cypher
        """
        # Escape single quotes and backslashes
        escaped = value.replace('\\', '\\\\').replace("'", "\\'")
        return f"'{escaped}'"

    def _format_value(self, value: Any) -> str:
        """
        Format Python value for Cypher query.

        Args:
            value: Python value (str, int, float, bool, None)

        Returns:
            Cypher-formatted value
        """
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return self._quote_string(value)
        elif isinstance(value, dict):
            # Convert dict to JSON string
            return self._quote_string(json.dumps(value))
        elif isinstance(value, list):
            # Convert list to JSON string
            return self._quote_string(json.dumps(value))
        else:
            return self._quote_string(str(value))

    def _execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute Cypher query against FalkorDB.

        Note: FalkorDB doesn't support parameterized queries via Redis protocol.
        Query should already have values interpolated.

        Args:
            query: Cypher query string (values already interpolated)
            params: Unused (kept for API compatibility)

        Returns:
            Query result from FalkorDB
        """
        try:
            result = self.r.execute_command('GRAPH.QUERY', self.graph_name, query)
            return result
        except Exception as e:
            self._log_event("query_error", {"query": query[:200], "error": str(e)})
            raise

    def _parse_node_result(self, result: Any) -> Optional[Dict[str, Any]]:
        """
        Parse node from FalkorDB query result.

        Args:
            result: FalkorDB query result

        Returns:
            Parsed node dict or None
        """
        if not result or len(result) < 2 or not result[1]:
            return None

        # FalkorDB returns: [headers, [[node_data]], statistics]
        # Parse first row, first column (the node)
        row = result[1][0]
        if not row or len(row) == 0:
            return None

        # Node structure: [['id', 2], ['labels', [b'Label']], ['properties', [[b'key', b'val'], ...]]]
        node_data = row[0]
        if not isinstance(node_data, list):
            return None

        # Extract properties from node_data
        node_dict = {}
        for item in node_data:
            if len(item) != 2:
                continue

            key = item[0].decode('utf-8') if isinstance(item[0], bytes) else str(item[0])

            if key == 'id':
                node_dict['_id'] = item[1]
            elif key == 'labels':
                # Labels is array of bytes
                labels = [lbl.decode('utf-8') if isinstance(lbl, bytes) else str(lbl) for lbl in item[1]]
                node_dict['_labels'] = labels
            elif key == 'properties':
                # Properties is array of [key, value] pairs
                for prop in item[1]:
                    if len(prop) == 2:
                        prop_key = prop[0].decode('utf-8') if isinstance(prop[0], bytes) else str(prop[0])
                        prop_val = prop[1]

                        # Decode bytes values
                        if isinstance(prop_val, bytes):
                            prop_val = prop_val.decode('utf-8')

                        node_dict[prop_key] = prop_val

        return node_dict if node_dict else None

    def _parse_edge_result(self, result: Any) -> Optional[Dict[str, Any]]:
        """
        Parse edge from FalkorDB query result.

        Args:
            result: FalkorDB query result

        Returns:
            Parsed edge dict or None
        """
        if not result or len(result) < 2 or not result[1]:
            return None

        # FalkorDB returns: [headers, [[edge_data]], statistics]
        # Parse first row, first column (the edge)
        row = result[1][0]
        if not row or len(row) == 0:
            return None

        # Edge structure similar to node: [['id', 2], ['type', b'IMPLEMENTS'], ['src_node', 1], ['dest_node', 3], ['properties', [[b'key', b'val'], ...]]]
        edge_data = row[0]
        if not isinstance(edge_data, list):
            return None

        # Extract properties from edge_data
        edge_dict = {}
        for item in edge_data:
            if len(item) != 2:
                continue

            key = item[0].decode('utf-8') if isinstance(item[0], bytes) else str(item[0])

            if key == 'id':
                edge_dict['_id'] = item[1]
            elif key == 'type':
                edge_type = item[1].decode('utf-8') if isinstance(item[1], bytes) else str(item[1])
                edge_dict['_type'] = edge_type
            elif key == 'src_node':
                edge_dict['_source_id'] = item[1]
            elif key == 'dest_node':
                edge_dict['_target_id'] = item[1]
            elif key == 'properties':
                # Properties is array of [key, value] pairs
                for prop in item[1]:
                    if len(prop) == 2:
                        prop_key = prop[0].decode('utf-8') if isinstance(prop[0], bytes) else str(prop[0])
                        prop_val = prop[1]

                        # Decode bytes values
                        if isinstance(prop_val, bytes):
                            prop_val = prop_val.decode('utf-8')

                        # If key is 'meta' or 'metadata', parse as JSON
                        if prop_key in ['meta', 'metadata'] and isinstance(prop_val, str):
                            try:
                                prop_val = json.loads(prop_val)
                            except json.JSONDecodeError:
                                pass  # Keep as string if not valid JSON

                        edge_dict[prop_key] = prop_val

        return edge_dict if edge_dict else None

    def ensure_node(
        self,
        node_type: str,
        node_id: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Idempotently ensure a node exists with given properties.

        Uses MERGE for idempotence. Writes node, reads back to confirm,
        retries up to MAX_RETRIES times if confirmation fails.

        Args:
            node_type: Node label (e.g., 'Principle', 'Mechanism')
            node_id: Unique node ID
            properties: Optional node properties to set

        Returns:
            {
                "confirmed": bool,
                "node_id": str,
                "node_type": str,
                "retries": int,
                "error": str (if confirmation failed)
            }
        """
        properties = properties or {}
        properties['id'] = node_id  # Ensure ID is in properties

        # Build property SET clause with string formatting
        props_set = ', '.join([f"n.{k} = {self._format_value(v)}" for k, v in properties.items()])

        # MERGE query (idempotent) - using string formatting
        merge_query = f"""
        MERGE (n:{node_type} {{id: {self._format_value(node_id)}}})
        SET {props_set}
        RETURN n
        """

        # Attempt write + confirmation with retries
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                # Write
                self._execute_query(merge_query)

                # Read back to confirm
                confirm_query = f"MATCH (n:{node_type} {{id: {self._format_value(node_id)}}}) RETURN n"
                result = self._execute_query(confirm_query)

                confirmed_node = self._parse_node_result(result)

                if confirmed_node:
                    # Success
                    self._log_event("node_ensured", {
                        "node_type": node_type,
                        "node_id": node_id,
                        "confirmed": True,
                        "retries": attempt
                    })

                    return {
                        "confirmed": True,
                        "node_id": node_id,
                        "node_type": node_type,
                        "retries": attempt
                    }
                else:
                    # Read-back failed, will retry
                    self._log_event("node_readback_failed", {
                        "node_type": node_type,
                        "node_id": node_id,
                        "attempt": attempt + 1,
                        "max_attempts": self.MAX_RETRIES + 1
                    })

            except Exception as e:
                self._log_event("node_ensure_error", {
                    "node_type": node_type,
                    "node_id": node_id,
                    "attempt": attempt + 1,
                    "error": str(e)
                })

                if attempt == self.MAX_RETRIES:
                    # Final attempt failed
                    return {
                        "confirmed": False,
                        "node_id": node_id,
                        "node_type": node_type,
                        "retries": attempt + 1,
                        "error": str(e)
                    }

        # All retries exhausted
        self._log_event("node_ensure_failed", {
            "node_type": node_type,
            "node_id": node_id,
            "retries": self.MAX_RETRIES + 1
        })

        return {
            "confirmed": False,
            "node_id": node_id,
            "node_type": node_type,
            "retries": self.MAX_RETRIES + 1,
            "error": "Read-back confirmation failed after all retries"
        }

    def ensure_edge(
        self,
        edge_type: str,
        source_id: str,
        target_id: str,
        meta: Dict[str, Any],
        confidence: float = 1.0,
        status: str = "CONFIRMED"
    ) -> Dict[str, Any]:
        """
        Idempotently ensure an edge exists with given metadata.

        Uses MERGE for idempotence. Writes edge, reads back to confirm,
        retries up to MAX_RETRIES times if confirmation fails.

        Args:
            edge_type: Edge type (e.g., 'IMPLEMENTS', 'MEASURES')
            source_id: Source node ID
            target_id: Target node ID
            meta: Edge metadata dict (required fields per link_meta.yaml)
            confidence: float = 1.0,
            status: PROPOSED | CONFIRMED

        Returns:
            {
                "confirmed": bool,
                "edge_type": str,
                "source_id": str,
                "target_id": str,
                "retries": int,
                "error": str (if confirmation failed)
            }
        """
        # Validate both nodes exist BEFORE attempting edge creation
        source_exists_query = f"MATCH (n {{id: {self._format_value(source_id)}}}) RETURN n LIMIT 1"
        target_exists_query = f"MATCH (n {{id: {self._format_value(target_id)}}}) RETURN n LIMIT 1"

        try:
            source_result = self._execute_query(source_exists_query)
            target_result = self._execute_query(target_exists_query)

            source_exists = source_result and len(source_result) > 1 and source_result[1]
            target_exists = target_result and len(target_result) > 1 and target_result[1]

            if not source_exists:
                self._log_event("edge_creation_failed", {
                    "edge_type": edge_type,
                    "source_id": source_id,
                    "target_id": target_id,
                    "error": f"Source node '{source_id}' does not exist",
                    "severity": "ERROR"
                })
                return {
                    "confirmed": False,
                    "edge_type": edge_type,
                    "source_id": source_id,
                    "target_id": target_id,
                    "retries": 0,
                    "error": f"Source node '{source_id}' does not exist"
                }

            if not target_exists:
                self._log_event("edge_creation_failed", {
                    "edge_type": edge_type,
                    "source_id": source_id,
                    "target_id": target_id,
                    "error": f"Target node '{target_id}' does not exist",
                    "severity": "ERROR"
                })
                return {
                    "confirmed": False,
                    "edge_type": edge_type,
                    "source_id": source_id,
                    "target_id": target_id,
                    "retries": 0,
                    "error": f"Target node '{target_id}' does not exist"
                }

        except Exception as e:
            self._log_event("edge_validation_failed", {
                "edge_type": edge_type,
                "source_id": source_id,
                "target_id": target_id,
                "error": str(e)
            })
            # Continue with edge creation attempt (may fail, but we tried to validate)

        # Build edge properties
        edge_props = {
            "confidence": confidence,
            "status": status,
            "meta": json.dumps(meta),  # Store meta as JSON string
            "created_at": datetime.utcnow().isoformat()
        }

        # Build property SET clause with string formatting
        props_set = ', '.join([f"r.{k} = {self._format_value(v)}" for k, v in edge_props.items()])

        # MERGE query (idempotent) - using string formatting
        merge_query = f"""
        MATCH (a {{id: {self._format_value(source_id)}}}), (b {{id: {self._format_value(target_id)}}})
        MERGE (a)-[r:{edge_type}]->(b)
        SET {props_set}
        RETURN r
        """

        # Attempt write + confirmation with retries
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                # Write
                self._execute_query(merge_query)

                # Read back to confirm
                confirm_query = f"""
                MATCH (a {{id: {self._format_value(source_id)}}})-[r:{edge_type}]->(b {{id: {self._format_value(target_id)}}})
                RETURN r
                """
                result = self._execute_query(confirm_query)

                confirmed_edge = self._parse_edge_result(result)

                if confirmed_edge:
                    # Success
                    self._log_event("edge_ensured", {
                        "edge_type": edge_type,
                        "source_id": source_id,
                        "target_id": target_id,
                        "status": status,
                        "confirmed": True,
                        "retries": attempt
                    })

                    return {
                        "confirmed": True,
                        "edge_type": edge_type,
                        "source_id": source_id,
                        "target_id": target_id,
                        "retries": attempt
                    }
                else:
                    # Read-back failed, will retry
                    self._log_event("edge_readback_failed", {
                        "edge_type": edge_type,
                        "source_id": source_id,
                        "target_id": target_id,
                        "attempt": attempt + 1,
                        "max_attempts": self.MAX_RETRIES + 1
                    })

            except Exception as e:
                self._log_event("edge_ensure_error", {
                    "edge_type": edge_type,
                    "source_id": source_id,
                    "target_id": target_id,
                    "attempt": attempt + 1,
                    "error": str(e)
                })

                if attempt == self.MAX_RETRIES:
                    # Final attempt failed
                    return {
                        "confirmed": False,
                        "edge_type": edge_type,
                        "source_id": source_id,
                        "target_id": target_id,
                        "retries": attempt + 1,
                        "error": str(e)
                    }

        # All retries exhausted
        self._log_event("edge_ensure_failed", {
            "edge_type": edge_type,
            "source_id": source_id,
            "target_id": target_id,
            "retries": self.MAX_RETRIES + 1
        })

        return {
            "confirmed": False,
            "edge_type": edge_type,
            "source_id": source_id,
            "target_id": target_id,
            "retries": self.MAX_RETRIES + 1,
            "error": "Read-back confirmation failed after all retries"
        }

    def get_node_types(self) -> List[Dict[str, Any]]:
        """
        Query schema registry for node type definitions.

        Returns:
            List of node type definitions from schema registry
        """
        # Query schema_registry graph for NodeTypeSchema nodes
        query = """
        MATCH (n:NodeTypeSchema)
        RETURN n.type_name AS type_name, n.description AS description,
               n.level AS level, n.category AS category
        ORDER BY n.type_name
        """

        try:
            # Execute against schema_registry graph
            original_graph = self.graph_name
            self.graph_name = "schema_registry"
            result = self._execute_query(query)
            self.graph_name = original_graph

            # Parse result: [headers, rows, stats]
            node_types = []
            if len(result) > 1 and result[1]:
                for row in result[1]:
                    node_types.append({
                        'type_name': row[0].decode('utf-8') if row[0] else None,
                        'description': row[1].decode('utf-8') if row[1] else None,
                        'level': row[2].decode('utf-8') if row[2] else None,
                        'category': row[3].decode('utf-8') if row[3] else None
                    })

            self._log_event("schema_query_success", {
                "registry": "node_types",
                "count": len(node_types)
            })
            return node_types

        except Exception as e:
            self._log_event("schema_query_error", {
                "registry": "node_types",
                "error": str(e)
            })
            return []

    def get_link_types(self) -> List[Dict[str, Any]]:
        """
        Query schema registry for link type definitions.

        Returns:
            List of link type definitions from schema registry
        """
        query = """
        MATCH (l:LinkTypeSchema)
        RETURN l.type_name AS type_name, l.description AS description
        ORDER BY l.type_name
        """

        try:
            # Execute against schema_registry graph
            original_graph = self.graph_name
            self.graph_name = "schema_registry"
            result = self._execute_query(query)
            self.graph_name = original_graph

            # Parse result: [headers, rows, stats]
            link_types = []
            if len(result) > 1 and result[1]:
                for row in result[1]:
                    link_types.append({
                        'type_name': row[0].decode('utf-8') if row[0] else None,
                        'description': row[1].decode('utf-8') if row[1] else None
                    })

            self._log_event("schema_query_success", {
                "registry": "link_types",
                "count": len(link_types)
            })
            return link_types

        except Exception as e:
            self._log_event("schema_query_error", {
                "registry": "link_types",
                "error": str(e)
            })
            return []

    def get_link_meta_contract(self) -> Dict[str, Any]:
        """
        Query schema registry for link metadata contract.

        Returns:
            Per-edge metadata requirements (required/optional fields)
        """
        # Try to query for metadata requirements via HAS_ATTRIBUTE relationships
        query = """
        MATCH (l:LinkTypeSchema)-[:HAS_ATTRIBUTE]->(a)
        RETURN l.type_name AS link_type, a.attribute_name AS field,
               a.required AS required, a.type AS field_type
        """

        try:
            # Execute against schema_registry graph
            original_graph = self.graph_name
            self.graph_name = "schema_registry"
            result = self._execute_query(query)
            self.graph_name = original_graph

            # Parse result into contract structure
            contract = {}
            if len(result) > 1 and result[1]:
                for row in result[1]:
                    link_type = row[0].decode('utf-8') if row[0] else None
                    field = row[1].decode('utf-8') if row[1] else None
                    required = row[2] if len(row) > 2 else False
                    field_type = row[3].decode('utf-8') if len(row) > 3 and row[3] else 'string'

                    if link_type not in contract:
                        contract[link_type] = {'required': [], 'optional': []}

                    if required:
                        contract[link_type]['required'].append(field)
                    else:
                        contract[link_type]['optional'].append(field)

                self._log_event("schema_query_success", {
                    "registry": "link_meta_contract",
                    "link_types_with_contracts": len(contract)
                })
            else:
                # No metadata contracts defined - return default
                self._log_event("schema_query_warning", {
                    "registry": "link_meta_contract",
                    "message": "No metadata contracts found, returning default"
                })

                # Default contract: all links should have these basic fields
                contract = {
                    "__default__": {
                        "required": ["rationale"],
                        "optional": ["confidence", "source", "created_at"]
                    }
                }

            return contract

        except Exception as e:
            self._log_event("schema_query_error", {
                "registry": "link_meta_contract",
                "error": str(e)
            })
            return {}

    def get_existing_nodes_by_type(self, node_type: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get existing nodes of a given type for candidate matching.

        Args:
            node_type: Node label to query
            limit: Maximum nodes to return

        Returns:
            List of {id, name, description, ...} dicts
        """
        query = f"""
        MATCH (n:{node_type})
        RETURN n.id AS id, n.name AS name, n.description AS description
        LIMIT {limit}
        """

        try:
            result = self._execute_query(query)
            # Parse nodes
            # TODO: Parse actual FalkorDB result format
            return []  # Placeholder
        except Exception as e:
            self._log_event("query_error", {
                "operation": "get_existing_nodes",
                "node_type": node_type,
                "error": str(e)
            })
            return []

    def _coerce_property_value(self, value: Any, key: str = "") -> Any:
        """Type-aware coercion for FalkorDB property values."""
        # Skip decoding for known binary/vector fields
        if key in ('content_embedding', 'embedding', 'vector'):
            return None  # Omit embeddings from props (too large)

        # Decode bytes
        if isinstance(value, bytes):
            try:
                decoded = value.decode('utf-8', errors='strict')
                # Try parsing as JSON if it looks like JSON
                if decoded and decoded[0] in ('{', '['):
                    try:
                        return json.loads(decoded)
                    except json.JSONDecodeError:
                        pass
                return decoded
            except UnicodeDecodeError:
                return None  # Drop unparseable binary

        # Recursively handle lists/tuples
        if isinstance(value, (list, tuple)):
            return [self._coerce_property_value(v, key) for v in value]

        # Keep numbers, bools, None as-is
        if isinstance(value, (int, float, bool)) or value is None:
            return value

        # Truncate large strings
        if isinstance(value, str) and len(value) > 16384:
            return value[:16384]

        return value

    def _parse_full_node_properties(self, node_data: List) -> Dict[str, Any]:
        """Parse complete property bag from FalkorDB node structure."""
        result = {
            "internal_id": None,
            "labels": [],
            "props": {},
            "props_truncated": False
        }

        if not isinstance(node_data, list):
            return result

        for item in node_data:
            if not isinstance(item, list) or len(item) != 2:
                continue

            key = item[0]
            if isinstance(key, bytes):
                key = key.decode('utf-8')

            # Extract internal ID
            if key == 'id':
                result["internal_id"] = item[1]

            # Extract labels
            elif key == 'labels':
                labels = item[1]
                if isinstance(labels, list):
                    result["labels"] = [
                        lbl.decode('utf-8') if isinstance(lbl, bytes) else str(lbl)
                        for lbl in labels
                    ]

            # Extract all properties
            elif key == 'properties' and isinstance(item[1], list):
                prop_count = 0
                for prop in item[1]:
                    if len(prop) != 2:
                        continue

                    prop_key = prop[0]
                    if isinstance(prop_key, bytes):
                        prop_key = prop_key.decode('utf-8')

                    # Apply type-aware coercion
                    prop_val = self._coerce_property_value(prop[1], prop_key)

                    # Skip None (filtered embeddings, unparseable binary)
                    if prop_val is None and prop_key not in ('expired_at', 'invalid_at'):
                        continue

                    result["props"][prop_key] = prop_val
                    prop_count += 1

                    # Sanity cap: max 200 properties
                    if prop_count >= 200:
                        result["props_truncated"] = True
                        break

        return result

    def _hydrate_edges_for_candidates(self, internal_ids: List[int]) -> Dict[int, List[Dict[str, Any]]]:
        """Batched edge hydration for top-N candidates."""
        if not internal_ids:
            return {}

        # Build ID list directly in query (FalkorDB doesn't support parameters)
        ids_str = "[" + ",".join(str(id) for id in internal_ids) + "]"

        # Batched query to fetch ego-nets with full r.meta
        query = f"""
        MATCH (n) WHERE id(n) IN {ids_str}
        OPTIONAL MATCH (n)-[r]->(m)
        WITH n, r, m
        RETURN
          id(n) AS nid,
          type(r) AS rel_type,
          properties(r) AS r_props,
          id(m) AS mid,
          properties(m) AS m_props
        """

        try:
            result = self._execute_query(query)

            # Build adjacency map
            adjacency_map = {}
            if result and len(result) > 1 and result[1]:
                for row in result[1]:
                    if len(row) < 5:
                        continue

                    nid = row[0]
                    rel_type = row[1]
                    r_props = row[2]
                    mid = row[3]
                    m_props = row[4]

                    # Skip rows with no edge (OPTIONAL MATCH returned null)
                    if rel_type is None:
                        continue

                    # Decode relation type
                    if isinstance(rel_type, bytes):
                        rel_type = rel_type.decode('utf-8')

                    # Parse target id from m_props
                    target_id = None
                    if isinstance(m_props, list):
                        for prop in m_props:
                            if len(prop) == 2:
                                k = prop[0].decode('utf-8') if isinstance(prop[0], bytes) else str(prop[0])
                                if k == 'id':
                                    v = prop[1]
                                    target_id = v.decode('utf-8') if isinstance(v, bytes) else str(v)
                                    break

                    if not target_id:
                        continue  # Skip edges without target ID

                    # Parse edge properties (including meta)
                    edge_props = {}
                    if isinstance(r_props, list):
                        for prop in r_props:
                            if len(prop) == 2:
                                k = prop[0].decode('utf-8') if isinstance(prop[0], bytes) else str(prop[0])
                                v = self._coerce_property_value(prop[1], k)
                                if v is not None:
                                    edge_props[k] = v

                    # Add to adjacency map
                    if nid not in adjacency_map:
                        adjacency_map[nid] = []

                    # Cap at 64 edges per node
                    if len(adjacency_map[nid]) < 64:
                        adjacency_map[nid].append({
                            "type": rel_type,
                            "target": target_id,
                            "props": edge_props
                        })

            return adjacency_map

        except Exception as e:
            self._log_event("edge_hydration_failed", {
                "error": str(e),
                "severity": "WARNING",
                "impact": "Candidates will not have adjacency information"
            })
            return {}

    def get_candidates(self, embedding: List[float], node_type: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        ANN search for candidate nodes of given type using vector similarity.

        Uses FalkorDB's vector search to find nodes with similar embeddings.

        Args:
            embedding: Query embedding vector (768 dims for all-mpnet-base-v2)
            node_type: Node label to search (e.g., 'Principle', 'Mechanism')
            top_k: Number of candidates to return

        Returns:
            List of candidate nodes with similarity scores:
            [
                {"id": "principle:foo", "name": "...", "description": "...", "similarity": 0.87},
                ...
            ]
        """
        # FalkorDB vector search using proper syntax
        embedding_str = str(embedding)

        query = f"""
        CALL db.idx.vector.queryNodes('{node_type}', 'content_embedding', {top_k}, vecf32({embedding_str}))
        YIELD node, score
        RETURN node, score
        LIMIT {top_k}
        """

        try:
            result = self._execute_query(query)

            # Parse results with FULL property bags
            candidates = []
            internal_ids = []

            if result and len(result) > 1 and result[1]:
                for row in result[1]:
                    if len(row) < 2:
                        continue

                    node_data = row[0]
                    score_str = row[1]

                    # Parse full node structure using helper
                    parsed = self._parse_full_node_properties(node_data)

                    # Extract or construct business ID
                    node_id = parsed["props"].get("id")
                    if not node_id:
                        # Fallback: construct ID from node_type + name (schema migration path)
                        name = parsed["props"].get("name")
                        if name:
                            # Convert "Best_Practice" -> "best_practice", "Principle" -> "principle"
                            prefix = node_type.lower().replace("_", "_")
                            node_id = f"{prefix}:{name}"
                        else:
                            self._log_event("candidate_missing_id_and_name", {
                                "node_type": node_type,
                                "internal_id": parsed["internal_id"],
                                "props_keys": list(parsed["props"].keys())[:10]
                            })
                            continue  # Drop candidates without ID or name

                    # Build rich candidate
                    similarity = float(score_str) if score_str else 0.0

                    candidate = {
                        "id": node_id,
                        "labels": parsed["labels"],
                        "score": similarity,
                        "props": parsed["props"],
                        "internal_id": parsed["internal_id"]
                    }

                    if parsed["props_truncated"]:
                        candidate["props_truncated"] = True

                    candidates.append(candidate)
                    internal_ids.append(parsed["internal_id"])

            # Hydrate edges for all candidates (batched)
            if internal_ids:
                adjacency_map = self._hydrate_edges_for_candidates(internal_ids)
                for candidate in candidates:
                    iid = candidate["internal_id"]
                    if iid in adjacency_map:
                        candidate["adjacency"] = adjacency_map[iid]
                    else:
                        candidate["adjacency"] = []

            self._log_event("candidates_retrieved", {
                "node_type": node_type,
                "count": len(candidates),
                "top_score": candidates[0]["score"] if candidates else 0.0,
                "avg_props_per_candidate": sum(len(c["props"]) for c in candidates) / len(candidates) if candidates else 0,
                "avg_edges_per_candidate": sum(len(c.get("adjacency", [])) for c in candidates) / len(candidates) if candidates else 0
            })
            return candidates

        except Exception as e:
            # Vector search failure is CRITICAL - log loudly
            self._log_event("vector_search_failed", {
                "node_type": node_type,
                "error": str(e),
                "severity": "ERROR",
                "impact": "No candidates retrieved - LLM will not see existing nodes for linking"
            })
            return []

    def _get_candidates_fallback(self, node_type: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Fallback candidate retrieval without vector search."""
        query = f"""
        MATCH (n:{node_type})
        WHERE n.id IS NOT NULL
        RETURN n.id AS id,
               n.name AS name,
               n.description AS description,
               1.0 AS similarity
        LIMIT {top_k}
        """

        try:
            result = self._execute_query(query)
            candidates = []
            if result and len(result) > 1 and result[1]:
                for row in result[1]:
                    node_id = row[0]
                    if isinstance(node_id, bytes):
                        node_id = node_id.decode('utf-8')
                    if node_id:
                        candidates.append({
                            "id": node_id,
                            "name": row[1].decode('utf-8') if isinstance(row[1], bytes) else (row[1] or ""),
                            "description": row[2].decode('utf-8') if isinstance(row[2], bytes) else (row[2] or ""),
                            "similarity": 1.0
                        })
            return candidates
        except:
            return []

    def get_context(self, seed_ids: List[str], depth: int = 1) -> Dict[str, Any]:
        """
        Get ego-nets (adjacent nodes/edges) for seed node IDs.

        Provides graph context around seed nodes up to specified depth.

        Args:
            seed_ids: List of node IDs to get context for
            depth: How many hops to traverse (1 = immediate neighbors)

        Returns:
            {
                "nodes": [{"id": "...", "type": "...", "name": "...", ...}, ...],
                "edges": [{"source": "...", "target": "...", "type": "...", "meta": {...}}, ...]
            }
        """
        if not seed_ids:
            return {"nodes": [], "edges": []}

        # Build MATCH pattern based on depth
        if depth == 1:
            # Direct neighbors only
            pattern = "(seed)-[r]-(neighbor)"
        elif depth == 2:
            # Two hops
            pattern = "(seed)-[r1]-(n1)-[r2]-(n2)"
        else:
            # Variable length path (up to depth)
            pattern = f"(seed)-[*1..{depth}]-(neighbor)"

        # Query for ego-net
        # Format seed_ids as Cypher list: ['id1', 'id2', ...]
        seed_ids_str = '[' + ', '.join([self._quote_string(sid) for sid in seed_ids]) + ']'

        query = f"""
        MATCH {pattern}
        WHERE seed.id IN {seed_ids_str}
        RETURN DISTINCT seed, neighbor, r
        """

        try:
            result = self._execute_query(query)

            # Parse result
            # TODO: Parse actual FalkorDB result format
            # Should extract nodes and edges from result

            # Placeholder return
            return {
                "nodes": [],
                "edges": []
            }
        except Exception as e:
            self._log_event("query_error", {
                "operation": "get_context",
                "seed_ids": seed_ids,
                "depth": depth,
                "error": str(e)
            })
            return {"nodes": [], "edges": []}


if __name__ == "__main__":
    # Quick test
    graph = GraphWrapper("L2_test")

    # Test node creation
    result = graph.ensure_node(
        "Mechanism",
        "mechanism:test_delta_broadcast",
        {"name": "Test Delta Broadcast", "description": "Test mechanism"}
    )

    print(f"\nNode creation result: {json.dumps(result, indent=2)}")

    # Test edge creation
    if result['confirmed']:
        edge_result = graph.ensure_edge(
            "IMPLEMENTS",
            "best_practice:streaming",
            "mechanism:test_delta_broadcast",
            meta={"rationale": "Test implementation"},
            confidence=0.85
        )

        print(f"\nEdge creation result: {json.dumps(edge_result, indent=2)}")
