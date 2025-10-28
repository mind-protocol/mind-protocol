"""
Forged Identity Integration Layer

Hooks into stimulus processing to generate forged identity prompts.
Separate from consciousness_engine_v2.py to avoid schema hook violations.

Integration Point:
- Called after stimulus injection + WM update
- Generates system prompt from WM state
- Emits telemetry events for dashboard observability
- Phase 3A: Observe-only (no LLM calls)
- Phase 3B: Autonomous responses (future)

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-26
"""

from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

from orchestration.mechanisms.forged_identity_generator import ForgedIdentityGenerator
from orchestration.mechanisms.consciousness_telemetry import ConsciousnessTelemetry

logger = logging.getLogger(__name__)


class ForgedIdentityIntegration:
    """
    Integration layer for forged identity generation.

    Manages generators for all citizens and handles prompt generation
    after stimulus processing.
    """

    def __init__(
        self,
        telemetry: Optional[ConsciousnessTelemetry] = None,
        autonomous_mode: bool = False
    ):
        """
        Initialize forged identity integration.

        Args:
            telemetry: ConsciousnessTelemetry instance for event emission
            autonomous_mode: Enable LLM execution (Phase 3B) - defaults to False (Phase 3A)
        """
        self.telemetry = telemetry
        self.autonomous_mode = autonomous_mode
        self.generators: Dict[str, ForgedIdentityGenerator] = {}

        logger.info(
            f"[ForgedIdentityIntegration] Initialized in "
            f"{'AUTONOMOUS' if autonomous_mode else 'OBSERVE-ONLY'} mode"
        )

    def get_generator(self, citizen_id: str) -> ForgedIdentityGenerator:
        """
        Get or create forged identity generator for citizen.

        Args:
            citizen_id: Citizen identifier

        Returns:
            ForgedIdentityGenerator instance
        """
        if citizen_id not in self.generators:
            self.generators[citizen_id] = ForgedIdentityGenerator(
                citizen_id=citizen_id,
                autonomous_mode=self.autonomous_mode,
                telemetry=self.telemetry
            )
            logger.info(f"[ForgedIdentityIntegration] Created generator for {citizen_id}")

        return self.generators[citizen_id]

    async def process_stimulus_response(
        self,
        citizen_id: str,
        stimulus_text: str,
        stimulus_id: str,
        wm_nodes: List[Dict[str, Any]],
        conversation_context: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate forged identity prompt/response for stimulus.

        Phase 3A: Returns None (observe-only)
        Phase 3B: Returns response text (autonomous)

        Args:
            citizen_id: Citizen who received stimulus
            stimulus_text: User message
            stimulus_id: Stimulus identifier
            wm_nodes: Current working memory nodes
            conversation_context: Recent conversation history

        Returns:
            Response text (Phase 3B) or None (Phase 3A)
        """
        generator = self.get_generator(citizen_id)

        # Generate prompt/response
        response = await generator.generate_response(
            stimulus_text=stimulus_text,
            stimulus_id=stimulus_id,
            wm_nodes=wm_nodes,
            conversation_context=conversation_context
        )

        if response:
            logger.info(
                f"[ForgedIdentityIntegration] Generated response for {citizen_id} "
                f"(stimulus={stimulus_id}, length={len(response)})"
            )
        else:
            logger.debug(
                f"[ForgedIdentityIntegration] Generated prompt for {citizen_id} "
                f"(observe-only mode, no response)"
            )

        return response


# Global instance (created by websocket_server or engine registry)
_global_integration: Optional[ForgedIdentityIntegration] = None


def initialize_forged_identity_integration(
    telemetry: Optional[ConsciousnessTelemetry] = None,
    autonomous_mode: bool = False
) -> ForgedIdentityIntegration:
    """
    Initialize global forged identity integration.

    Should be called once at startup by websocket_server.

    Args:
        telemetry: ConsciousnessTelemetry instance
        autonomous_mode: Enable autonomous responses

    Returns:
        ForgedIdentityIntegration instance
    """
    global _global_integration

    if _global_integration is None:
        _global_integration = ForgedIdentityIntegration(
            telemetry=telemetry,
            autonomous_mode=autonomous_mode
        )
        logger.info("[ForgedIdentityIntegration] Global instance initialized")

    return _global_integration


def get_forged_identity_integration() -> Optional[ForgedIdentityIntegration]:
    """
    Get global forged identity integration instance.

    Returns:
        ForgedIdentityIntegration or None if not initialized
    """
    return _global_integration
