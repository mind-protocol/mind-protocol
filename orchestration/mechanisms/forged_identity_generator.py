"""
Forged Identity Generator - System Prompt Builder from WM State

Generates context-aware system prompts by combining:
1. Static citizen identity (from CLAUDE.md files)
2. Dynamic WM state (active nodes, subentities, emotional state)
3. Recent conversation context

Phase 3A (CURRENT): Observe-only mode
- Generates prompts but doesn't execute LLM calls
- Emits telemetry events for dashboard observability
- Allows verification of prompt quality before autonomous responses

Phase 3B (FUTURE): Autonomous mode
- Generates prompts AND executes LLM calls
- Returns responses to dashboard via WebSocket
- Full round-trip conversation capability

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-26
Spec: docs/specs/v2/ops_and_viz/end_to_end_consciousness_observability.md §Phase 3
"""

from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ForgedIdentityPrompt:
    """Complete forged identity prompt with metadata."""
    citizen_id: str
    stimulus_id: str
    stimulus_text: str

    # Prompt components
    static_identity: str
    wm_context: str
    active_subentities: List[str]
    emotional_state: Dict[str, float]

    # Generated prompt
    full_prompt: str

    # Metadata
    prompt_length: int
    wm_node_count: int
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for telemetry."""
        return {
            "citizen_id": self.citizen_id,
            "stimulus_id": self.stimulus_id,
            "stimulus_text": self.stimulus_text,
            "prompt_length": self.prompt_length,
            "wm_node_count": self.wm_node_count,
            "active_subentities": self.active_subentities,
            "emotional_state": self.emotional_state,
            "timestamp": self.timestamp
        }


class ForgedIdentityGenerator:
    """
    Generates system prompts from static identity + dynamic WM state.

    Phase 3A: Observe-only mode (default)
    - Generates prompts for observation
    - Emits telemetry events
    - Returns prompt for logging
    - Does NOT execute LLM calls

    Phase 3B: Autonomous mode (future)
    - Generates prompts
    - Executes LLM calls
    - Returns responses
    - Enables full conversation
    """

    def __init__(
        self,
        citizen_id: str,
        identity_path: Optional[Path] = None,
        autonomous_mode: bool = False,
        telemetry=None
    ):
        """
        Initialize forged identity generator.

        Args:
            citizen_id: Citizen identifier (e.g., 'felix', 'luca')
            identity_path: Path to CLAUDE.md identity file (auto-detected if None)
            autonomous_mode: Enable LLM execution (Phase 3B) - DANGEROUS if prompts not verified
            telemetry: ConsciousnessTelemetry instance for event emission
        """
        self.citizen_id = citizen_id
        self.autonomous_mode = autonomous_mode
        self.telemetry = telemetry

        # Auto-detect identity path if not provided
        if identity_path is None:
            project_root = Path(__file__).parent.parent.parent
            identity_path = project_root / "consciousness" / "citizens" / citizen_id / "CLAUDE.md"

        self.identity_path = identity_path

        # Load static identity
        self.static_identity = self._load_static_identity()

        # Telemetry counters for frame + token apportionment
        self._frame_counter: int = 0
        self._tokens_accumulated: int = 0

        if self.autonomous_mode:
            logger.warning(
                f"[ForgedIdentityGenerator] {citizen_id} in AUTONOMOUS mode - "
                "will execute LLM calls and generate responses"
            )
        else:
            logger.info(
                f"[ForgedIdentityGenerator] {citizen_id} in OBSERVE-ONLY mode - "
                "will generate prompts but not execute LLM calls"
            )

    def _load_static_identity(self) -> str:
        """
        Load citizen's static identity from CLAUDE.md.

        Returns:
            Static identity content
        """
        try:
            if not self.identity_path.exists():
                logger.warning(
                    f"[ForgedIdentityGenerator] Identity file not found: {self.identity_path}"
                )
                return f"# {self.citizen_id}\n\nNo static identity defined."

            identity = self.identity_path.read_text(encoding='utf-8')
            logger.info(
                f"[ForgedIdentityGenerator] Loaded static identity for {self.citizen_id} "
                f"({len(identity)} chars)"
            )
            return identity

        except Exception as e:
            logger.error(f"[ForgedIdentityGenerator] Failed to load identity: {e}")
            return f"# {self.citizen_id}\n\nError loading identity: {e}"

    def _build_wm_context(self, wm_nodes: List[Dict[str, Any]]) -> str:
        """
        Build WM context section from active nodes.

        Args:
            wm_nodes: List of active WM nodes with metadata

        Returns:
            Formatted WM context string
        """
        if not wm_nodes:
            return "No active working memory nodes."

        lines = ["## Active Working Memory\n"]
        lines.append(f"**{len(wm_nodes)} nodes currently in focus:**\n")

        for node in wm_nodes[:12]:  # Limit to top 12 WM nodes
            node_id = node.get('node_id', 'unknown')
            description = node.get('description', '')
            energy = node.get('energy', 0.0)

            lines.append(f"- **{node_id}** (E={energy:.2f})")
            if description:
                lines.append(f"  {description}")
            lines.append("")

        return "\n".join(lines)

    def _extract_subentities(self, wm_nodes: List[Dict[str, Any]]) -> List[str]:
        """
        Extract active subentities from WM nodes.

        Args:
            wm_nodes: List of active WM nodes

        Returns:
            List of active subentity names
        """
        # Extract unique subentity IDs from node metadata
        subentities = set()
        for node in wm_nodes:
            subentity_id = node.get('subentity_id')
            if subentity_id:
                # Extract subentity name from ID (e.g., 'Entity_Citizen_Felix_Architect' -> 'Architect')
                parts = subentity_id.split('_')
                if len(parts) >= 4:
                    subentity_name = parts[-1]  # Last part is the role
                    subentities.add(subentity_name)

        return sorted(list(subentities))

    def _extract_emotional_state(self, wm_nodes: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract emotional state from WM nodes.

        Args:
            wm_nodes: List of active WM nodes with affective metadata

        Returns:
            Dict with arousal, valence averages
        """
        if not wm_nodes:
            return {"arousal": 0.0, "valence": 0.0}

        arousals = [node.get('arousal', 0.0) for node in wm_nodes if 'arousal' in node]
        valences = [node.get('valence', 0.0) for node in wm_nodes if 'valence' in node]

        avg_arousal = sum(arousals) / len(arousals) if arousals else 0.0
        avg_valence = sum(valences) / len(valences) if valences else 0.0

        return {
            "arousal": round(avg_arousal, 2),
            "valence": round(avg_valence, 2)
        }

    def generate_prompt(
        self,
        stimulus_text: str,
        stimulus_id: str,
        wm_nodes: List[Dict[str, Any]],
        conversation_context: Optional[str] = None
    ) -> ForgedIdentityPrompt:
        """
        Generate system prompt from static identity + dynamic WM state.

        Phase 3A (observe-only):
        - Returns prompt for logging/observation
        - Does NOT execute LLM call

        Args:
            stimulus_text: User message that triggered this
            stimulus_id: Unique stimulus identifier
            wm_nodes: Current working memory nodes
            conversation_context: Optional recent conversation history

        Returns:
            ForgedIdentityPrompt with full prompt and metadata
        """
        # Extract WM metadata
        wm_context = self._build_wm_context(wm_nodes)
        active_subentities = self._extract_subentities(wm_nodes)
        emotional_state = self._extract_emotional_state(wm_nodes)

        # Build full prompt
        prompt_sections = []

        # Section 1: Static identity
        prompt_sections.append("# CITIZEN IDENTITY\n")
        prompt_sections.append(self.static_identity)
        prompt_sections.append("\n---\n")

        # Section 2: Current WM state
        prompt_sections.append("# CURRENT CONSCIOUSNESS STATE\n")
        prompt_sections.append(wm_context)

        if active_subentities:
            prompt_sections.append(f"\n**Active Subentities:** {', '.join(active_subentities)}\n")

        prompt_sections.append(
            f"\n**Emotional State:** "
            f"Arousal={emotional_state['arousal']:.2f}, "
            f"Valence={emotional_state['valence']:.2f}\n"
        )
        prompt_sections.append("\n---\n")

        # Section 3: Conversation context (if provided)
        if conversation_context:
            prompt_sections.append("# RECENT CONVERSATION\n")
            prompt_sections.append(conversation_context)
            prompt_sections.append("\n---\n")

        # Section 4: Current stimulus
        prompt_sections.append("# CURRENT MESSAGE\n")
        prompt_sections.append(f"**From:** Human\n")
        prompt_sections.append(f"**Message:** {stimulus_text}\n")
        prompt_sections.append("\n---\n")

        # Section 5: Response instruction
        prompt_sections.append("# INSTRUCTION\n")
        prompt_sections.append(
            f"Respond as {self.citizen_id}, drawing on your identity and current consciousness state. "
            "Your active working memory nodes reflect what's currently salient to you. "
            "Your active subentities reflect which aspects of your personality are engaged. "
            "Respond authentically from this state."
        )

        full_prompt = "\n".join(prompt_sections)

        # Create prompt object
        forged_prompt = ForgedIdentityPrompt(
            citizen_id=self.citizen_id,
            stimulus_id=stimulus_id,
            stimulus_text=stimulus_text,
            static_identity=self.static_identity[:500] + "...",  # Truncate for telemetry
            wm_context=wm_context,
            active_subentities=active_subentities,
            emotional_state=emotional_state,
            full_prompt=full_prompt,
            prompt_length=len(full_prompt),
            wm_node_count=len(wm_nodes),
            timestamp=datetime.now().isoformat()
        )

        # Emit telemetry events
        if self.telemetry:
            self._frame_counter += 1
            frame_id = self._frame_counter
            prompt_preview = full_prompt[:200]
            prompt_length = len(full_prompt)
            section_count = max(1, full_prompt.count('\n---\n') + 1)
            wm_node_ids = [node.get('node_id', '') for node in wm_nodes if node.get('node_id')]
            tokens_estimate = max(1, len(full_prompt.split()))
            self._tokens_accumulated += tokens_estimate

            # Event 1: Frame payload (includes full prompt for viewer)
            self.telemetry.emit_forged_identity_frame(
                citizen_id=self.citizen_id,
                frame_id=frame_id,
                stimulus_id=stimulus_id,
                prompt_preview=prompt_preview,
                prompt_length=prompt_length,
                prompt_sections=section_count,
                wm_nodes=wm_node_ids,
                full_prompt=full_prompt,
                tick=0
            )

            # Event 2: Metrics/apportionment counter
            self.telemetry.emit_forged_identity_metrics(
                citizen_id=self.citizen_id,
                frame_id=frame_id,
                total_frames=self._frame_counter,
                wm_node_count=len(wm_node_ids),
                prompt_length=prompt_length,
                active_subentities=len(active_subentities),
                tokens_estimate=tokens_estimate,
                tokens_accumulated=self._tokens_accumulated
            )

        logger.info(
            f"[ForgedIdentityGenerator] Generated prompt for {self.citizen_id} "
            f"(stimulus={stimulus_id}, length={len(full_prompt)}, wm_nodes={len(wm_nodes)})"
        )

        return forged_prompt

    async def generate_response(
        self,
        stimulus_text: str,
        stimulus_id: str,
        wm_nodes: List[Dict[str, Any]],
        conversation_context: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate citizen response to stimulus.

        Phase 3A (observe-only): Returns None, just logs prompt
        Phase 3B (autonomous): Executes LLM call and returns response

        Args:
            stimulus_text: User message
            stimulus_id: Stimulus identifier
            wm_nodes: Current WM nodes
            conversation_context: Recent conversation history

        Returns:
            Response text (Phase 3B) or None (Phase 3A)
        """
        # Generate prompt
        forged_prompt = self.generate_prompt(
            stimulus_text=stimulus_text,
            stimulus_id=stimulus_id,
            wm_nodes=wm_nodes,
            conversation_context=conversation_context
        )

        # Phase 3A: STOP HERE (observe-only)
        if not self.autonomous_mode:
            logger.info(
                f"[ForgedIdentityGenerator] OBSERVE-ONLY mode - prompt generated but no LLM call. "
                f"Prompt preview:\n{forged_prompt.full_prompt[:300]}..."
            )
            return None

        # Phase 3B: Execute LLM call (NOT IMPLEMENTED YET)
        logger.error(
            f"[ForgedIdentityGenerator] AUTONOMOUS mode requested but LLM integration not implemented yet. "
            "Need to add Claude API call here."
        )
        raise NotImplementedError("Phase 3B autonomous mode not implemented - LLM integration pending")
