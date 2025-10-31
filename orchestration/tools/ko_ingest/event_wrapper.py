#!/usr/bin/env python3
"""
Event-Native KO Ingestion Wrapper

Wraps existing tools (MarkdownChunker + map_and_link) to emit KO events instead of direct writes.

Flow:
1. MD file → MarkdownChunker → chunks
2. Emit docs.ingest.chunk event per chunk
3. KO Extractor consumes events → map_and_link → KO proposals
4. Emit ko.cluster.proposed events
5. KO Applier consumes proposals → GraphWrapper.ensure_* → write confirmation
6. Emit ko.cluster.applied or ko.cluster.rejected

Author: Ada Bridgekeeper
Date: 2025-10-30
Spec: KO-First Documentation Architecture - Membrane-Pure Ingestion
"""

import asyncio
import json
import os
import sys
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Add tools to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "tools" / "doc_ingestion"))

try:
    from md_chunker import MarkdownChunker
except ImportError:
    print("⚠️  Warning: md_chunker not found, using mock chunker")
    MarkdownChunker = None


class EventNativeIngestion:
    """
    Event-native wrapper for KO ingestion pipeline.

    Converts imperative pipeline (MD → chunks → KOs → graph writes)
    into event-driven flow (MD → chunk events → proposal events → apply events).
    """

    def __init__(self, repo_root: str = "/home/mind-protocol/mindprotocol"):
        self.repo_root = repo_root
        self.tool_id = "tool.ko.ingest"
        self.event_log = []

        print(f"[{self.tool_id}] Initializing Event-Native KO Ingestion")
        print(f"[{self.tool_id}] Repository root: {repo_root}")

    async def ingest_file(self, file_path: str, sensitivity: str = "internal") -> List[Dict[str, Any]]:
        """
        Ingest a single MD file via events.

        Args:
            file_path: Relative path from repo root (e.g., "docs/patterns/builder.md")
            sensitivity: public|internal|restricted

        Returns:
            List of events emitted (chunk events + proposal events)
        """
        full_path = os.path.join(self.repo_root, file_path)

        if not os.path.exists(full_path):
            print(f"[{self.tool_id}] ERROR: File not found: {full_path}")
            return []

        print(f"\n[{self.tool_id}] Ingesting: {file_path}")
        print(f"  - Sensitivity: {sensitivity}")

        # Step 1: Read file
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        print(f"  - File hash: sha256:{file_hash[:16]}...")
        print(f"  - File size: {len(content)} chars")

        # Step 2: Chunk via MarkdownChunker
        chunks = await self._chunk_file(file_path, content)
        print(f"  - Chunks created: {len(chunks)}")

        # Step 3: Emit docs.ingest.chunk events
        chunk_events = []
        for i, chunk in enumerate(chunks):
            event = self._create_chunk_event(file_path, i, chunk, file_hash, sensitivity)
            chunk_events.append(event)
            self._log_event(event, f"CHUNK_{i}")

        print(f"  ✓ Emitted {len(chunk_events)} chunk events")

        # Step 4: Simulate KO extraction (in production: map_and_link consumes chunk events)
        proposal_events = []
        for chunk_event in chunk_events:
            proposals = await self._extract_kos_from_chunk(chunk_event)
            proposal_events.extend(proposals)

        if proposal_events:
            print(f"  ✓ Emitted {len(proposal_events)} proposal events")
        else:
            print(f"  ⚠️  No KO proposals extracted (would use map_and_link in production)")

        all_events = chunk_events + proposal_events
        return all_events

    async def _chunk_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Chunk file using MarkdownChunker (or mock).

        Returns:
            List of chunks: [{md, token_count, headers}]
        """
        if MarkdownChunker:
            # Use real chunker
            chunker = MarkdownChunker(target_tokens=250, max_tokens=480)
            chunk_objects = chunker.chunk_file(content)

            return [
                {
                    'md': chunk.content,
                    'token_count': chunk.token_count,
                    'headers': [],  # Chunk object doesn't have headers
                    'start_line': chunk.char_offset,  # Use char offset as approximation
                    'chunk_type': chunk.chunk_type
                }
                for chunk in chunk_objects
            ]
        else:
            # Mock chunker for testing
            lines = content.split('\n')
            chunk_size = 20  # 20 lines per chunk

            chunks = []
            for i in range(0, len(lines), chunk_size):
                chunk_lines = lines[i:i+chunk_size]
                chunks.append({
                    'md': '\n'.join(chunk_lines),
                    'token_count': len('\n'.join(chunk_lines)) // 4,
                    'headers': [],
                    'start_line': i
                })

            return chunks

    def _create_chunk_event(self, file_path: str, chunk_id: int, chunk: Dict[str, Any],
                           file_hash: str, sensitivity: str) -> Dict[str, Any]:
        """
        Create docs.ingest.chunk event from chunk data.
        """
        chunk_content = chunk['md']
        chunk_hash = hashlib.sha256(chunk_content.encode('utf-8')).hexdigest()

        return {
            "type": "docs.ingest.chunk",
            "id": f"chunk-{file_hash[:8]}-{chunk_id:03d}",
            "ts": datetime.utcnow().isoformat() + "Z",
            "spec": {"name": "ko.contract", "rev": "1.0"},
            "provenance": {
                "scope": "organizational",
                "ecosystem_id": "mind-network",
                "org_id": "mind-protocol",
                "component": f"component:{self.tool_id}",
                "source_file": file_path
            },
            "content": {
                "file_path": file_path,
                "chunk_id": chunk_id,
                "md": chunk_content,
                "token_count": chunk['token_count'],
                "sha256": chunk_hash,
                "sensitivity": sensitivity,
                "headers": chunk.get('headers', []),
                "start_line": chunk.get('start_line', 0)
            }
        }

    async def _extract_kos_from_chunk(self, chunk_event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract KOs from chunk event (mock implementation).

        In production: This would call map_and_link.py to extract typed nodes + edges.

        Returns:
            List of ko.cluster.proposed events
        """
        # Mock extraction: Create simple proposals from chunk content
        chunk_content = chunk_event['content']['md']
        chunk_id = chunk_event['id']

        # Simple heuristic: Look for headings and bullet points as potential KOs
        lines = chunk_content.split('\n')
        proposals = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Heading as Principle/Best_Practice/Mechanism
            if stripped.startswith('##'):
                heading_text = stripped.lstrip('#').strip()
                if heading_text:
                    node_type = self._guess_node_type(heading_text, i, len(lines))
                    proposal = self._create_ko_proposal(
                        chunk_id, f"heading_{i}",
                        node_type, heading_text,
                        chunk_event['content']['file_path'],
                        chunk_event['content']['sensitivity']
                    )
                    proposals.append(proposal)

            # Only extract from first few lines to keep mock minimal
            if i > 5:
                break

        return proposals

    def _guess_node_type(self, text: str, line_num: int, total_lines: int) -> str:
        """Mock logic to guess KO type from heading text"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['principle', 'law', 'rule']):
            return 'Principle'
        elif any(word in text_lower for word in ['pattern', 'practice', 'approach']):
            return 'Best_Practice'
        elif any(word in text_lower for word in ['mechanism', 'algorithm', 'process']):
            return 'Mechanism'
        elif any(word in text_lower for word in ['metric', 'measure', 'indicator']):
            return 'Metric'
        else:
            # Default based on position
            if line_num < total_lines * 0.3:
                return 'Principle'
            elif line_num < total_lines * 0.6:
                return 'Best_Practice'
            else:
                return 'Mechanism'

    def _create_ko_proposal(self, chunk_id: str, node_id_suffix: str,
                           node_type: str, name: str, file_path: str,
                           sensitivity: str) -> Dict[str, Any]:
        """
        Create ko.cluster.proposed event for a single node.

        In production: map_and_link creates full clusters with nodes + edges.
        """
        node_id = f"{node_type.lower()}:{name.lower().replace(' ', '_')[:40]}"

        return {
            "type": "ko.cluster.proposed",
            "id": f"proposal-{chunk_id}-{node_id_suffix}",
            "ts": datetime.utcnow().isoformat() + "Z",
            "spec": {"name": "ko.contract", "rev": "1.0"},
            "provenance": {
                "scope": "organizational",
                "ecosystem_id": "mind-network",
                "org_id": "mind-protocol",
                "component": "component:tool.ko.extractor",
                "source_chunk": chunk_id
            },
            "content": {
                "source_file": file_path,
                "sensitivity": sensitivity,
                "nodes": [
                    {
                        "id": node_id,
                        "type_name": node_type,
                        "name": name,
                        "summary": f"Extracted from {file_path}"
                    }
                ],
                "edges": [],  # Mock: would include IMPLEMENTS/EXTENDS/etc
                "quality": {
                    "extraction_method": "mock_heading_extractor",
                    "confidence": 0.7
                }
            }
        }

    def _log_event(self, event: Dict[str, Any], stage: str):
        """Log event for tracing"""
        self.event_log.append({
            "stage": stage,
            "event_type": event["type"],
            "event_id": event["id"],
            "timestamp": event["ts"]
        })

    async def run_test(self, test_file: str = "docs/patterns/builder_energy.md"):
        """
        Run test ingestion on a sample file.
        """
        print(f"\n{'='*60}")
        print(f"[{self.tool_id}] Running Ingestion Test")
        print(f"{'='*60}\n")

        # Create mock test file if it doesn't exist
        test_path = os.path.join(self.repo_root, test_file)
        if not os.path.exists(test_path):
            print(f"[{self.tool_id}] Creating test file: {test_file}")
            os.makedirs(os.path.dirname(test_path), exist_ok=True)

            mock_content = """# Builder Energy Pattern

