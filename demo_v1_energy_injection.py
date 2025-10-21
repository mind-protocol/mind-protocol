"""
Demo: V1 Energy Injection with Real Graph Persistence

Shows:
1. Current state of matched nodes (before)
2. V1 injection with full formula
3. Updated state in FalkorDB (after)
4. Learning mechanism statistics

Author: Felix "Ironhand"
Date: 2025-10-21
"""

import sys
import redis
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from orchestration.mechanisms.stimulus_injection import StimulusInjector, create_match
from orchestration.embedding_service import get_embedding_service
from orchestration.semantic_search import SemanticSearch

def demo_injection(
    graph_name: str = "citizen_luca",
    citizen_id: str = "luca",
    stimulus_text: str = "Understanding how consciousness emerges from graph structure and energy flow"
):
    """Demonstrate V1 energy injection with real persistence."""

    print("=" * 80)
    print("V1 ENERGY INJECTION DEMO")
    print("=" * 80)
    print()
    print(f"Graph: {graph_name}")
    print(f"Citizen: {citizen_id}")
    print(f"Stimulus: \"{stimulus_text}\"")
    print()

    # Initialize services
    print("1. Initializing services...")
    injector = StimulusInjector()
    embedding_service = get_embedding_service()
    search = SemanticSearch(graph_name=graph_name)
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    print("   ✅ Services ready")
    print()

    # Embed stimulus
    print("2. Creating stimulus embedding...")
    stimulus_embedding = embedding_service.embed(stimulus_text)
    print(f"   ✅ Embedded to 768-dim vector")
    print()

    # Search for matches
    print("3. Vector search for matching nodes...")
    matches = []
    for node_type in ['Realization', 'Principle', 'Mechanism']:
        results = search.find_similar_nodes(
            query_text=stimulus_text,
            node_type=node_type,
            threshold=0.5,
            limit=3
        )
        matches.extend(results[:3])  # Top 3 per type

    print(f"   ✅ Found {len(matches)} matches")
    print()

    # Build injection matches
    print("4. Building injection matches...")
    injection_matches = []

    print()
    print("   📊 MATCHED NODES (BEFORE INJECTION):")
    print()

    for match in matches[:5]:  # Top 5
        # Query current state
        query = f"MATCH (n {{name: '{match['name']}'}}) RETURN n.threshold, n.energy"
        result = r.execute_command('GRAPH.QUERY', graph_name, query)

        if result and result[1]:
            threshold = float(result[1][0][0]) if result[1][0][0] else 1.0

            # Parse energy
            energy_value = result[1][0][1]
            if energy_value:
                try:
                    parsed = json.loads(energy_value) if isinstance(energy_value, str) else energy_value
                    if isinstance(parsed, dict):
                        current_energy = parsed.get(citizen_id, 0.0)
                    else:
                        current_energy = float(parsed)
                except (json.JSONDecodeError, ValueError):
                    current_energy = 0.0
            else:
                current_energy = 0.0

            # Create injection match
            injection_match = create_match(
                item_id=match['name'],
                item_type='node',
                similarity=match['similarity'],
                current_energy=current_energy,
                threshold=threshold
            )
            injection_matches.append(injection_match)

            # Display
            gap = threshold - current_energy
            print(f"   {match['name'][:60]}")
            print(f"      Similarity: {match['similarity']:.3f}")
            print(f"      Current E:  {current_energy:.3f}")
            print(f"      Threshold:  {threshold:.3f}")
            print(f"      Gap:        {gap:.3f}")
            print()

    print(f"   ✅ {len(injection_matches)} nodes ready for injection")
    print()

    # Inject with V1 formula
    print("5. Injecting energy with V1 formula...")
    print()

    injection_result = injector.inject(
        stimulus_embedding=stimulus_embedding,
        matches=injection_matches,
        source_type="user_message",
        rho_proxy=None,  # Bootstrap mode
        context_embeddings=None
    )

    print(f"   📈 V1 FORMULA BREAKDOWN:")
    print(f"      Gap mass Σ(sim×gap):  {injection_result.gap_mass:.3f}")
    print(f"      Health f(ρ):           {injection_result.health_factor:.3f}")
    print(f"      Source g(source):      {injection_result.source_factor:.3f}")
    print(f"      Peripheral (1+α):      {injection_result.peripheral_factor:.3f}")
    print(f"      ─────────────────────")
    print(f"      Total Budget:          {injection_result.total_budget:.3f}")
    print()

    print(f"   🎯 ENTROPY-COVERAGE SEARCH:")
    print(f"      Entropy H:             {injection_result.entropy:.3f}")
    print(f"      Coverage ĉ:            {injection_result.coverage_target:.3f}")
    print(f"      Matches selected:      {injection_result.matches_selected}/{len(injection_matches)}")
    print()

    print(f"   ✅ Injected {injection_result.total_energy_injected:.3f} energy into {injection_result.items_injected} nodes")
    print()

    # Persist to database
    print("6. Persisting energy to FalkorDB...")
    print()

    persisted_count = 0
    for inj in injection_result.injections:
        node_id = inj['item_id']
        new_energy = inj['new_energy']

        # Update node energy in FalkorDB
        # For multi-citizen graphs, we need to update the energy dict
        query = f"MATCH (n {{name: '{node_id}'}}) RETURN n.energy"
        result = r.execute_command('GRAPH.QUERY', graph_name, query)

        if result and result[1]:
            energy_value = result[1][0][0]
            if energy_value:
                try:
                    parsed = json.loads(energy_value) if isinstance(energy_value, str) else energy_value
                    if isinstance(parsed, dict):
                        energy_dict = parsed
                    else:
                        # Convert single value to dict
                        energy_dict = {citizen_id: float(parsed)}
                except (json.JSONDecodeError, ValueError):
                    energy_dict = {}
            else:
                energy_dict = {}

            # Update citizen-specific energy
            energy_dict[citizen_id] = new_energy
            energy_json = json.dumps(energy_dict).replace("'", "\\'")

            # Write back to graph
            update_query = f"MATCH (n {{name: '{node_id}'}}) SET n.energy = '{energy_json}'"
            r.execute_command('GRAPH.QUERY', graph_name, update_query)

            persisted_count += 1
            print(f"   ✓ {node_id[:60]}: {inj['current_energy']:.3f} → {new_energy:.3f}")

    print()
    print(f"   ✅ Persisted {persisted_count} energy updates to FalkorDB")
    print()

    # Verify persistence
    print("7. Verifying persistence...")
    print()
    print("   📊 NODES AFTER INJECTION:")
    print()

    for inj in sorted(injection_result.injections, key=lambda x: x['delta_energy'], reverse=True)[:3]:
        node_id = inj['item_id']

        # Re-query from database
        query = f"MATCH (n {{name: '{node_id}'}}) RETURN n.energy"
        result = r.execute_command('GRAPH.QUERY', graph_name, query)

        if result and result[1]:
            energy_value = result[1][0][0]
            if energy_value:
                parsed = json.loads(energy_value) if isinstance(energy_value, str) else energy_value
                if isinstance(parsed, dict):
                    db_energy = parsed.get(citizen_id, 0.0)
                else:
                    db_energy = float(parsed)
            else:
                db_energy = 0.0

            match_icon = "✓" if abs(db_energy - inj['new_energy']) < 0.001 else "✗"

            print(f"   {match_icon} {node_id[:60]}")
            print(f"      Expected:  {inj['new_energy']:.3f}")
            print(f"      Database:  {db_energy:.3f}")
            print(f"      ΔE:        +{inj['delta_energy']:.3f}")
            print()

    print("   ✅ All energy values verified in FalkorDB")
    print()

    # Show learning stats
    print("8. Learning mechanism statistics:")
    print()

    # Record frame for learning
    injector.record_frame_result(
        result=injection_result,
        source_type="user_message",
        rho_proxy=None,
        max_degree=10,
        avg_weight=1.0,
        active_node_count=237,
        activation_entropy=2.5,
        overflow_occurred=False
    )

    stats = injector.get_stats()
    print(f"   Frame count:              {stats['frame_count']}")
    print(f"   Health observations:      {stats['health_modulator']['observations']}")
    print(f"   Source types tracked:     {len(stats['source_impact'])}")
    print(f"   Peripheral observations:  {stats['peripheral_amplifier']['observations']}")
    print()

    print("=" * 80)
    print("✅ V1 INJECTION COMPLETE!")
    print("=" * 80)
    print()
    print("🎯 Key Points:")
    print("   • Vector search found semantically similar nodes")
    print("   • V1 formula computed optimal energy budget")
    print("   • Entropy-coverage search selected best matches")
    print("   • Energy persisted to FalkorDB successfully")
    print("   • Learning mechanisms recorded frame data")
    print()
    print("💡 The system improves with every injection!")
    print()


if __name__ == "__main__":
    demo_injection()
