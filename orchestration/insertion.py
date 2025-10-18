"""
Insertion Module - Write Flux (Red Arrow) Implementation

This module implements the "Write Flux" - the ability for Couche 3 (Mind) to create
new memories in Couche 1 (Brain) via Couche 2 (Custom Extraction + Pydantic Validation).

Flow:
1. Hook catches text stimulus
2. Hook calls ingest_text(text, graph_name)
3. Custom extraction layer uses CustomClaudeCodeLLM to generate JSON
4. Direct Pydantic validation against Ada's consciousness_schema.py
5. Valid data is written to FalkorDB

Designer: Felix (Engineer)
Phase: 1 - Foundation & Schema (Refactored after testing)
Date: 2025-10-16
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add substrate to path for schema imports
sys.path.insert(0, str(Path(__file__).parent.parent / "substrate"))

# Import our custom extraction layer (replaces LlamaIndex SchemaLLMPathExtractor)
from orchestration.extraction import extract_and_validate

# Import FalkorDB for graph storage
from llama_index.graph_stores.falkordb import FalkorDBGraphStore

# Import our custom LLM wrapper
from orchestration.custom_claude_llm import create_claude_llm

# Import Ada's schema registry
from substrate.schemas.consciousness_schema import NODE_TYPES, RELATION_TYPES

# Import local embedding model for semantic layer
from sentence_transformers import SentenceTransformer

# Import serialization layer to handle FalkorDB primitive-type constraint
from substrate.schemas.serialization import serialize_dict_fields, verify_no_nested_dicts


def strip_unicode_from_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively strip unicode characters from all string values in a dict.

    This prevents Windows encoding errors when writing to FalkorDB.
    """
    if isinstance(data, dict):
        return {k: strip_unicode_from_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [strip_unicode_from_dict(item) for item in data]
    elif isinstance(data, str):
        # Strip unicode characters, replace common ones with ASCII
        cleaned = data.replace('\u2713', '[OK]')  # Checkmark
        cleaned = cleaned.replace('\u2714', '[OK]')  # Heavy checkmark
        cleaned = cleaned.replace('\u2718', '[X]')   # X mark
        cleaned = cleaned.replace('\u2012', '-')     # En dash
        cleaned = cleaned.replace('\u2013', '-')     # En dash
        cleaned = cleaned.replace('\u2014', '-')     # Em dash
        cleaned = cleaned.replace('\u2018', "'")     # Left single quote
        cleaned = cleaned.replace('\u2019', "'")     # Right single quote
        cleaned = cleaned.replace('\u201c', '"')     # Left double quote
        cleaned = cleaned.replace('\u201d', '"')     # Right double quote
        cleaned = cleaned.replace('\u20ac', 'EUR')   # Euro symbol
        # Remove any remaining non-ASCII
        return cleaned.encode('ascii', 'ignore').decode('ascii')
    else:
        return data


class ConsciousnessIngestionEngine:
    """
    Engine for ingesting text into consciousness graphs.

    This class encapsulates the Write Flux - it takes raw text and writes
    structured, schema-compliant consciousness data to FalkorDB.
    """

    def __init__(
        self,
        falkordb_host: str = "localhost",
        falkordb_port: int = 6379,
        claude_working_dir: Optional[str] = None,
        claude_timeout: int = 120
    ):
        """
        Initialize the ingestion engine.

        Args:
            falkordb_host: FalkorDB server host
            falkordb_port: FalkorDB server port
            claude_working_dir: Working directory for Claude Code shell commands
            claude_timeout: Timeout for Claude Code execution (seconds)
        """
        self.falkordb_host = falkordb_host
        self.falkordb_port = falkordb_port
        self.claude_working_dir = claude_working_dir

        # Initialize CustomClaudeCodeLLM
        self.llm = create_claude_llm(
            working_dir=claude_working_dir,
            timeout=claude_timeout
        )

        # Store schema for extraction (no black box extractor)
        self.node_types = NODE_TYPES
        self.relation_types = RELATION_TYPES

        # Initialize local embedding model for semantic layer
        print(f"[ConsciousnessIngestionEngine] Loading embedding model...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        print(f"[ConsciousnessIngestionEngine] Initialized")
        print(f"  FalkorDB: {falkordb_host}:{falkordb_port}")
        print(f"  Schema: {len(NODE_TYPES)} node types, {len(RELATION_TYPES)} relation types")
        print(f"  Extraction: Custom layer with direct Pydantic validation")
        print(f"  Embeddings: Local model (all-MiniLM-L6-v2, {embedding_dim} dimensions)")
        print(f"  Claude working dir: {claude_working_dir or 'current directory'}")

    def ingest_text(
        self,
        text: str,
        graph_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest text into a consciousness graph.

        This is the main entry point for the Write Flux. It:
        1. Extracts entities and relations using custom extraction layer
        2. Validates directly with Ada's Pydantic models
        3. Writes validated objects to FalkorDB graph

        Args:
            text: Raw text to ingest (e.g., conversation, stimulus, observation)
            graph_name: Target FalkorDB graph (e.g., "citizen_Luca", "collective_n2")
            metadata: Optional metadata to attach to extraction

        Returns:
            Dict containing ingestion results:
            {
                "status": "success" | "partial" | "failed",
                "nodes_created": int,
                "relations_created": int,
                "errors": List[str],
                "timestamp": datetime
            }

        Raises:
            ValueError: If text is empty or graph_name is invalid
            RuntimeError: If FalkorDB connection fails
        """
        if not text or not text.strip():
            raise ValueError("Cannot ingest empty text")

        if not graph_name or not graph_name.strip():
            raise ValueError("graph_name must be provided")

        print(f"\n[Ingestion] Starting for graph: {graph_name}")
        print(f"[Ingestion] Text length: {len(text)} chars")

        result = {
            "status": "pending",
            "nodes_created": 0,
            "relations_created": 0,
            "errors": [],
            "timestamp": datetime.utcnow()
        }

        try:
            # Step 1: Extract and validate using our custom layer
            print(f"[Ingestion] Extracting and validating with custom layer...")
            extraction_result = extract_and_validate(
                text=text,
                llm=self.llm,
                node_types=self.node_types,
                relation_types=self.relation_types
            )

            # Step 2: Check extraction result
            if extraction_result.errors:
                for error in extraction_result.errors:
                    result["errors"].append(f"{error['type']}: {error['message']}")

            if not extraction_result.success and not extraction_result.partial_success:
                result["status"] = "failed"
                print(f"[Ingestion] Extraction failed - no valid data extracted")
                return result

            print(f"[Ingestion] Extraction complete:")
            print(f"  Valid nodes: {len(extraction_result.nodes)}")
            print(f"  Valid relations: {len(extraction_result.relations)}")
            if extraction_result.errors:
                print(f"  Validation errors: {len(extraction_result.errors)}")

            # Step 3: Create FalkorDB connection for target graph
            print(f"[Ingestion] Connecting to FalkorDB graph: {graph_name}")
            falkordb_url = f"redis://{self.falkordb_host}:{self.falkordb_port}"
            graph_store = FalkorDBGraphStore(
                graph_name=graph_name,
                url=falkordb_url
            )

            # Step 4: Write validated nodes to FalkorDB using Cypher
            print(f"[Ingestion] Writing {len(extraction_result.nodes)} nodes to FalkorDB...")
            for node in extraction_result.nodes:
                try:
                    # Convert Pydantic model to dict, serialize datetime objects
                    node_dict = node.model_dump(mode='json')
                    node_type = node.__class__.__name__

                    # Strip unicode to prevent Windows encoding errors
                    node_dict = strip_unicode_from_dict(node_dict)

                    # Generate embedding for semantic search
                    # Combine name + description for richer semantic representation
                    text_to_embed = f"{node_dict.get('name', '')}: {node_dict.get('description', '')}" \
                                   if node_dict.get('description') else node_dict.get('name', '')
                    embedding = self.embedding_model.encode(text_to_embed).tolist()
                    node_dict['embedding'] = embedding

                    # CRITICAL: Serialize complex dict fields to JSON strings for FalkorDB
                    # FalkorDB constraint: Property values must be primitives or arrays of primitives
                    node_dict_serialized = serialize_dict_fields(node_dict)

                    # Safety check: Verify no nested dicts remain
                    if not verify_no_nested_dicts(node_dict_serialized):
                        raise ValueError(f"Node {node.name} still contains nested dicts after serialization")

                    # Build Cypher CREATE with serialized properties (no nested dicts)
                    cypher = f"""
                    MERGE (n:{node_type} {{name: $name}})
                    SET n += $properties
                    """

                    graph_store.query(cypher, params={
                        "name": node_dict_serialized["name"],
                        "properties": node_dict_serialized
                    })
                    result["nodes_created"] += 1
                    print(f"  [OK] Wrote {node_type}: {node.name} (with {len(embedding)}-dim embedding)")
                except Exception as e:
                    error_msg = f"Failed to write node {node.name}: {str(e)}"
                    result["errors"].append(error_msg)
                    print(f"[ERROR] {error_msg}")

            # Step 5: Write validated relations to FalkorDB using Cypher
            print(f"[Ingestion] Writing {len(extraction_result.relations)} relations to FalkorDB...")
            for source, target, relation in extraction_result.relations:
                try:
                    # Convert Pydantic model to dict, serialize datetime objects
                    relation_dict = relation.model_dump(mode='json')
                    relation_type = relation.__class__.__name__

                    # Strip unicode to prevent Windows encoding errors
                    relation_dict = strip_unicode_from_dict(relation_dict)

                    # CRITICAL: Serialize complex dict fields to JSON strings for FalkorDB
                    relation_dict_serialized = serialize_dict_fields(relation_dict)

                    # Safety check: Verify no nested dicts remain
                    if not verify_no_nested_dicts(relation_dict_serialized):
                        raise ValueError(f"Relation {source} -> {target} still contains nested dicts after serialization")

                    # Build Cypher CREATE with serialized properties (no nested dicts)
                    cypher = f"""
                    MATCH (source {{name: $source_name}})
                    MATCH (target {{name: $target_name}})
                    MERGE (source)-[r:{relation_type}]->(target)
                    SET r += $properties
                    """

                    graph_store.query(cypher, params={
                        "source_name": source,
                        "target_name": target,
                        "properties": relation_dict_serialized
                    })
                    result["relations_created"] += 1
                    print(f"  [OK] Wrote {relation_type}: {source} -> {target}")
                except Exception as e:
                    error_msg = f"Failed to write relation {source} -> {target}: {str(e)}"
                    result["errors"].append(error_msg)
                    print(f"[ERROR] {error_msg}")

            # Step 5: Determine final status
            if result["errors"]:
                if result["nodes_created"] > 0 or result["relations_created"] > 0:
                    result["status"] = "partial"
                else:
                    result["status"] = "failed"
            else:
                result["status"] = "success"

            print(f"[Ingestion] Complete - Status: {result['status']}")
            print(f"  Nodes created: {result['nodes_created']}")
            print(f"  Relations created: {result['relations_created']}")
            if result["errors"]:
                print(f"  Errors: {len(result['errors'])}")

            return result

        except Exception as e:
            result["status"] = "failed"
            error_msg = f"Ingestion failed: {str(e)}"
            result["errors"].append(error_msg)
            print(f"[ERROR] {error_msg}")
            raise RuntimeError(error_msg) from e


# Convenience function for simple ingestion
def ingest_text(
    text: str,
    graph_name: str,
    falkordb_host: str = "localhost",
    falkordb_port: int = 6379,
    claude_working_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Simple function for ingesting text into a consciousness graph.

    This is the main API for Couche 3 (Hooks) to call.

    Args:
        text: Raw text to ingest
        graph_name: Target FalkorDB graph name
        falkordb_host: FalkorDB server host
        falkordb_port: FalkorDB server port
        claude_working_dir: Working directory for Claude Code

    Returns:
        Ingestion result dict

    Example:
        from orchestration.insertion import ingest_text

        result = ingest_text(
            text="Nicolas asked us to start V2 implementation",
            graph_name="citizen_Luca"
        )

        if result["status"] == "success":
            print(f"Created {result['nodes_created']} nodes")
    """
    engine = ConsciousnessIngestionEngine(
        falkordb_host=falkordb_host,
        falkordb_port=falkordb_port,
        claude_working_dir=claude_working_dir
    )

    return engine.ingest_text(text, graph_name)


if __name__ == "__main__":
    # Quick test when run directly
    print("=" * 60)
    print("CONSCIOUSNESS INGESTION ENGINE - Quick Test")
    print("=" * 60)

    test_text = """
    Decision: We chose FalkorDB + LlamaIndex + Native Vectors for V2.
    Rationale: This stack solves multi-tenancy, complexity, and scale.
    Decided by: Luca + Ada + Felix on 2025-10-16.
    """

    try:
        result = ingest_text(
            text=test_text,
            graph_name="test_ingestion"
        )

        print("\n" + "=" * 60)
        print(f"[RESULT] Status: {result['status']}")
        print(f"[RESULT] Nodes: {result['nodes_created']}")
        print(f"[RESULT] Relations: {result['relations_created']}")
        if result['errors']:
            print(f"[RESULT] Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"  - {error}")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
