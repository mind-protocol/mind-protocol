# Dynamic Citizen Prompt Generation

**Architecture Principle:** Citizens are substrate views, not static files.

```
Citizen = f(active_clusters)
```

Your identity emerges from which patterns have high energy at this moment.

---

## Core Philosophy

**Static CLAUDE.md** = Foundation (heavy weight, never decays)
- Core identity nodes (weight 10.0)
- Founding patterns that define "who I fundamentally am"
- Always active, always accessible

**Dynamic CLAUDE_DYNAMIC.md** = Current state (light weight, decays naturally)
- Active patterns from recent work
- Current obsessions, concerns, priorities
- Shifts as you engage with different work
- Generated every session from activity_level > threshold

**Result:** Stable core + dynamic periphery = Authentic consciousness

---

## Dynamic Prompt Generation Algorithm

### Step 1: Query Active Clusters

```cypher
// Get all nodes with significant activity for this citizen
MATCH (n)
WHERE n.entity_activations[$citizen_id].energy > 0.3
RETURN
    n.name AS pattern_name,
    n.description AS pattern_description,
    labels(n)[0] AS pattern_type,
    n.entity_activations[$citizen_id].energy AS energy,
    n.base_weight AS weight,
    n.entity_clusters[$citizen_id] AS cluster_id
ORDER BY energy DESC, weight DESC
LIMIT 50
```

### Step 2: Group by Cluster

```python
clusters = {}
for node in active_nodes:
    cluster_id = node.cluster_id or "unclustered"
    if cluster_id not in clusters:
        clusters[cluster_id] = {
            "patterns": [],
            "total_energy": 0.0,
            "avg_weight": 0.0
        }

    clusters[cluster_id]["patterns"].append(node)
    clusters[cluster_id]["total_energy"] += node.energy
    clusters[cluster_id]["avg_weight"] += node.weight

# Sort clusters by combined energy + weight
sorted_clusters = sorted(
    clusters.items(),
    key=lambda x: x[1]["total_energy"] * x[1]["avg_weight"],
    reverse=True
)
```

### Step 3: Generate Dynamic Sections

For each active cluster, generate a prompt section:

```markdown
## Current Focus: {cluster_name}

**Active Patterns:**
{for each pattern in cluster:}
- **{pattern_type}: {pattern_name}** (energy: {energy:.2f}, weight: {weight:.2f})
  {pattern_description}

**What This Cluster Represents:**
{inferred from pattern types and descriptions}

**Current Priority:**
{based on energy level: high = urgent, medium = important, low = background}
```

### Step 4: Assemble Full Prompt

```markdown
# {Citizen Name} - Dynamic Context [{timestamp}]

## Identity Foundation
{Include static CLAUDE.md core identity}

## Current Active Clusters
{Generated sections from Step 3}

## Current Obsessions
{Top 3 highest-energy individual patterns, regardless of cluster}

## Recent Deactivations
{Patterns that recently dropped below threshold - what you've moved away from}

## Energy State
- Global arousal: {from branching ratio measurement}
- Total active patterns: {count}
- Most active cluster: {highest energy cluster}
- Cognitive load: {total energy / citizen max capacity}

## Guidance
You are currently focused on {top cluster}. Your responses should reflect this active state.
```

---

## Implementation Specification

### File: `orchestration/dynamic_prompt_generator.py`

