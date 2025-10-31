#!/usr/bin/env python3
"""
L4 Canonical Documentation Renderer

Event-native tool that renders documentation from L4 protocol graph.

Flow:
1. Subscribes to docs.request.generate events via membrane
2. Queries L4 protocol graph for canonical truth
3. Renders markdown with provenance (front matter + citations)
4. Emits docs.draft.created back to L2 via membrane

Author: Ada Bridgekeeper
Date: 2025-10-30
Spec: Phase 1 - Minimal Tool Mesh
"""

import asyncio
import json
import redis
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime


class L4CanonicalRenderer:
    """
    Event-native documentation renderer.

    Renders docs from L4 protocol graph and emits drafts via membrane.
    Pure membrane discipline - no REST APIs, no polling.
    """

    def __init__(self, protocol_graph_host: str = "localhost", protocol_graph_port: int = 6379):
        self.protocol_db = redis.Redis(host=protocol_graph_host, port=protocol_graph_port, decode_responses=False)
        self.tool_id = "tool.docgen.l4_canonical"

        print(f"[{self.tool_id}] Initializing L4 Canonical Renderer")
        print(f"[{self.tool_id}] Connected to protocol graph at {protocol_graph_host}:{protocol_graph_port}")

    async def announce_capability(self):
        """Announce tool capability to ecosystem via tool.offer event"""
        capability_announcement = {
            "type": "tool.offer",
            "id": f"tool-offer-{datetime.utcnow().isoformat()}",
            "ts": datetime.utcnow().isoformat() + "Z",
            "spec": {"name": "tool.contract", "rev": "1.0"},
            "provenance": {
                "scope": "organizational",
                "ecosystem_id": "mind-network",
                "org_id": "mind-protocol",
                "component": f"component:{self.tool_id}"
            },
            "content": {
                "tool_id": self.tool_id,
                "capabilities": ["docs.request.generate"],
                "constraints": {"mode": "canonical"},
                "description": "Renders documentation from L4 protocol graph with provenance"
            }
        }

        print(f"[{self.tool_id}] Capability announcement ready:")
        print(f"  - Handles: docs.request.generate")
        print(f"  - Mode: canonical (from L4 protocol graph)")
        print(f"  - Output: docs.draft.created events")

        # In production: emit via membrane bus
        # For now: mock announcement
        print(f"[{self.tool_id}] [MOCK] Would emit tool.offer event")

        return capability_announcement

    async def handle_generate_request(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle docs.request.generate event.

        Args:
            event: Membrane envelope with docs.request.generate content

        Returns:
            docs.draft.created event envelope (or None if error)
        """
        try:
            content = event.get("content", {})
            path = content.get("path")
            mode = content.get("mode", "canonical")
            source_nodes = content.get("source_nodes", [])
            priority = content.get("priority", "normal")

            print(f"\n[{self.tool_id}] Received docs.request.generate")
            print(f"  - Path: {path}")
            print(f"  - Mode: {mode}")
            print(f"  - Source nodes: {len(source_nodes)} specified")
            print(f"  - Priority: {priority}")

            if mode != "canonical":
                print(f"[{self.tool_id}] WARNING: Only 'canonical' mode supported, got '{mode}'")
                return None

            # Query L4 for canonical data
            doc_data = self._query_l4_canonical(source_nodes)

            if not doc_data:
                print(f"[{self.tool_id}] No data found in L4 for sources: {source_nodes}")
                return None

            # Render markdown with provenance
            rendered = self._render_canonical_page(doc_data, source_nodes, path)

            # Emit draft back to L2
            draft_event = {
                "type": "docs.draft.created",
                "id": f"draft-{datetime.utcnow().isoformat()}",
                "ts": datetime.utcnow().isoformat() + "Z",
                "spec": {"name": "docs.contract", "rev": "1.0"},
                "provenance": {
                    "scope": "organizational",
                    "ecosystem_id": event["provenance"]["ecosystem_id"],
                    "org_id": event["provenance"]["org_id"],
                    "component": f"component:{self.tool_id}",
                    "source": event["id"]  # Reference to request
                },
                "content": {
                    "path": path,
                    "md": rendered["body"],
                    "front_matter": rendered["front_matter"],
                    "l4_sources": source_nodes,
                    "rendered_at": datetime.utcnow().isoformat() + "Z"
                }
            }

            print(f"[{self.tool_id}] Draft created:")
            print(f"  - Path: {path}")
            print(f"  - Content length: {len(rendered['body'])} chars")
            print(f"  - Citations: {len(rendered['front_matter'].get('l4_citations', []))}")

            return draft_event

        except Exception as e:
            print(f"[{self.tool_id}] ERROR handling request: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _query_l4_canonical(self, source_nodes: List[str]) -> Optional[Dict[str, Any]]:
        """
        Query L4 protocol graph for canonical data.

        Args:
            source_nodes: List of L4 node IDs to query (e.g., ["protocol/Event_Schema/docs.request.generate"])

        Returns:
            Structured data from L4 graph
        """
        try:
            if not source_nodes:
                # Default: query all docs.* events
                query = """
                MATCH (es)
                WHERE es.type_name = 'Event_Schema' AND es.name STARTS WITH 'docs.'
                RETURN es.id, es.name, es.direction, es.topic_pattern, es.summary
                ORDER BY es.name
                """
            else:
                # Query specific nodes
                node_ids_str = ", ".join([f"'{nid}'" for nid in source_nodes])
                query = f"""
                MATCH (n)
                WHERE n.id IN [{node_ids_str}]
                RETURN n.id, n.type_name, n.name, n.summary, n.direction, n.topic_pattern
                """

            result = self.protocol_db.execute_command('GRAPH.QUERY', 'protocol', query)

            if not result or not result[1]:
                return None

            # Parse FalkorDB result
            rows = result[1]
            nodes = []

            for row in rows:
                node = {
                    'id': row[0].decode() if isinstance(row[0], bytes) else row[0],
                    'name': row[2].decode() if isinstance(row[2], bytes) else row[2] if len(row) > 2 else '',
                    'summary': row[3].decode() if isinstance(row[3], bytes) else row[3] if len(row) > 3 else '',
                }
                # Add optional fields if present
                if len(row) > 4:
                    node['direction'] = row[4].decode() if isinstance(row[4], bytes) else row[4]
                if len(row) > 5:
                    node['topic_pattern'] = row[5].decode() if isinstance(row[5], bytes) else row[5]

                nodes.append(node)

            print(f"[{self.tool_id}] L4 query returned {len(nodes)} nodes")

            return {
                'nodes': nodes,
                'query': query,
                'retrieved_at': datetime.utcnow().isoformat() + "Z"
            }

        except Exception as e:
            print(f"[{self.tool_id}] ERROR querying L4: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _render_canonical_page(self, doc_data: Dict[str, Any], source_nodes: List[str], path: str) -> Dict[str, str]:
        """
        Render markdown page with provenance.

        Args:
            doc_data: Data from L4 query
            source_nodes: L4 node IDs cited
            path: Target file path

        Returns:
            {"front_matter": {...}, "body": "..."}
        """
        nodes = doc_data.get('nodes', [])

        # Generate front matter (YAML)
        front_matter = {
            'title': self._infer_title_from_path(path),
            'generated': 'canonical',
            'l4_citations': [node['id'] for node in nodes],
            'retrieved_at': doc_data['retrieved_at'],
            'source': 'L4 Protocol Graph (protocol database)'
        }

        # Generate markdown body
        body_lines = [
            f"# {front_matter['title']}",
            "",
            f"**Generated from L4 Protocol Graph** - {datetime.utcnow().strftime('%Y-%m-%d')}",
            "",
            "---",
            "",
        ]

        if not nodes:
            body_lines.append("*No data found in L4 protocol graph.*")
        else:
            # Render nodes as documentation
            body_lines.append(f"## Event Schemas ({len(nodes)} total)")
            body_lines.append("")

            for node in nodes:
                body_lines.append(f"### {node.get('name', 'Unnamed')}")
                body_lines.append("")
                body_lines.append(f"**Summary:** {node.get('summary', 'No summary available')}")
                body_lines.append("")

                if 'direction' in node:
                    body_lines.append(f"**Direction:** `{node['direction']}`")
                if 'topic_pattern' in node:
                    body_lines.append(f"**Topic:** `{node['topic_pattern']}`")

                body_lines.append("")
                body_lines.append(f"**L4 Reference:** `{node['id']}`")
                body_lines.append("")
                body_lines.append("---")
                body_lines.append("")

        # Add provenance footer
        body_lines.extend([
            "",
            "---",
            "",
            "## Provenance",
            "",
            f"**Source:** L4 Protocol Graph (`protocol` database)",
            f"**Retrieved:** {doc_data['retrieved_at']}",
            f"**Citations:** {len(nodes)} L4 nodes",
            "",
            "**L4 Node IDs:**",
        ])

        for node in nodes:
            body_lines.append(f"- `{node['id']}`")

        return {
            'front_matter': front_matter,
            'body': '\n'.join(body_lines)
        }

    def _infer_title_from_path(self, path: str) -> str:
        """Infer document title from file path"""
        # Extract filename without extension
        filename = path.split('/')[-1].replace('.md', '')
        # Convert snake_case or kebab-case to Title Case
        title = filename.replace('_', ' ').replace('-', ' ').title()
        return title

    async def run_mock_test(self):
        """Run mock test to verify functionality"""
        print(f"\n{'='*60}")
        print(f"[{self.tool_id}] Running Mock Test")
        print(f"{'='*60}\n")

        # Step 1: Announce capability
        await self.announce_capability()

        # Step 2: Mock incoming docs.request.generate event
        mock_request = {
            "type": "docs.request.generate",
            "id": "test-request-001",
            "ts": datetime.utcnow().isoformat() + "Z",
            "spec": {"name": "docs.contract", "rev": "1.0"},
            "provenance": {
                "scope": "organizational",
                "ecosystem_id": "mind-network",
                "org_id": "mind-protocol",
                "component": "component:orchestrator.l2"
            },
            "content": {
                "path": "docs/protocol/events_reference.md",
                "mode": "canonical",
                "source_nodes": [],  # Empty = query all docs.* events
                "priority": "normal"
            }
        }

        # Step 3: Handle request
        draft_event = await self.handle_generate_request(mock_request)

        if draft_event:
            print(f"\n[{self.tool_id}] SUCCESS - Draft event created")
            print(f"\n--- DRAFT EVENT ---")
            print(json.dumps(draft_event, indent=2))
            print(f"\n--- RENDERED MARKDOWN PREVIEW (first 500 chars) ---")
            print(draft_event['content']['md'][:500])
            print("...")
        else:
            print(f"\n[{self.tool_id}] FAILED - No draft created")

        print(f"\n{'='*60}")
        print(f"[{self.tool_id}] Mock Test Complete")
        print(f"{'='*60}\n")


async def main():
    """Main entry point for testing"""
    renderer = L4CanonicalRenderer()
    await renderer.run_mock_test()


if __name__ == "__main__":
    asyncio.run(main())
