"""Diagnose nodes that failed to get id during migration."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from llama_index.graph_stores.falkordb import FalkorDBGraphStore


def diagnose_graph(graph_id: str):
    """Find nodes without id field and diagnose why."""

    print(f"\n{'='*60}")
    print(f"Diagnosing: {graph_id}")
    print(f"{'='*60}")

    graph_store = FalkorDBGraphStore(
        database=graph_id,
        url='redis://localhost:6379'
    )

    # Find nodes without id
    query = """
    MATCH (n)
    WHERE n.id IS NULL
    RETURN labels(n) AS labels, n.name AS name, keys(n) AS props
    LIMIT 10
    """

    result = graph_store.query(query)

    if not result or len(result) == 0:
        print("✓ No nodes without id")
        return

    print(f"Found {len(result)} nodes without id:")
    for row in result:
        labels = row[0]
        name = row[1]
        props = row[2]

        print(f"\n  Labels: {labels}")
        print(f"  Name: {name} (type: {type(name)})")
        print(f"  Properties: {props}")

        # Try to construct what id SHOULD be
        if labels and name:
            expected_id = f"{labels[0]}:{name}"
            print(f"  Expected id: {expected_id}")
        else:
            print(f"  ❌ Cannot construct id (labels={labels}, name={name})")


def main():
    citizens = [
        'citizen_ada',
        'citizen_atlas',
        'citizen_felix',
        'citizen_iris',
        'citizen_luca',
        'citizen_victor'
    ]

    for citizen_id in citizens:
        try:
            diagnose_graph(citizen_id)
        except Exception as e:
            print(f"❌ Error diagnosing {citizen_id}: {e}")


if __name__ == '__main__':
    main()
