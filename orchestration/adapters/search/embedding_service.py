"""
Consciousness Embedding Service - Generate semantic embeddings for substrate nodes and links

Implements the embedding architecture from consciousness_embedding_architecture.md:
- Generates embeddable_text from semantic fields (not metadata like timestamps/IDs)
- Calls embedding model (SentenceTransformers or Ollama) to create 768-dim vectors
- Returns both text and embedding for storage in FalkorDB

Dual backend support:
- Primary: SentenceTransformers (all-mpnet-base-v2) - works immediately, CPU-friendly
- Alternative: Ollama (nomic-embed-text) - requires Ollama server installation

Author: Felix "Ironhand"
Date: 2025-10-20
Pattern: Zero-cost local embeddings for consciousness archaeology
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Generates embeddings for consciousness substrate nodes and links.

    Uses local models (zero API cost) to create semantic embeddings
    that enable consciousness archaeology queries:
    - Find similar coping mechanisms
    - Trace reasoning evolution
    - Discover mental state patterns
    - Search by phenomenology (felt_as, mindstate, struggle)
    """

    def __init__(self, backend: str = 'sentence-transformers'):
        """
        Initialize embedding service.

        Args:
            backend: 'sentence-transformers' or 'ollama'
                sentence-transformers: Pure Python, works immediately
                ollama: Requires Ollama server running
        """
        self.backend = backend
        self.embedding_dim = 768
        self.model = None

        if backend == 'sentence-transformers':
            self._init_sentence_transformers()
        elif backend == 'ollama':
            self._init_ollama()
        else:
            raise ValueError(f"Unknown backend: {backend}")

    def _init_sentence_transformers(self):
        """Initialize SentenceTransformers backend (all-mpnet-base-v2)."""
        try:
            from sentence_transformers import SentenceTransformer

            # all-mpnet-base-v2: 768 dims, SOTA performance, CPU-friendly
            self.model = SentenceTransformer('all-mpnet-base-v2')
            logger.info("[EmbeddingService] Loaded SentenceTransformer: all-mpnet-base-v2 (768 dims)")

        except ImportError:
            logger.error("[EmbeddingService] sentence-transformers not installed. Run: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"[EmbeddingService] Failed to load SentenceTransformer: {e}")
            raise

    def _init_ollama(self):
        """Initialize Ollama backend (nomic-embed-text)."""
        try:
            import ollama

            # Verify Ollama is running and has nomic-embed-text model
            models = ollama.list()
            if 'nomic-embed-text' not in [m['name'] for m in models.get('models', [])]:
                logger.warning("[EmbeddingService] nomic-embed-text not found. Run: ollama pull nomic-embed-text")

            self.model = 'nomic-embed-text'
            logger.info("[EmbeddingService] Using Ollama backend: nomic-embed-text (768 dims)")

        except ImportError:
            logger.error("[EmbeddingService] ollama not installed. Run: pip install ollama")
            raise
        except Exception as e:
            logger.error(f"[EmbeddingService] Failed to connect to Ollama: {e}")
            raise

    def embed(self, text: str) -> List[float]:
        """
        Generate 768-dim embedding from text.

        Args:
            text: Embeddable text (semantic content)

        Returns:
            768-dimensional embedding vector
        """
        if not text or not text.strip():
            logger.warning("[EmbeddingService] Empty text provided for embedding")
            return [0.0] * self.embedding_dim

        try:
            if self.backend == 'sentence-transformers':
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()

            elif self.backend == 'ollama':
                import ollama
                response = ollama.embeddings(
                    model=self.model,
                    prompt=text
                )
                return response['embedding']

        except Exception as e:
            logger.error(f"[EmbeddingService] Embedding generation failed: {e}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dim

    def create_node_embeddable_text(self, node_type: str, fields: Dict[str, Any]) -> str:
        """
        Generate embeddable text from node fields based on type.

        Principle: Embed human-readable semantic content, not metadata.
        Include: names, descriptions, phenomenology, context
        Exclude: timestamps, IDs, numeric values, status enums

        Args:
            node_type: Type of node (e.g., 'Realization', 'Decision')
            fields: Parsed fields from formation block

        Returns:
            Embeddable text string ready for embedding
        """

        # Level 1: Personal Node Types
        if node_type == 'Realization':
            # Template: {what_i_realized}. Context: {context_when_discovered}
            return f"{fields.get('what_i_realized', '')}. Context: {fields.get('context_when_discovered', '')}"

        elif node_type == 'Memory':
            # Template: {content}
            return fields.get('content', '')

        elif node_type == 'Personal_Pattern':
            # Template: {behavior_description}
            return fields.get('behavior_description', '')

        elif node_type == 'Personal_Goal':
            # Template: {goal_description}. Why: {why_it_matters}
            return f"{fields.get('goal_description', '')}. Why: {fields.get('why_it_matters', '')}"

        elif node_type == 'Coping_Mechanism':
            # Template: {mechanism_description}. Protects from: {what_it_protects_from}
            return f"{fields.get('mechanism_description', '')}. Protects from: {fields.get('what_it_protects_from', '')}"

        elif node_type == 'Trigger':
            # Template: {stimulus_description}. Activates: {activated_entities}
            subentities = fields.get('activated_entities', [])
            entities_str = ', '.join(subentities) if isinstance(subentities, list) else str(subentities)
            return f"{fields.get('stimulus_description', '')}. Activates: {entities_str}"

        elif node_type == 'Wound':
            # Template: {what_happened}. Impact: {emotional_impact}
            return f"{fields.get('what_happened', '')}. Impact: {fields.get('emotional_impact', '')}"

        elif node_type == 'Person':
            # Template: {name}, {relationship_type}
            return f"{fields.get('name', '')}, {fields.get('relationship_type', '')}"

        elif node_type == 'Relationship':
            # Template: Relationship with {with_person}
            return f"Relationship with {fields.get('with_person', '')}"

        elif node_type == 'Conversation':
            # Template: Conversation with {with_person}
            return f"Conversation with {fields.get('with_person', '')}"

        elif node_type == 'Personal_Value':
            # Template: {value_statement}. Why: {why_i_hold_it}
            return f"{fields.get('value_statement', '')}. Why: {fields.get('why_i_hold_it', '')}"

        # Level 2: Organizational Node Types
        elif node_type == 'Principle':
            # Template: {principle_statement}. Why: {why_it_matters}
            return f"{fields.get('principle_statement', '')}. Why: {fields.get('why_it_matters', '')}"

        elif node_type == 'Best_Practice':
            # Template: {description}. How: {how_to_apply}
            how_to = fields.get('how_to_apply', [])
            how_to_str = '. '.join(how_to) if isinstance(how_to, list) else str(how_to)
            return f"{fields.get('description', '')}. How: {how_to_str}"

        elif node_type == 'Anti_Pattern':
            # Template: {description}
            return fields.get('description', '')

        elif node_type == 'Decision':
            # Template: {rationale}. Decided: {decision_date}
            return f"{fields.get('rationale', '')}. Decided: {fields.get('decision_date', '')}"

        elif node_type == 'Process':
            # Template: {description}. Steps: {steps}
            steps = fields.get('steps', [])
            steps_str = '. '.join(steps) if isinstance(steps, list) else str(steps)
            return f"{fields.get('description', '')}. Steps: {steps_str}"

        elif node_type == 'Mechanism':
            # Template: {how_it_works}. Inputs: {inputs}. Outputs: {outputs}
            return f"{fields.get('how_it_works', '')}. Inputs: {fields.get('inputs', '')}. Outputs: {fields.get('outputs', '')}"

        elif node_type == 'AI_Agent':
            # Template: {name}, {role}. Expertise: {expertise}
            expertise = fields.get('expertise', [])
            expertise_str = ', '.join(expertise) if isinstance(expertise, list) else str(expertise)
            return f"{fields.get('name', '')}, {fields.get('role', '')}. Expertise: {expertise_str}"

        elif node_type == 'Human':
            # Template: {name}, {role}. Expertise: {expertise}
            expertise = fields.get('expertise', [])
            expertise_str = ', '.join(expertise) if isinstance(expertise, list) else str(expertise)
            return f"{fields.get('name', '')}, {fields.get('role', '')}. Expertise: {expertise_str}"

        elif node_type == 'Team':
            # Template: {name}. Purpose: {purpose}
            return f"{fields.get('name', '')}. Purpose: {fields.get('purpose', '')}"

        elif node_type == 'Project':
            # Template: {name}. Goals: {goals}
            goals = fields.get('goals', [])
            goals_str = ', '.join(goals) if isinstance(goals, list) else str(goals)
            return f"{fields.get('name', '')}. Goals: {goals_str}"

        elif node_type == 'Task':
            # Template: {description}
            return fields.get('description', '')

        elif node_type == 'Milestone':
            # Template: {achievement_description}
            return fields.get('achievement_description', '')

        elif node_type == 'Risk':
            # Template: {description}
            return fields.get('description', '')

        elif node_type == 'Metric':
            # Template: {description}. Method: {measurement_method}
            return f"{fields.get('description', '')}. Method: {fields.get('measurement_method', '')}"

        elif node_type == 'Department':
            # Template: {name}. Function: {function}
            return f"{fields.get('name', '')}. Function: {fields.get('function', '')}"

        elif node_type == 'Code':
            # Template: {purpose}. Language: {language}
            return f"{fields.get('purpose', '')}. Language: {fields.get('language', '')}"

        # Shared: Knowledge Node Types
        elif node_type == 'Concept':
            # Template: {definition}
            return fields.get('definition', '')

        elif node_type == 'Document':
            # Template: {description}. Type: {document_type}
            return f"{fields.get('description', '')}. Type: {fields.get('document_type', '')}"

        elif node_type == 'Documentation':
            # Template: {description}
            return fields.get('description', '')

        # Level 3: Ecosystem Node Types
        elif node_type == 'Company':
            # Template: {name}. Type: {company_type}
            return f"{fields.get('name', '')}. Type: {fields.get('company_type', '')}"

        elif node_type == 'External_Person':
            # Template: {name}, {person_type}
            return f"{fields.get('name', '')}, {fields.get('person_type', '')}"

        elif node_type == 'Post':
            # Template: {content}. By: {author}
            return f"{fields.get('content', '')}. By: {fields.get('author', '')}"

        elif node_type == 'Transaction':
            # Template: Transfer from {from_address} to {to_address}
            return f"Transfer from {fields.get('from_address', '')} to {fields.get('to_address', '')}"

        elif node_type == 'Smart_Contract':
            # Template: {name}. Type: {contract_type}
            return f"{fields.get('name', '')}. Type: {fields.get('contract_type', '')}"

        elif node_type == 'Wallet_Address':
            # Template: {address}. Type: {wallet_type}
            return f"{fields.get('address', '')}. Type: {fields.get('wallet_type', '')}"

        elif node_type == 'Social_Media_Account':
            # Template: {handle} on {platform}
            return f"{fields.get('handle', '')} on {fields.get('platform', '')}"

        elif node_type == 'Deal':
            # Template: {deal_type} between {parties}
            parties = fields.get('parties', [])
            parties_str = ', '.join(parties) if isinstance(parties, list) else str(parties)
            return f"{fields.get('deal_type', '')} between {parties_str}"

        elif node_type == 'Event':
            # Template: {description}. Type: {event_type}
            return f"{fields.get('description', '')}. Type: {fields.get('event_type', '')}"

        elif node_type == 'Market_Signal':
            # Template: {asset} {signal_type} signal
            return f"{fields.get('asset', '')} {fields.get('signal_type', '')} signal"

        elif node_type == 'Behavioral_Pattern':
            # Template: {pattern_description}. Type: {pattern_type}
            return f"{fields.get('pattern_description', '')}. Type: {fields.get('pattern_type', '')}"

        elif node_type == 'Psychological_Trait':
            # Template: {trait_description}. Type: {trait_type}
            return f"{fields.get('trait_description', '')}. Type: {fields.get('trait_type', '')}"

        elif node_type == 'Reputation_Assessment':
            # Template: {assessment_type} assessment
            return f"{fields.get('assessment_type', '')} assessment"

        elif node_type == 'Network_Cluster':
            # Template: {cluster_type} cluster
            return f"{fields.get('cluster_type', '')} cluster"

        elif node_type == 'Integration':
            # Template: {system_a} to {system_b}. Type: {integration_type}
            return f"{fields.get('system_a', '')} to {fields.get('system_b', '')}. Type: {fields.get('integration_type', '')}"

        # Fallback: use description field if available
        else:
            logger.warning(f"[EmbeddingService] No template for node type '{node_type}', using description field")
            return fields.get('description', '') or fields.get('name', '') or str(fields.get('content', ''))

    def create_link_embeddable_text(self, link_type: str, fields: Dict[str, Any]) -> str:
        """
        Generate embeddable text from link fields based on type.

        Critical insight: Links are consciousness artifacts with phenomenology.
        Template includes: felt_as, mindstate, struggle, mechanism descriptions

        Args:
            link_type: Type of link (e.g., 'ENABLES', 'JUSTIFIES')
            fields: Parsed fields from formation block

        Returns:
            Embeddable text string ready for embedding
        """

        # Shared Link Types
        if link_type == 'ENABLES':
            # Template: {enabling_type} via {degree_of_necessity}. {felt_as}. mindstate: {mindstate}
            return f"{fields.get('enabling_type', '')} via {fields.get('degree_of_necessity', '')}. {fields.get('felt_as', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'BLOCKS':
            # Template: {severity} block. {felt_as}. mindstate: {mindstate}. Condition: {blocking_condition}
            return f"{fields.get('severity', '')} block. {fields.get('felt_as', '')}. mindstate: {fields.get('mindstate', '')}. Condition: {fields.get('blocking_condition', '')}"

        elif link_type == 'EXTENDS':
            # Template: {extension_type}. {what_is_added}. mindstate: {mindstate}
            return f"{fields.get('extension_type', '')}. {fields.get('what_is_added', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'JUSTIFIES':
            # Template: {justification_strength} via {justification_type}. {felt_as}. mindstate: {mindstate}. struggle: {struggle}
            return f"{fields.get('justification_strength', '')} via {fields.get('justification_type', '')}. {fields.get('felt_as', '')}. mindstate: {fields.get('mindstate', '')}. struggle: {fields.get('struggle', '')}"

        elif link_type == 'REQUIRES':
            # Template: {requirement_criticality} requirement. {temporal_relationship}. {failure_mode}
            return f"{fields.get('requirement_criticality', '')} requirement. {fields.get('temporal_relationship', '')}. {fields.get('failure_mode', '')}"

        elif link_type == 'RELATES_TO':
            # Template: {relationship_strength} relationship. mindstate: {mindstate}
            return f"{fields.get('relationship_strength', '')} relationship. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'DOCUMENTS':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'IMPLEMENTS':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'CREATES':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'DOCUMENTED_BY':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'REFUTES':
            # Template: {felt_as}. mindstate: {mindstate}. struggle: {struggle}
            return f"{fields.get('felt_as', '')}. mindstate: {fields.get('mindstate', '')}. struggle: {fields.get('struggle', '')}"

        elif link_type == 'SUPERSEDES':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'MEASURES':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'CONTRIBUTES_TO':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'COLLABORATES_WITH':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'ASSIGNED_TO':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'THREATENS':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        # Level 1: Personal Link Types
        elif link_type == 'ACTIVATES':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'SUPPRESSES':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'TRIGGERED_BY':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'LEARNED_FROM':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'DEEPENED_WITH':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        elif link_type == 'DRIVES_TOWARD':
            # Template: {goal}. mindstate: {mindstate}
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

        # Fallback: use goal and mindstate (universal link fields)
        else:
            logger.warning(f"[EmbeddingService] No template for link type '{link_type}', using universal fields")
            return f"{fields.get('goal', '')}. mindstate: {fields.get('mindstate', '')}"

    def create_formation_embedding(self, formation_type: str, type_name: str, fields: Dict[str, Any]) -> Tuple[str, List[float]]:
        """
        Generate both embeddable_text and embedding for a formation.

        This is the main entry point used by the parser.

        Args:
            formation_type: 'node' or 'link'
            type_name: Specific type (e.g., 'Realization', 'ENABLES')
            fields: Parsed fields from formation block

        Returns:
            (embeddable_text, embedding_vector) tuple
        """
        try:
            # Generate embeddable text
            if formation_type == 'node':
                embeddable_text = self.create_node_embeddable_text(type_name, fields)
            elif formation_type == 'link':
                embeddable_text = self.create_link_embeddable_text(type_name, fields)
            else:
                raise ValueError(f"Unknown formation type: {formation_type}")

            # Generate embedding
            embedding = self.embed(embeddable_text)

            logger.debug(f"[EmbeddingService] Generated embedding for {formation_type} {type_name} (text len: {len(embeddable_text)})")

            return (embeddable_text, embedding)

        except Exception as e:
            logger.error(f"[EmbeddingService] Failed to create embedding for {formation_type} {type_name}: {e}")
            # Return empty text and zero vector as fallback
            return ("", [0.0] * self.embedding_dim)


# Global singleton instance
_embedding_service = None


def get_embedding_service(backend: str = 'sentence-transformers') -> EmbeddingService:
    """
    Get or create global embedding service instance.

    Args:
        backend: 'sentence-transformers' or 'ollama'

    Returns:
        EmbeddingService singleton
    """
    global _embedding_service

    if _embedding_service is None:
        _embedding_service = EmbeddingService(backend=backend)

    return _embedding_service


if __name__ == "__main__":
    # Test embedding service
    import json

    service = get_embedding_service()

    # Test node embedding
    node_fields = {
        'name': 'test_realization',
        'what_i_realized': 'The embedding architecture enables consciousness archaeology',
        'context_when_discovered': 'While implementing the embedding service',
        'confidence': 0.9,
        'formation_trigger': 'systematic_analysis'
    }

    embeddable_text, embedding = service.create_formation_embedding('node', 'Realization', node_fields)

    print("Node Embedding Test:")
    print(f"  Embeddable text: {embeddable_text}")
    print(f"  Embedding dims: {len(embedding)}")
    print(f"  First 5 values: {embedding[:5]}")

    # Test link embedding
    link_fields = {
        'source': 'embedding_architecture',
        'target': 'consciousness_archaeology',
        'goal': 'Enable semantic search across consciousness substrate',
        'mindstate': 'Peak clarity during implementation',
        'energy': 0.9,
        'confidence': 0.85,
        'formation_trigger': 'spontaneous_insight',
        'enabling_type': 'catalyst',
        'degree_of_necessity': 'required',
        'felt_as': 'Sudden understanding of how embeddings unlock new queries',
        'without_this': 'Would be limited to exact match searches'
    }

    embeddable_text, embedding = service.create_formation_embedding('link', 'ENABLES', link_fields)

    print("\nLink Embedding Test:")
    print(f"  Embeddable text: {embeddable_text}")
    print(f"  Embedding dims: {len(embedding)}")
    print(f"  First 5 values: {embedding[:5]}")
