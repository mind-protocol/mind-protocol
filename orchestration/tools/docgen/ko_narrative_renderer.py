#!/usr/bin/env python3
"""
KO Narrative Documentation Renderer

Event-native tool that renders narrative documentation from L2 Knowledge Objects and SubEntity bundles.

Flow:
1. Subscribes to docs.request.generate events (mode: "narrative")
2. Queries L2 org graph for SubEntity bundles + KO vertical/horizontal chains
3. Renders markdown with narrative structure (overview → execution → metrics → tensions)
4. Emits docs.draft.created with KO provenance

Author: Ada Bridgekeeper
Date: 2025-10-30
Spec: KO-First Documentation Architecture
"""

import asyncio
import json
import redis
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib


class KONarrativeRenderer:
    """
    Event-native documentation renderer for KO-driven narrative docs.

    Renders narrative pages from:
    - SubEntity bundles (purpose, intent, anti-claims)
    - Vertical chains (Principle → Best_Practice → Mechanism)
    - Horizontal bundles (design tensions, complements)
    - Role nodes (Behavior, Process, Metric with link metadata)

    Pure membrane discipline - no REST APIs, no direct graph writes.
    """

    def __init__(self, l2_graph_host: str = "localhost", l2_graph_port: int = 6379,
                 l2_graph_name: str = "consciousness-infrastructure"):
        self.l2_db = redis.Redis(host=l2_graph_host, port=l2_graph_port, decode_responses=False)
        self.l2_graph = l2_graph_name
        self.tool_id = "tool.docgen.ko_narrative"

        print(f"[{self.tool_id}] Initializing KO Narrative Renderer")
        print(f"[{self.tool_id}] Connected to L2 graph: {l2_graph_name} at {l2_graph_host}:{l2_graph_port}")

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
                "constraints": {"mode": "narrative"},
                "description": "Renders narrative docs from L2 KOs and SubEntity bundles"
            }
        }

        print(f"[{self.tool_id}] Capability announcement ready:")
        print(f"  - Handles: docs.request.generate (mode: narrative)")
        print(f"  - Reads: L2 KO graph (SubEntities, vertical/horizontal chains)")
        print(f"  - Output: docs.draft.created events")

        # In production: emit via membrane bus
        print(f"[{self.tool_id}] [MOCK] Would emit tool.offer event")

        return capability_announcement

    async def handle_generate_request(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle docs.request.generate event (mode: "narrative").

        Args:
            event: Membrane envelope with docs.request.generate content

        Returns:
            docs.draft.created event envelope (or None if error)
        """
        try:
            content = event.get("content", {})
            path = content.get("path")
            mode = content.get("mode", "narrative")
            source_nodes = content.get("source_nodes", [])
            sensitivity = content.get("sensitivity", "internal")

            print(f"\n[{self.tool_id}] Received docs.request.generate")
            print(f"  - Path: {path}")
            print(f"  - Mode: {mode}")
            print(f"  - Source nodes: {source_nodes}")
            print(f"  - Sensitivity: {sensitivity}")

            if mode != "narrative":
                print(f"[{self.tool_id}] WARNING: Only 'narrative' mode supported, got '{mode}'")
                return None

            if not source_nodes:
                print(f"[{self.tool_id}] ERROR: No source_nodes provided (need SubEntity IDs)")
                return None

            subentity_id = source_nodes[0]  # Focus on first SubEntity

            # Query L2 for SubEntity bundle + KO chains
            bundle_data = self._fetch_subentity_bundle(subentity_id)

            if not bundle_data:
                print(f"[{self.tool_id}] No SubEntity found: {subentity_id}")
                return None

            # Render markdown with narrative structure
            rendered = self._render_narrative_page(bundle_data, subentity_id, path, sensitivity)

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
                    "quality_signals": {
                        "anchors": 1,
                        "sections": rendered.get("section_count", 0),
                        "ko_nodes": rendered.get("ko_count", 0)
                    },
                    "rendered_at": datetime.utcnow().isoformat() + "Z"
                }
            }

            print(f"[{self.tool_id}] Draft created:")
            print(f"  - Path: {path}")
            print(f"  - Content length: {len(rendered['body'])} chars")
            print(f"  - Sections: {rendered.get('section_count', 0)}")
            print(f"  - KO nodes: {rendered.get('ko_count', 0)}")

            return draft_event

        except Exception as e:
            print(f"[{self.tool_id}] ERROR handling request: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _fetch_subentity_bundle(self, subentity_id: str) -> Optional[Dict[str, Any]]:
        """
        Query L2 graph for SubEntity bundle data.

        Args:
            subentity_id: SubEntity node ID (e.g., "subentity:builder_energy")

        Returns:
            Bundle data: {bundle: {purpose, intent, anti_claims},
                         vertical_chain: [...],
                         horizontal_bundle: [...],
                         roles: [...]}
        """
        try:
            # Query SubEntity bundle (purpose, intent, anti-claims)
            query_bundle = f"""
            MATCH (se:SubEntity {{id: '{subentity_id}'}})
            RETURN se.purpose as purpose, se.intent as intent, se.anti_claims as anti_claims,
                   se.slug as slug, se.name as name
            """
            result = self.l2_db.execute_command('GRAPH.QUERY', self.l2_graph, query_bundle)

            if not result or not result[1]:
                return None

            row = result[1][0]
            bundle = {
                'purpose': self._decode(row[0]) if len(row) > 0 else '',
                'intent': self._decode(row[1]) if len(row) > 1 else '',
                'anti_claims': self._decode(row[2]) if len(row) > 2 else '',
                'slug': self._decode(row[3]) if len(row) > 3 else subentity_id,
                'name': self._decode(row[4]) if len(row) > 4 else ''
            }

            # Query vertical chain (Principle → Best_Practice → Mechanism)
            query_vertical = f"""
            MATCH (se:SubEntity {{id: '{subentity_id}'}})-[:IMPLEMENTS|EXTENDS*1..3]->(n)
            WHERE n.type_name IN ['Principle', 'Best_Practice', 'Mechanism']
            RETURN n.id, n.type_name, n.name, n.summary
            ORDER BY n.type_name
            """
            result_vertical = self.l2_db.execute_command('GRAPH.QUERY', self.l2_graph, query_vertical)
            vertical_chain = self._parse_node_results(result_vertical)

            # Query horizontal bundle (tensions, complements)
            query_horizontal = f"""
            MATCH (se:SubEntity {{id: '{subentity_id}'}})-[r:RELATES_TO|ENABLES|REQUIRES|AFFECTS]->(n)
            RETURN n.id, n.type_name, n.name, type(r) as rel_type, r.meta as meta
            """
            result_horizontal = self.l2_db.execute_command('GRAPH.QUERY', self.l2_graph, query_horizontal)
            horizontal_bundle = self._parse_relation_results(result_horizontal)

            # Query roles (Behavior, Process, Metric with MEASURES meta)
            query_roles = f"""
            MATCH (se:SubEntity {{id: '{subentity_id}'}})-[r:MEASURES|PROCESS_FOR|SPEC_ROLE]->(m)
            WHERE m.type_name IN ['Behavior', 'Process', 'Metric']
            RETURN m.id, m.type_name, m.name, type(r) as rel_type, r.meta as meta
            """
            result_roles = self.l2_db.execute_command('GRAPH.QUERY', self.l2_graph, query_roles)
            roles = self._parse_relation_results(result_roles)

            print(f"[{self.tool_id}] L2 query returned:")
            print(f"  - Bundle: {bundle['slug']}")
            print(f"  - Vertical chain: {len(vertical_chain)} nodes")
            print(f"  - Horizontal bundle: {len(horizontal_bundle)} relations")
            print(f"  - Roles: {len(roles)} nodes")

            return {
                'bundle': bundle,
                'vertical_chain': vertical_chain,
                'horizontal_bundle': horizontal_bundle,
                'roles': roles
            }

        except Exception as e:
            print(f"[{self.tool_id}] ERROR querying L2: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _parse_node_results(self, result) -> List[Dict[str, Any]]:
        """Parse FalkorDB node query results"""
        if not result or not result[1]:
            return []

        nodes = []
        for row in result[1]:
            nodes.append({
                'id': self._decode(row[0]),
                'type_name': self._decode(row[1]) if len(row) > 1 else '',
                'name': self._decode(row[2]) if len(row) > 2 else '',
                'summary': self._decode(row[3]) if len(row) > 3 else ''
            })
        return nodes

    def _parse_relation_results(self, result) -> List[Dict[str, Any]]:
        """Parse FalkorDB relationship query results"""
        if not result or not result[1]:
            return []

        relations = []
        for row in result[1]:
            relations.append({
                'id': self._decode(row[0]),
                'type_name': self._decode(row[1]) if len(row) > 1 else '',
                'name': self._decode(row[2]) if len(row) > 2 else '',
                'rel_type': self._decode(row[3]) if len(row) > 3 else '',
                'meta': self._decode(row[4]) if len(row) > 4 else '{}'
            })
        return relations

    def _decode(self, value):
        """Decode bytes to string if needed"""
        if isinstance(value, bytes):
            return value.decode('utf-8')
        return value if value is not None else ''

    def _render_narrative_page(self, bundle_data: Dict[str, Any], subentity_id: str,
                               path: str, sensitivity: str) -> Dict[str, Any]:
        """
        Render narrative markdown from SubEntity bundle + KO chains.

        Args:
            bundle_data: SubEntity bundle + chains from L2
            subentity_id: SubEntity ID
            path: Target file path
            sensitivity: public|internal|restricted

        Returns:
            {"front_matter": {...}, "body": "...", "section_count": N, "ko_count": M}
        """
        bundle = bundle_data['bundle']
        vertical_chain = bundle_data['vertical_chain']
        horizontal_bundle = bundle_data['horizontal_bundle']
        roles = bundle_data['roles']

        # Generate title from slug
        title = bundle['slug'].replace('_', ' ').replace('-', ' ').title()

        # Generate front matter
        front_matter = {
            'title': title,
            'doc_type': 'narrative',
            'sensitivity': sensitivity,
            'anchors': {
                'subentities': [subentity_id]
            },
            'provenance': {
                'author': self.tool_id,
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'source': 'L2 Knowledge Objects (org graph)'
            }
        }

        # Generate markdown body
        body_lines = [
            f"# {title}",
            "",
            f"**Generated from L2 Knowledge Objects** - {datetime.utcnow().strftime('%Y-%m-%d')}",
            "",
            "---",
            "",
        ]

        # Section 1: Overview (from SubEntity bundle)
        body_lines.extend([
            "## Overview",
            "",
            f"**Purpose:** {bundle.get('purpose', 'Not documented')}",
            "",
        ])

        if bundle.get('intent'):
            body_lines.extend([
                f"**Intent:** {bundle['intent']}",
                "",
            ])

        if bundle.get('anti_claims'):
            body_lines.extend([
                "**Anti-Claims (What This Is NOT):**",
                "",
                bundle['anti_claims'],
                "",
            ])

        # Section 2: Execution Spine (from vertical chain)
        if vertical_chain:
            body_lines.extend([
                "## Execution Spine",
                "",
                "The implementation hierarchy for this pattern:",
                "",
            ])

            # Group by type
            by_type = {}
            for node in vertical_chain:
                node_type = node['type_name']
                if node_type not in by_type:
                    by_type[node_type] = []
                by_type[node_type].append(node)

            # Render in order: Principle → Best_Practice → Mechanism
            for node_type in ['Principle', 'Best_Practice', 'Mechanism']:
                if node_type in by_type:
                    body_lines.append(f"### {node_type.replace('_', ' ')}")
                    body_lines.append("")
                    for node in by_type[node_type]:
                        body_lines.append(f"**{node['name']}**")
                        if node.get('summary'):
                            body_lines.append(f"{node['summary']}")
                        body_lines.append(f"*KO Reference:* `{node['id']}`")
                        body_lines.append("")

        # Section 3: Metrics & Verification (from roles with MEASURES)
        if roles:
            metrics = [r for r in roles if r['type_name'] == 'Metric']
            if metrics:
                body_lines.extend([
                    "## Metrics & Verification",
                    "",
                    "Measurable indicators for this pattern:",
                    "",
                ])

                for metric in metrics:
                    body_lines.append(f"### {metric['name']}")
                    body_lines.append("")

                    # Parse meta for units/method
                    try:
                        meta = json.loads(metric['meta']) if metric['meta'] and metric['meta'] != '{}' else {}
                        if meta.get('unit'):
                            body_lines.append(f"**Unit:** {meta['unit']}")
                        if meta.get('method'):
                            body_lines.append(f"**Method:** {meta['method']}")
                    except:
                        pass

                    body_lines.append(f"*KO Reference:* `{metric['id']}`")
                    body_lines.append("")

        # Section 4: Design Tensions (from horizontal bundle)
        if horizontal_bundle:
            body_lines.extend([
                "## Design Tensions & Relationships",
                "",
                "How this pattern relates to others:",
                "",
            ])

            for rel in horizontal_bundle:
                body_lines.append(f"**{rel['rel_type']}** → {rel['name']} (`{rel['id']}`)")

                # Parse meta for rationale
                try:
                    meta = json.loads(rel['meta']) if rel['meta'] and rel['meta'] != '{}' else {}
                    if meta.get('rationale'):
                        body_lines.append(f"  - *Rationale:* {meta['rationale']}")
                except:
                    pass

                body_lines.append("")

        # Provenance footer
        body_lines.extend([
            "",
            "---",
            "",
            "## Provenance",
            "",
            f"**Source:** L2 Knowledge Objects (org graph)",
            f"**SubEntity:** `{subentity_id}`",
            f"**Generated:** {datetime.utcnow().isoformat()}Z",
            "",
            "**Knowledge Objects Referenced:**",
        ])

        # List all KO IDs
        all_kos = set()
        for node in vertical_chain:
            all_kos.add(node['id'])
        for rel in horizontal_bundle:
            all_kos.add(rel['id'])
        for role in roles:
            all_kos.add(role['id'])

        for ko_id in sorted(all_kos):
            body_lines.append(f"- `{ko_id}`")

        body = '\n'.join(body_lines)

        # Compute content hash
        content_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()
        front_matter['content_hash'] = f"sha256:{content_hash}"

        return {
            'front_matter': front_matter,
            'body': body,
            'section_count': 4,  # Overview + Spine + Metrics + Tensions
            'ko_count': len(all_kos)
        }

    async def run_mock_test(self):
        """Run mock test with simulated SubEntity data"""
        print(f"\n{'='*60}")
        print(f"[{self.tool_id}] Running Mock Test")
        print(f"{'='*60}\n")

        # Step 1: Announce capability
        await self.announce_capability()

        # Step 2: Create mock SubEntity data (simulates what would be in L2)
        mock_subentity_id = "subentity:builder_energy"
        mock_bundle_data = {
            'bundle': {
                'slug': 'builder_energy',
                'name': 'Builder Energy',
                'purpose': 'The drive to architect solutions immediately when seeing solvable problems',
                'intent': 'Channel architectural capability toward high-value system design',
                'anti_claims': 'NOT about implementation (that\'s for engineers). NOT about endless design without delivery.'
            },
            'vertical_chain': [
                {'id': 'principle:design_before_build', 'type_name': 'Principle',
                 'name': 'Design Before Build', 'summary': 'Architectural clarity precedes implementation'},
                {'id': 'best_practice:spec_driven_dev', 'type_name': 'Best_Practice',
                 'name': 'Spec-Driven Development', 'summary': 'Write implementable specs, hand off to specialists'},
                {'id': 'mechanism:handoff_protocol', 'type_name': 'Mechanism',
                 'name': 'Clean Handoff Protocol', 'summary': 'Context + Requirements + Success Criteria'}
            ],
            'horizontal_bundle': [
                {'id': 'subentity:skeptic_energy', 'type_name': 'SubEntity', 'name': 'Skeptic Energy',
                 'rel_type': 'BALANCES', 'meta': '{"rationale": "Prevents premature architecture"}'}
            ],
            'roles': [
                {'id': 'metric:spec_completeness', 'type_name': 'Metric', 'name': 'Spec Completeness',
                 'rel_type': 'MEASURES', 'meta': '{"unit": "percentage", "method": "Required sections present"}'}
            ]
        }

        # Override _fetch_subentity_bundle to return mock data
        original_fetch = self._fetch_subentity_bundle
        self._fetch_subentity_bundle = lambda sid: mock_bundle_data if sid == mock_subentity_id else None

        # Step 3: Mock incoming docs.request.generate event
        mock_request = {
            "type": "docs.request.generate",
            "id": "test-request-ko-narrative-001",
            "ts": datetime.utcnow().isoformat() + "Z",
            "spec": {"name": "docs.contract", "rev": "1.0"},
            "provenance": {
                "scope": "organizational",
                "ecosystem_id": "mind-network",
                "org_id": "mind-protocol",
                "component": "component:test.ko_narrative"
            },
            "content": {
                "path": "docs/patterns/builder_energy.md",
                "mode": "narrative",
                "source_nodes": [mock_subentity_id],
                "sensitivity": "internal"
            }
        }

        # Step 4: Handle request
        draft_event = await self.handle_generate_request(mock_request)

        if draft_event:
            print(f"\n[{self.tool_id}] SUCCESS - Draft event created")
            print(f"\n--- DRAFT EVENT PREVIEW ---")
            print(f"Type: {draft_event['type']}")
            print(f"Path: {draft_event['content']['path']}")
            print(f"Sections: {draft_event['content']['quality_signals']['sections']}")
            print(f"KO nodes: {draft_event['content']['quality_signals']['ko_nodes']}")
            print(f"\n--- RENDERED MARKDOWN PREVIEW (first 800 chars) ---")
            print(draft_event['content']['md'][:800])
            print("...")
        else:
            print(f"\n[{self.tool_id}] FAILED - No draft created")

        # Restore original function
        self._fetch_subentity_bundle = original_fetch

        print(f"\n{'='*60}")
        print(f"[{self.tool_id}] Mock Test Complete")
        print(f"{'='*60}\n")


async def main():
    """Main entry point for testing"""
    renderer = KONarrativeRenderer()
    await renderer.run_mock_test()


if __name__ == "__main__":
    asyncio.run(main())
