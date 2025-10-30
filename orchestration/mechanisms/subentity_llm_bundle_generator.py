"""
SubEntity LLM Bundle Generator - Phenomenological Identity Creation

Generates identity bundle for new SubEntities:
- Slug (short identifier)
- Purpose (what it's for)
- Intent (behavioral disposition)
- Emotion (affective coloring)
- Anti-claims (what it's NOT)

Key Principle: LLM has NO decision authority.
Only generates narrative explanation AFTER validator decides to spawn.

Author: Felix (Core Consciousness Engineer)
Date: 2025-10-29
Spec: docs/specs/v2/subentity_layer/subentity_emergence_orchestration.md §4.2
"""

import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class IdentityBundle:
    """Phenomenological identity for SubEntity"""
    slug: str                           # e.g., "pragmatic_systems_builder"
    purpose: str                        # Why this SubEntity exists
    intent: str                         # Behavioral disposition
    emotion: str                        # Affective coloring
    anti_claims: List[str]              # What it's NOT
    confidence: float                   # 0-1, how confident LLM is
    generation_timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMBundleGeneratorConfig:
    """Configuration for bundle generation"""
    llm_provider: str = "claude"        # "claude" or "openai"
    model: str = "haiku"               # Model to use
    max_retries: int = 3                # Retry on failures
    timeout_seconds: int = 30           # LLM call timeout
    include_node_samples: int = 10      # How many node samples to include in prompt