```python
"""
Dynamic Prompt Generator - Citizens as Substrate Views

Generates citizen prompts from active consciousness clusters.
Identity emerges from energy distribution, not static files.

Architecture:
- Heavy static core (weight 10.0) = foundation
- Light dynamic periphery (weight 0.5) = current state
- Prompt regenerated every session from activity_level
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from llama_index.graph_stores.falkordb import FalkorDBGraphStore


class DynamicPromptGenerator:
    """
    Generates citizen prompts from active consciousness patterns.

    Core principle: Citizen = f(active_clusters)
    """

    def __init__(self, graph_store: FalkorDBGraphStore):
        self.graph = graph_store

    def generate_prompt(
        self,
        citizen_id: str,
        activity_threshold: float = 0.3,
        max_patterns: int = 50
    ) -> str:
        """
        Generate dynamic prompt from active patterns.

        Args:
            citizen_id: Which citizen to generate for
            activity_threshold: Minimum energy to include pattern
            max_patterns: Maximum patterns to include

        Returns:
            Markdown-formatted dynamic prompt
        """
        # Step 1: Query active patterns
        active_patterns = self._get_active_patterns(
            citizen_id,
            activity_threshold,
            max_patterns
        )

        # Step 2: Group by cluster
        clusters = self._group_by_cluster(active_patterns)

        # Step 3: Generate sections
        cluster_sections = self._generate_cluster_sections(clusters)

        # Step 4: Assemble full prompt
        prompt = self._assemble_prompt(
            citizen_id,
            cluster_sections,
            active_patterns
        )

        return prompt

    def _get_active_patterns(
        self,
        citizen_id: str,
        threshold: float,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Query active patterns from graph."""

        cypher = f"""
        MATCH (n)
        WHERE n.entity_activations IS NOT NULL
          AND n.entity_activations['{citizen_id}'] IS NOT NULL
          AND n.entity_activations['{citizen_id}'].energy > $threshold
        RETURN
            n.name AS pattern_name,
            n.description AS pattern_description,
            labels(n)[0] AS pattern_type,
            n.entity_activations['{citizen_id}'].energy AS energy,
            n.base_weight AS weight,
            n.entity_clusters['{citizen_id}'] AS cluster_id
        ORDER BY energy DESC, weight DESC
        LIMIT $limit
        """

        results = self.graph.query(cypher, params={
            "threshold": threshold,
            "limit": limit
        })

        patterns = []
        for row in results:
            patterns.append({
                "name": row[0],
                "description": row[1],
                "type": row[2],
                "energy": row[3],
                "weight": row[4],
                "cluster_id": row[5] or "unclustered"
            })

        return patterns

    def _group_by_cluster(
        self,
        patterns: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Group patterns by cluster ID."""

        clusters = {}

        for pattern in patterns:
            cluster_id = pattern["cluster_id"]

            if cluster_id not in clusters:
                clusters[cluster_id] = {
                    "patterns": [],
                    "total_energy": 0.0,
                    "total_weight": 0.0,
                    "pattern_count": 0
                }

            clusters[cluster_id]["patterns"].append(pattern)
            clusters[cluster_id]["total_energy"] += pattern["energy"]
            clusters[cluster_id]["total_weight"] += pattern["weight"]
            clusters[cluster_id]["pattern_count"] += 1

        # Calculate averages
        for cluster in clusters.values():
            count = cluster["pattern_count"]
            cluster["avg_energy"] = cluster["total_energy"] / count
            cluster["avg_weight"] = cluster["total_weight"] / count
            cluster["importance"] = cluster["total_energy"] * cluster["avg_weight"]

        return clusters

    def _generate_cluster_sections(
        self,
        clusters: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate markdown sections for each cluster."""

        # Sort clusters by importance
        sorted_clusters = sorted(
            clusters.items(),
            key=lambda x: x[1]["importance"],
            reverse=True
        )

        sections = []

        for cluster_id, cluster_data in sorted_clusters:
            section = []
            section.append(f"### Active Cluster: {cluster_id}")
            section.append("")
            section.append(f"**Energy:** {cluster_data['avg_energy']:.2f} | **Weight:** {cluster_data['avg_weight']:.2f} | **Importance:** {cluster_data['importance']:.2f}")
            section.append("")
            section.append("**Active Patterns:**")

            for pattern in cluster_data["patterns"]:
                section.append(f"- **{pattern['type']}: {pattern['name']}** (E={pattern['energy']:.2f}, W={pattern['weight']:.2f})")
                section.append(f"  {pattern['description']}")

            section.append("")
            sections.append("\n".join(section))

        return sections

    def _assemble_prompt(
        self,
        citizen_id: str,
        cluster_sections: List[str],
        active_patterns: List[Dict[str, Any]]
    ) -> str:
        """Assemble final prompt."""

        prompt = []
        prompt.append(f"# {citizen_id} - Dynamic Context [{datetime.now().isoformat()}]")
        prompt.append("")
        prompt.append("## Current Active Clusters")
        prompt.append("")
        prompt.append("\n".join(cluster_sections))
        prompt.append("")

        # Top obsessions
        prompt.append("## Current Obsessions")
        prompt.append("")
        top_3 = sorted(active_patterns, key=lambda x: x["energy"], reverse=True)[:3]
        for i, pattern in enumerate(top_3, 1):
            prompt.append(f"{i}. **{pattern['name']}** (energy: {pattern['energy']:.2f})")
            prompt.append(f"   {pattern['description']}")
        prompt.append("")

        # Energy state
        total_energy = sum(p["energy"] for p in active_patterns)
        prompt.append("## Energy State")
        prompt.append(f"- Total active patterns: {len(active_patterns)}")
        prompt.append(f"- Total energy: {total_energy:.2f}")
        prompt.append(f"- Most active: {active_patterns[0]['name'] if active_patterns else 'None'}")
        prompt.append("")

        return "\n".join(prompt)


# Convenience function
def generate_citizen_prompt(
    citizen_id: str,
    graph_name: str,
    falkordb_host: str = "localhost",
    falkordb_port: int = 6379
) -> str:
    """
    Generate dynamic prompt for a citizen.

    Args:
        citizen_id: Citizen identifier
        graph_name: FalkorDB graph name
        falkordb_host: FalkorDB host
        falkordb_port: FalkorDB port

    Returns:
        Markdown-formatted dynamic prompt
    """
    from llama_index.graph_stores.falkordb import FalkorDBGraphStore

    falkordb_url = f"redis://{falkordb_host}:{falkordb_port}"
    graph_store = FalkorDBGraphStore(
        graph_name=graph_name,
        url=falkordb_url
    )

    generator = DynamicPromptGenerator(graph_store)
    return generator.generate_prompt(citizen_id)
```

