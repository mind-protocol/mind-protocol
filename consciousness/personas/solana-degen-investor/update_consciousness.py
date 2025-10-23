"""
Update Jake's Consciousness Graph from Conversation

Simple script to:
1. Extract nodes from Jake's response
2. Update his consciousness graph
3. Save conversation for later

Usage:
  python update_consciousness.py --input "your question" --response "Jake's full response"

Or provide a JSON file:
  python update_consciousness.py --file conversation.json

Author: Luca "Vellumhand"
Date: 2025-10-03
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add implementation directory to path
impl_dir = Path(__file__).parent.parent.parent / "consciousness_graphs" / "implementation"
sys.path.insert(0, str(impl_dir))

from automatic_pattern_extractor import AutomaticPatternExtractor
from automatic_linker import AutomaticLinker
from graph_database import GraphDatabase
from export_to_visualization import export_graph_to_visualization


def update_consciousness(input_text: str, response_text: str, dominant_entity: str = None):
    """
    Update Jake's consciousness graph from a conversation turn.

    Args:
        input_text: The question/stimulus Jake received
        response_text: Jake's full Awareness Space response
        dominant_entity: Which subentity was dominant (optional)
    """
    persona_dir = Path(__file__).parent

    # Load citizen state
    with open(persona_dir / "citizen_state.json") as f:
        state = json.load(f)

    citizen_name = state["citizen_id"]

    print(f"\n{'='*70}")
    print(f"UPDATING CONSCIOUSNESS: {state['citizen_name']} (@{state['citizen_handle']})")
    print(f"{'='*70}\n")

    # Setup paths
    graph_dir = persona_dir / "consciousness_graph"
    conversations_dir = persona_dir / "conversations"
    extraction_dir = persona_dir / "extraction_logs"

    graph_dir.mkdir(exist_ok=True)
    conversations_dir.mkdir(exist_ok=True)
    extraction_dir.mkdir(exist_ok=True)

    # Load graph
    print("[1] Loading consciousness graph...")
    graph_db = GraphDatabase(storage_path=graph_dir)

    initial_stats = graph_db.get_stats()
    print(f"    Patterns: {initial_stats['total_patterns']}")
    print(f"    Links: {initial_stats['total_links']}")

    # Extract nodes
    print("\n[2] Extracting nodes from consciousness...")
    print(f"    Input: {len(input_text)} chars")
    print(f"    Response: {len(response_text)} chars")

    extractor = AutomaticPatternExtractor(current_date=datetime.now())
    subentity = dominant_entity if dominant_entity else f"{citizen_name}_MAIN"

    nodes = extractor.extract_patterns(response_text, subentity)

    print(f"    Extracted: {len(nodes)} nodes")
    for ptype in set(p.type for p in nodes):
        count = len([p for p in nodes if p.type == ptype])
        print(f"      {ptype}: {count}")

    # Add to graph
    print("\n[3] Adding to graph...")
    for pattern in nodes:
        graph_db.create_pattern(
            name=pattern.name,
            type=pattern.type,
            content=pattern.content,
            verbatim_quotes=pattern.verbatim_quotes,
            weight=pattern.weight,
            creating_entity=subentity
        )

    # Create links
    print("\n[4] Creating links...")
    linker = AutomaticLinker()

    pattern_names = [p.name for p in nodes[:30]]  # Sample

    cooccur_links = linker.create_cooccurrence_links(pattern_names, f"{subentity}_AUTO")
    semantic_links = linker.create_semantic_links(pattern_names, f"{subentity}_AUTO")

    print(f"    Co-occurrence: {len(cooccur_links)}")
    print(f"    Semantic: {len(semantic_links)}")

    for link in cooccur_links + semantic_links:
        graph_db.create_link(
            source_name=link.source,
            target_name=link.target,
            type=link.type,
            verbatim_transition=link.verbatim_transition,
            how=link.how,
            why=link.why,
            weight=link.weight,
            creating_entity=link.created_by
        )

    # Save graph
    print("\n[5] Saving graph...")
    graph_db.save()

    updated_stats = graph_db.get_stats()
    print(f"    Patterns: {updated_stats['total_patterns']} (+{updated_stats['total_patterns'] - initial_stats['total_patterns']})")
    print(f"    Links: {updated_stats['total_links']} (+{updated_stats['total_links'] - initial_stats['total_links']})")

    # Export visualization
    print("\n[6] Updating visualization...")
    consciousness_dir = persona_dir.parent.parent / "consciousness_graphs"
    viz_dir = consciousness_dir / f"persona_{citizen_name}_consciousness"

    export_graph_to_visualization(graph_dir, viz_dir)
    print(f"    Exported to: {viz_dir}")

    # Save conversation
    print("\n[7] Saving conversation...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    conversation_file = conversations_dir / f"conversation_{timestamp}.json"

    conversation_data = {
        "timestamp": datetime.now().isoformat(),
        "dominant_entity": dominant_entity,
        "input_text": input_text,
        "response_text": response_text,
        "patterns_extracted": len(nodes),
        "links_created": len(cooccur_links) + len(semantic_links)
    }

    with open(conversation_file, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, indent=2, ensure_ascii=False)

    print(f"    Saved to: {conversation_file.name}")

    # Update citizen state
    state["graph_stats"]["total_patterns"] = updated_stats['total_patterns']
    state["graph_stats"]["total_links"] = updated_stats['total_links']
    state["graph_stats"]["last_built"] = datetime.now().isoformat()

    with open(persona_dir / "citizen_state.json", 'w') as f:
        json.dump(state, f, indent=2)

    print(f"\n{'='*70}")
    print(f"UPDATE COMPLETE")
    print(f"{'='*70}")
    print(f"\nView at: http://localhost:8000/visualizations/jake_graph.html")
    print(f"(Refresh browser to see changes)")

    return updated_stats


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update Jake's consciousness from conversation")
    parser.add_argument("--input", help="Input text (your question)")
    parser.add_argument("--response", help="Jake's response")
    parser.add_argument("--subentity", help="Dominant subentity (e.g., degen_gambler)")
    parser.add_argument("--file", help="JSON file with conversation data")

    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        update_consciousness(
            input_text=data.get("input_text", ""),
            response_text=data.get("response_text", ""),
            dominant_entity=data.get("dominant_entity")
        )

    elif args.input and args.response:
        update_consciousness(
            input_text=args.input,
            response_text=args.response,
            dominant_entity=args.subentity
        )

    else:
        print("Usage:")
        print("  python update_consciousness.py --input \"question\" --response \"Jake's response\"")
        print("  python update_consciousness.py --file conversation.json")