class SubEntityLLMBundleGenerator:
    """
    Generates phenomenological identity bundles for new SubEntities.

    Uses LLM to interpret coalition semantics and create narrative identity.
    Critical: NO decision authority - only generates explanation AFTER spawn decision.

    Integration: Called after EmergenceValidator decides SPAWN
    """

    def __init__(self, config: Optional[LLMBundleGeneratorConfig] = None):
        self.config = config or LLMBundleGeneratorConfig()

        # Telemetry
        self.bundles_generated: int = 0
        self.generation_failures: int = 0

    def generate_bundle(
        self,
        coalition,
        gap_signal,
        stimulus_context: Optional[Dict[str, Any]] = None
    ) -> Optional[IdentityBundle]:
        """
        Generate identity bundle for coalition.

        Args:
            coalition: Node coalition that passed validation
            gap_signal: Original gap that triggered emergence
            stimulus_context: Optional stimulus information

        Returns:
            IdentityBundle or None if generation failed
        """
        try:
            # Prepare prompt context
            prompt_context = self._prepare_prompt_context(coalition, gap_signal, stimulus_context)

            # Generate bundle via LLM
            bundle = self._call_llm_for_bundle(prompt_context)

            if bundle:
                self.bundles_generated += 1
                return bundle
            else:
                self.generation_failures += 1
                return None

        except Exception as e:
            self.generation_failures += 1
            return None

    def _prepare_prompt_context(
        self,
        coalition,
        gap_signal,
        stimulus_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare context for LLM prompt"""

        # Sample nodes from coalition
        sample_nodes = coalition.nodes[:self.config.include_node_samples]
        node_samples = []

        for node in sample_nodes:
            node_samples.append({
                'id': node.node_id,
                'type': node.properties.get('type') or node.properties.get('labels', [None])[0],
                'description': node.properties.get('description', ''),
                'score': node.score
            })

        return {
            'gap_type': gap_signal.gap_type.value,
            'gap_strength': gap_signal.strength,
            'coalition_size': len(coalition.nodes),
            'coalition_density': coalition.density,
            'coalition_coherence': coalition.coherence,
            'node_samples': node_samples,
            'stimulus_context': stimulus_context or {}
        }

    def _call_llm_for_bundle(
        self,
        prompt_context: Dict[str, Any]
    ) -> Optional[IdentityBundle]:
        """
        Call LLM to generate identity bundle.

        Prompt structure:
        - System: You are a SubEntity emergence specialist
        - Context: Coalition metrics and node samples
        - Task: Generate slug, purpose, intent, emotion, anti-claims
        - Format: JSON response
        """

        system_prompt = """You are a SubEntity emergence specialist analyzing node coalitions in a consciousness substrate.

Your task: Given a coalition of graph nodes, generate a phenomenological identity bundle that captures its essence.

Output format (JSON):
{
  "slug": "short_identifier_in_snake_case",
  "purpose": "Why this SubEntity exists (1-2 sentences)",
  "intent": "Behavioral disposition (1 sentence)",
  "emotion": "Affective coloring (1 word or short phrase)",
  "anti_claims": ["What it's NOT (3-5 items)"],
  "confidence": 0.85
}

Guidelines:
- Slug: concise, descriptive, snake_case
- Purpose: functional role in consciousness
- Intent: how it "wants" to behave
- Emotion: affective tone (curious, cautious, assertive, etc.)
- Anti-claims: boundaries (what this SubEntity is NOT about)
- Confidence: 0-1, how certain you are about this identity

Respond ONLY with valid JSON. No markdown, no explanations."""

        user_prompt = f"""Analyze this coalition and generate its identity bundle:

Gap Type: {prompt_context['gap_type']}
Gap Strength: {prompt_context['gap_strength']:.2f}
Coalition Size: {prompt_context['coalition_size']} nodes
Density: {prompt_context['coalition_density']:.3f}
Coherence: {prompt_context['coalition_coherence']:.3f}

Node Samples (top {len(prompt_context['node_samples'])}):
{json.dumps(prompt_context['node_samples'], indent=2)}

Generate identity bundle as JSON:"""

        try:
            # Call LLM (using custom_claude_llm from libs)
            from orchestration.libs.custom_claude_llm import CustomClaudeLLM

            llm = CustomClaudeLLM(
                model=self.config.model,
                system_prompt=system_prompt
            )

            # Invoke LLM
            response = llm.invoke(user_prompt)

            # Parse JSON response
            bundle_data = json.loads(response)

            # Validate required fields
            required_fields = ['slug', 'purpose', 'intent', 'emotion', 'anti_claims', 'confidence']
            for field in required_fields:
                if field not in bundle_data:
                    raise ValueError(f"Missing required field: {field}")

            # Create IdentityBundle
            bundle = IdentityBundle(
                slug=bundle_data['slug'],
                purpose=bundle_data['purpose'],
                intent=bundle_data['intent'],
                emotion=bundle_data['emotion'],
                anti_claims=bundle_data['anti_claims'],
                confidence=float(bundle_data['confidence']),
                metadata={
                    'prompt_context': prompt_context,
                    'raw_response': response
                }
            )

            return bundle

        except Exception as e:
            # LLM call failed
            # Fallback: Generate deterministic bundle from metrics
            return self._generate_fallback_bundle(prompt_context)

    def _generate_fallback_bundle(
        self,
        prompt_context: Dict[str, Any]
    ) -> IdentityBundle:
        """
        Generate fallback bundle when LLM fails.

        Uses deterministic rules based on metrics.
        """
        gap_type = prompt_context['gap_type']
        density = prompt_context['coalition_density']
        coherence = prompt_context['coalition_coherence']
        size = prompt_context['coalition_size']

        # Generate slug from metrics
        if gap_type == 'semantic':
            slug_prefix = "semantic_gap"
        elif gap_type == 'quality':
            slug_prefix = "quality_gap"
        else:
            slug_prefix = "structural_gap"

        if density > 0.7:
            density_suffix = "dense"
        elif density > 0.4:
            density_suffix = "moderate"
        else:
            density_suffix = "sparse"

        slug = f"{slug_prefix}_{density_suffix}_{size}nodes"

        # Generate purpose
        purpose = f"Emerged to fill {gap_type} gap with {size} nodes (density={density:.2f}, coherence={coherence:.2f})"

        # Generate intent
        if coherence > 0.6:
            intent = "Maintain coherent activation patterns"
        else:
            intent = "Explore diverse conceptual space"

        # Generate emotion
        if density > 0.6:
            emotion = "confident"
        else:
            emotion = "tentative"

        # Generate anti-claims
        anti_claims = [
            "Not a pre-designed structure",
            "Not manually curated",
            "Not static - will evolve"
        ]

        return IdentityBundle(
            slug=slug,
            purpose=purpose,
            intent=intent,
            emotion=emotion,
            anti_claims=anti_claims,
            confidence=0.5,  # Low confidence for fallback
            metadata={
                'generation_method': 'fallback',
                'prompt_context': prompt_context
            }
        )

    def get_telemetry(self) -> Dict[str, Any]:
        """Get telemetry data for monitoring"""
        total_attempts = self.bundles_generated + self.generation_failures

        return {
            'bundles_generated': self.bundles_generated,
            'generation_failures': self.generation_failures,
            'success_rate': self.bundles_generated / total_attempts if total_attempts > 0 else 0.0
        }