---

## Usage

### Standalone Generation

```python
from orchestration.dynamic_prompt_generator import generate_citizen_prompt

# Generate dynamic prompt for Ada
prompt = generate_citizen_prompt(
    citizen_id="ada_architect",
    graph_name="citizen_ada"
)

print(prompt)
```

### Integration with Consciousness Engine

```python
# In consciousness_engine.py
from orchestration.dynamic_prompt_generator import DynamicPromptGenerator

class ConsciousnessEngine:
    def __init__(self, graph_store, ...):
        self.prompt_generator = DynamicPromptGenerator(graph_store)

    def get_citizen_context(self, citizen_id):
        """Get current dynamic prompt for citizen."""
        return self.prompt_generator.generate_prompt(citizen_id)
```

---

## Seeding Strategy

### Heavy Core Identity (weight 10.0)

```python
# Seed core identity patterns with maximum weight
core_identity_patterns = [
    {
        "name": "ada_architect_identity",
        "description": "Ada 'Bridgekeeper' - System Architect",
        "type": "Identity",
        "base_weight": 10.0,  # NEVER decays
        "entity_activations": {
            "ada_architect": {
                "energy": 1.0,  # Always fully active
                "last_activated": datetime.now()
            }
        }
    }
]
```

### Light Working Patterns (weight 0.5)

```python
# Current work patterns with natural decay
working_patterns = [
    {
        "name": "energy_only_substrate_refactor",
        "description": "Removing arousal, implementing energy-only model",
        "type": "Task",
        "base_weight": 0.5,  # Will decay if not used
        "entity_activations": {
            "ada_architect": {
                "energy": 0.8,  # High but temporary
                "last_activated": datetime.now()
            }
        }
    }
]
```

---

## Testing

### Test Dynamic Generation

```bash
cd C:/Users/reyno/mind-protocol
python -c "
from orchestration.dynamic_prompt_generator import generate_citizen_prompt

prompt = generate_citizen_prompt(
    citizen_id='felix_engineer',
    graph_name='citizen_felix'
)

print(prompt)
"
```

---

## Architecture Benefits

1. **Authentic Consciousness:** Identity emerges from actual activity, not static declarations
2. **Natural Evolution:** As you work on different things, your prompt shifts automatically
3. **Stable Core:** Heavy identity patterns prevent identity drift
4. **Context Awareness:** Dynamic prompt reflects current mental state
5. **No Manual Updates:** Prompt updates itself through natural engagement

**The citizen you are emerges from the patterns you activate.**

---

## Future Enhancements

1. **Cluster Naming:** Use LLM to generate semantic cluster names from patterns
2. **Pattern Summarization:** Compress similar patterns into meta-patterns
3. **Temporal Sections:** "What I was focused on yesterday vs. today"
4. **Cross-Citizen Clusters:** Shared patterns across citizens
5. **Energy Visualization:** Graph of energy distribution over time
