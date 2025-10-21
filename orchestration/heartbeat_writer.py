"""
Heartbeat Writer - File-based health monitoring for Python processes

Writes timestamped JSON heartbeat files every 10 seconds to signal process is alive.
The System Status API checks these files to report component health in the dashboard.

Usage:
    from orchestration.heartbeat_writer import HeartbeatWriter

    heartbeat = HeartbeatWriter("consciousness_engine")
    heartbeat.start()

    # Your main loop here

    heartbeat.stop()

Author: Iris "The Aperture" (Observability Architect)
Date: 2025-10-19
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class HeartbeatWriter:
    """Writes heartbeat file to signal this process is alive."""

    def __init__(self, component_name: str):
        """
        Initialize heartbeat writer.

        Args:
            component_name: Component identifier (e.g., "consciousness_engine", "conversation_watcher")
        """
        self.component_name = component_name
        self.heartbeat_dir = Path(__file__).parent.parent / ".heartbeats"
        self.heartbeat_path = self.heartbeat_dir / f"{component_name}.heartbeat"
        self.running = False
        self.task: Optional[asyncio.Task] = None

        # Create heartbeats directory if needed
        self.heartbeat_dir.mkdir(exist_ok=True)

    async def write_heartbeat(self, **metadata):
        """
        Write a single heartbeat file with optional metadata.

        Args:
            **metadata: Optional component-specific metadata to include
        """
        try:
            heartbeat_data: Dict[str, Any] = {
                "component": self.component_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "pid": os.getpid(),
                "status": "active",
                **metadata  # Optional component-specific fields
            }

            # Atomic write (temp file + rename)
            temp_path = self.heartbeat_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(heartbeat_data, f, indent=2)
            temp_path.replace(self.heartbeat_path)

        except Exception as e:
            logger.error(f"[Heartbeat] Failed to write {self.component_name}: {e}")

    async def heartbeat_loop(self):
        """Background loop that writes heartbeats every 10 seconds."""
        logger.info(f"[Heartbeat] Starting heartbeat writer for {self.component_name}")

        while self.running:
            await self.write_heartbeat()

            # Sleep in 1s chunks for responsive shutdown
            for _ in range(10):
                if not self.running:
                    break
                await asyncio.sleep(1)

        logger.info(f"[Heartbeat] Stopped for {self.component_name}")

    def start(self):
        """Start background heartbeat task."""
        if self.running:
            logger.warning(f"[Heartbeat] Already running for {self.component_name}")
            return

        self.running = True
        self.task = asyncio.create_task(self.heartbeat_loop())
        logger.info(f"[Heartbeat] Started for {self.component_name}")

    async def stop(self):
        """Stop heartbeat and clean up file."""
        self.running = False
        if self.task:
            await self.task

        # Remove heartbeat file on shutdown
        if self.heartbeat_path.exists():
            self.heartbeat_path.unlink()
            logger.info(f"[Heartbeat] Cleaned up heartbeat file for {self.component_name}")