## Principle: Design Before Build

Architectural clarity precedes implementation.

## Best Practice: Spec-Driven Development

Write implementable specs, hand off to specialists.

## Mechanism: Clean Handoff Protocol

Provide:
- Context: What problem we're solving
- Requirements: What the solution must do
- Success Criteria: How we know it works

## Metrics

### Spec Completeness

Measure: percentage of required sections present
Method: Automated checks + peer review
"""
            with open(test_path, 'w') as f:
                f.write(mock_content)
            print(f"  ✓ Test file created")

        # Ingest file
        events = await self.ingest_file(test_file, sensitivity="internal")

        # Summary
        print(f"\n{'='*60}")
        print(f"[{self.tool_id}] Test Complete")
        print(f"{'='*60}\n")

        print(f"Events emitted: {len(events)}")
        print(f"  - Chunk events: {len([e for e in events if e['type'] == 'docs.ingest.chunk'])}")
        print(f"  - Proposal events: {len([e for e in events if e['type'] == 'ko.cluster.proposed'])}")

        print(f"\nEvent flow:")
        for i, log_entry in enumerate(self.event_log, 1):
            print(f"  {i}. {log_entry['stage']}: {log_entry['event_type']} ({log_entry['event_id']})")

        if events:
            print(f"\n--- SAMPLE EVENT (first chunk) ---")
            sample = events[0]
            print(json.dumps({
                "type": sample["type"],
                "id": sample["id"],
                "content": {
                    "file_path": sample["content"]["file_path"],
                    "chunk_id": sample["content"]["chunk_id"],
                    "token_count": sample["content"]["token_count"],
                    "md_preview": sample["content"]["md"][:200] + "..."
                }
            }, indent=2))

        print(f"\n✅ Next: Wire KO Applier to consume ko.cluster.proposed events")
        print(f"   Then: Apply via GraphWrapper → emit ko.cluster.applied/rejected")


async def main():
    """Main entry point for testing"""
    ingestion = EventNativeIngestion()
    await ingestion.run_test()


if __name__ == "__main__":
    asyncio.run(main())
