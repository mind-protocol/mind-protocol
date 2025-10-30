"""
Custom Extraction Layer - Direct Pydantic Validation

This module replaces LlamaIndex's SchemaLLMPathExtractor with our own transparent
extraction and validation layer. It:
1. Uses CustomClaudeCodeLLM to generate JSON
2. Validates JSON directly against Ada's Pydantic schema
3. Returns validated objects ready for FalkorDB insertion

This makes Ada's consciousness_schema.py the single source of truth.
No black boxes, no mystery - just: does Pydantic validate? Yes = valid data.

Designer: Felix (Engineer)
Phase: 1 - Foundation & Schema (Refactored after testing)
Date: 2025-10-16
"""

import json
from typing import List, Dict, Any, Tuple
from datetime import datetime

from substrate.schemas.consciousness_schema import (
    get_node_type_by_name,
    get_relation_type_by_name,
    BaseNode,
    BaseRelation
)


# Extraction prompt template
EXTRACTION_PROMPT_TEMPLATE = """
You are extracting consciousness graph data from text.

Extract nodes (subentities) and relations (connections) that match our consciousness schema.

**Available Node Types:**
{node_types}

**Available Relation Types:**
{relation_types}

**CRITICAL - Every Relation Must Include:**
- goal (string): Why this link exists
- mindstate (string): Internal subentity state during formation
- confidence (float 0.0-1.0): Logical certainty
- formation_trigger (enum): How discovered (direct_experience, inference, systematic_analysis, etc.)

Note: Energy-only model - no energy field

**Input Text:**
{text}

**Instructions:**
1. Extract all meaningful nodes and relations
2. Use exact type names from the lists above
3. Every node needs: name (unique ID), description, formation_trigger, confidence
4. Every relation needs: source_node, target_node, and ALL 4 required consciousness fields (goal, mindstate, confidence, formation_trigger)
5. Include type-specific required fields (e.g., Decision needs: decided_by, decision_date, rationale)
6. **CRITICAL: Use ONLY ASCII characters. NO unicode symbols (no checkmarks, no special quotes, no em-dashes)**

**Return valid JSON in this exact format:**
{{
  "nodes": [
    {{
      "type": "NodeTypeName",
      "data": {{
        "name": "unique_identifier",
        "description": "what this represents",
        "formation_trigger": "direct_experience",
        "confidence": 0.95,
        ... type-specific fields ...
      }}
    }}
  ],
  "relations": [
    {{
      "type": "RELATION_TYPE",
      "source_node": "source_name",
      "target_node": "target_name",
      "data": {{
        "goal": "why this link",
        "mindstate": "subentity state",
        "confidence": 0.9,
        "formation_trigger": "inference",
        ... type-specific fields ...
      }}
    }}
  ]
}}

Return ONLY the JSON, no additional text.
"""


class ExtractionResult:
    """Result of extraction and validation"""

    def __init__(self):
        self.nodes: List[BaseNode] = []
        self.relations: List[Tuple[str, str, BaseRelation]] = []  # (source, target, relation)
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[str] = []

    def add_node(self, node: BaseNode):
        self.nodes.append(node)

    def add_relation(self, source: str, target: str, relation: BaseRelation):
        self.relations.append((source, target, relation))

    def add_error(self, error_type: str, message: str, data: Any = None):
        self.errors.append({
            "type": error_type,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })

    def add_warning(self, message: str):
        self.warnings.append(message)

    @property
    def success(self) -> bool:
        """Extraction succeeded if we have nodes or relations and no critical errors"""
        return (len(self.nodes) > 0 or len(self.relations) > 0) and len(self.errors) == 0

    @property
    def partial_success(self) -> bool:
        """Partial success if we have some valid data but also errors"""
        return (len(self.nodes) > 0 or len(self.relations) > 0) and len(self.errors) > 0


