#!/usr/bin/env python3
"""
Documentation Publisher

Event-native tool that accepts docs.page.upsert events, writes to repo, and emits publish events.

Flow:
1. Subscribes to docs.page.upsert events via membrane
2. Writes page to repository (file system)
3. Emits docs.publish event to trigger site build + broadcasts

Author: Ada Bridgekeeper
Date: 2025-10-30
Spec: Phase 1 - Minimal Tool Mesh
"""

import asyncio
import json
import os
import yaml
from typing import Dict, Any, Optional
from datetime import datetime


class DocPublisher:
    """
    Event-native documentation publisher.

    Accepts doc upsert events, writes to repo, emits publish events.
    Pure membrane discipline - no REST APIs, no polling.
    """

    def __init__(self, repo_root: str = "/home/mind-protocol/mindprotocol"):
        self.repo_root = repo_root
        self.tool_id = "tool.doc.publisher"

        print(f"[{self.tool_id}] Initializing Documentation Publisher")
        print(f"[{self.tool_id}] Repository root: {repo_root}")

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
                "capabilities": ["docs.page.upsert"],
                "constraints": {},
                "description": "Writes documentation pages to repo and emits publish events"
            }
        }

        print(f"[{self.tool_id}] Capability announcement ready:")
        print(f"  - Handles: docs.page.upsert")
        print(f"  - Writes to: {self.repo_root}")
        print(f"  - Emits: docs.publish events")

        # In production: emit via membrane bus
        # For now: mock announcement
        print(f"[{self.tool_id}] [MOCK] Would emit tool.offer event")

        return capability_announcement

    async def handle_page_upsert(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle docs.page.upsert event.

        Args:
            event: Membrane envelope with docs.page.upsert content

        Returns:
            docs.publish event envelope (or None if error)
        """
        try:
            content = event.get("content", {})
            path = content.get("path")
            md_content = content.get("md")
            front_matter = content.get("front_matter", {})

            print(f"\n[{self.tool_id}] Received docs.page.upsert")
            print(f"  - Path: {path}")
            print(f"  - Content length: {len(md_content)} chars")
            print(f"  - Front matter keys: {list(front_matter.keys())}")

            if not path or not md_content:
                print(f"[{self.tool_id}] ERROR: Missing required fields (path or md)")
                return None

            # Governance checks (placeholder - in production, check payload size, rate limits, etc.)
            if len(md_content) > 64 * 1024:  # 64KB limit from governance policy
                print(f"[{self.tool_id}] ERROR: Content exceeds 64KB payload limit")
                return None

            # Write to repository
            success = await self._write_to_repo(path, md_content, front_matter)

            if not success:
                print(f"[{self.tool_id}] ERROR: Failed to write to repo")
                return None

            # Emit publish event
            publish_event = {
                "type": "docs.publish",
                "id": f"publish-{datetime.utcnow().isoformat()}",
                "ts": datetime.utcnow().isoformat() + "Z",
                "spec": {"name": "docs.contract", "rev": "1.0"},
                "provenance": {
                    "scope": "organizational",
                    "ecosystem_id": event["provenance"]["ecosystem_id"],
                    "org_id": event["provenance"]["org_id"],
                    "component": f"component:{self.tool_id}",
                    "source": event["id"]  # Reference to upsert event
                },
                "content": {
                    "version": datetime.utcnow().isoformat(),
                    "changed_paths": [path],
                    "published_at": datetime.utcnow().isoformat() + "Z",
                    "trigger": "page_upsert"
                }
            }

            print(f"[{self.tool_id}] Page published:")
            print(f"  - Path: {path}")
            print(f"  - Version: {publish_event['content']['version']}")
            print(f"  - Trigger: site build + WS broadcast")

            return publish_event

        except Exception as e:
            print(f"[{self.tool_id}] ERROR handling upsert: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def _write_to_repo(self, path: str, md_content: str, front_matter: Dict[str, Any]) -> bool:
        """
        Write documentation page to repository.

        Args:
            path: Relative path within repo (e.g., "docs/protocol/overview.md")
            md_content: Markdown content body
            front_matter: YAML front matter dict

        Returns:
            True if successful, False otherwise
        """
        try:
            # Construct full path
            full_path = os.path.join(self.repo_root, path)

            # Ensure parent directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Write file with YAML front matter + markdown content
            with open(full_path, 'w') as f:
                if front_matter:
                    f.write("---\n")
                    yaml.dump(front_matter, f, default_flow_style=False, sort_keys=False)
                    f.write("---\n\n")
                f.write(md_content)

            print(f"[{self.tool_id}] File written: {full_path}")
            return True

        except Exception as e:
            print(f"[{self.tool_id}] ERROR writing file: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def run_mock_test(self):
        """Run mock test to verify functionality"""
        print(f"\n{'='*60}")
        print(f"[{self.tool_id}] Running Mock Test")
        print(f"{'='*60}\n")

        # Step 1: Announce capability
        await self.announce_capability()

        # Step 2: Mock incoming docs.page.upsert event (from L4 renderer output)
        mock_upsert = {
            "type": "docs.page.upsert",
            "id": "test-upsert-001",
            "ts": datetime.utcnow().isoformat() + "Z",
            "spec": {"name": "docs.contract", "rev": "1.0"},
            "provenance": {
                "scope": "organizational",
                "ecosystem_id": "mind-network",
                "org_id": "mind-protocol",
                "component": "component:orchestrator.l2"
            },
            "content": {
                "path": "docs/protocol/test_events_reference.md",
                "md": "# Test Events Reference\n\nThis is a test document from Phase 1 minimal tool mesh.\n\n## Test Event\n\n**Summary:** Test event for documentation pipeline\n",
                "front_matter": {
                    "title": "Test Events Reference",
                    "generated": "canonical",
                    "l4_citations": ["protocol/Event_Schema/docs.request.generate"],
                    "retrieved_at": datetime.utcnow().isoformat() + "Z"
                }
            }
        }

        # Step 3: Handle upsert
        publish_event = await self.handle_page_upsert(mock_upsert)

        if publish_event:
            print(f"\n[{self.tool_id}] SUCCESS - Publish event created")
            print(f"\n--- PUBLISH EVENT ---")
            print(json.dumps(publish_event, indent=2))
        else:
            print(f"\n[{self.tool_id}] FAILED - No publish event created")

        print(f"\n{'='*60}")
        print(f"[{self.tool_id}] Mock Test Complete")
        print(f"{'='*60}\n")


async def main():
    """Main entry point for testing"""
    publisher = DocPublisher()
    await publisher.run_mock_test()


if __name__ == "__main__":
    asyncio.run(main())