def extract_and_validate(
    text: str,
    llm,  # CustomClaudeCodeLLM instance
    node_types: List[type],
    relation_types: List[type]
) -> ExtractionResult:
    """
    Extract subentities and relations from text, validating against Ada's schema.

    This is the core extraction function that replaces SchemaLLMPathExtractor.

    Args:
        text: Raw text to extract from
        llm: CustomClaudeCodeLLM instance for generation
        node_types: List of Pydantic node classes from Ada's schema
        relation_types: List of Pydantic relation classes from Ada's schema

    Returns:
        ExtractionResult with validated nodes, relations, and any errors

    Process:
        1. Generate extraction prompt with schema info
        2. Call LLM to generate JSON
        3. Parse JSON
        4. Validate each node/relation with Pydantic
        5. Return validated objects + errors
    """
    result = ExtractionResult()

    try:
        # Step 1: Build extraction prompt
        node_type_names = [cls.__name__ for cls in node_types]
        relation_type_names = [cls.__name__ for cls in relation_types]

        prompt = EXTRACTION_PROMPT_TEMPLATE.format(
            node_types=", ".join(node_type_names),
            relation_types=", ".join(relation_type_names),
            text=text
        )

        print("[Extraction] Calling LLM for subentity/relation extraction...")

        # Step 2: Generate JSON with LLM
        response = llm.complete(prompt)
        json_text = response.text.strip()

        # Strip unicode characters that cause Windows encoding issues
        # Replace common unicode with ASCII equivalents
        json_text = json_text.replace('\u2713', '[OK]')  # Checkmark -> [OK]
        json_text = json_text.replace('\u2714', '[OK]')  # Heavy checkmark
        json_text = json_text.replace('\u2718', '[X]')   # X mark
        json_text = json_text.replace('\u2012', '-')     # En dash -> hyphen
        json_text = json_text.replace('\u2013', '-')     # En dash
        json_text = json_text.replace('\u2014', '-')     # Em dash
        json_text = json_text.replace('\u2018', "'")     # Left single quote
        json_text = json_text.replace('\u2019', "'")     # Right single quote
        json_text = json_text.replace('\u201c', '"')     # Left double quote
        json_text = json_text.replace('\u201d', '"')     # Right double quote
        # Remove any remaining non-ASCII characters
        json_text = json_text.encode('ascii', 'ignore').decode('ascii')

        # Clean potential markdown code blocks
        if json_text.startswith("```"):
            json_text = json_text.split("```")[1]
            if json_text.startswith("json"):
                json_text = json_text[4:]
        json_text = json_text.strip()

        print(f"[Extraction] LLM returned {len(json_text)} chars")

        # Step 3: Parse JSON
        try:
            extracted_data = json.loads(json_text)
        except json.JSONDecodeError as e:
            result.add_error("json_parse_error", f"Failed to parse JSON: {str(e)}", json_text)
            return result

        # Step 4: Validate nodes
        for node_entry in extracted_data.get("nodes", []):
            try:
                node_type_name = node_entry.get("type")
                node_data = node_entry.get("data", {})

                if not node_type_name:
                    result.add_error("missing_node_type", "Node entry missing 'type' field", node_entry)
                    continue

                # Get Pydantic class for this node type
                node_class = get_node_type_by_name(node_type_name)
                if not node_class:
                    result.add_error(
                        "unknown_node_type",
                        f"Unknown node type: {node_type_name}",
                        node_entry
                    )
                    continue

                # Validate with Pydantic - this is where schema enforcement happens
                validated_node = node_class(**node_data)
                result.add_node(validated_node)

                print(f"[Extraction] [OK] Validated node: {node_type_name} ({validated_node.name})")

            except Exception as e:
                result.add_error(
                    "node_validation_error",
                    f"Failed to validate {node_entry.get('type', 'unknown')}: {str(e)}",
                    node_entry
                )

        # Step 5: Validate relations
        for rel_entry in extracted_data.get("relations", []):
            try:
                rel_type_name = rel_entry.get("type")
                source_node = rel_entry.get("source_node")
                target_node = rel_entry.get("target_node")
                rel_data = rel_entry.get("data", {})

                if not rel_type_name:
                    result.add_error("missing_relation_type", "Relation entry missing 'type' field", rel_entry)
                    continue

                if not source_node or not target_node:
                    result.add_error(
                        "missing_relation_nodes",
                        "Relation missing source_node or target_node",
                        rel_entry
                    )
                    continue

                # Get Pydantic class for this relation type
                rel_class = get_relation_type_by_name(rel_type_name)
                if not rel_class:
                    result.add_error(
                        "unknown_relation_type",
                        f"Unknown relation type: {rel_type_name}",
                        rel_entry
                    )
                    continue

                # Validate with Pydantic - schema enforcement
                validated_relation = rel_class(**rel_data)
                result.add_relation(source_node, target_node, validated_relation)

                print(f"[Extraction] [OK] Validated relation: {rel_type_name} ({source_node} -> {target_node})")

            except Exception as e:
                result.add_error(
                    "relation_validation_error",
                    f"Failed to validate {rel_entry.get('type', 'unknown')}: {str(e)}",
                    rel_entry
                )

        # Step 6: Summary
        print(f"[Extraction] Complete:")
        print(f"  Valid nodes: {len(result.nodes)}")
        print(f"  Valid relations: {len(result.relations)}")
        print(f"  Errors: {len(result.errors)}")

        return result

    except Exception as e:
        result.add_error("extraction_failed", f"Extraction process failed: {str(e)}")
        return result
