#!/usr/bin/env python3
"""
Parallel Document Ingestion Coordinator

Coordinates 5 parallel agents processing documentation corpus.
Each agent gets:
- A deterministic subset of pending files
- An isolated SQLite database (no concurrent write conflicts)

Usage:
    python parallel_ingest_coordinator.py

Author: Ada (Architect)
Date: 2025-10-29
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import time

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.doc_ingestion.ingest_docs import IngestionStateManager, ProcessingStatus


def get_all_files_from_manifest(manifest_path: str) -> List[Dict[str, Any]]:
    """
    Get all files from main manifest.

    Returns:
        List of file entries with sequence numbers
    """
    with open(manifest_path, 'r') as f:
        manifest_data = json.load(f)
    return manifest_data['processing_order']


def create_agent_databases(
    all_files: List[Dict[str, Any]],
    num_agents: int,
    db_dir: Path
) -> List[Path]:
    """
    Create isolated database for each agent.

    Each database is initialized with its agent's file subset.
    This eliminates SQLite concurrent write conflicts.

    Args:
        all_files: All files from main manifest
        num_agents: Number of parallel agents (5)
        db_dir: Directory for database files

    Returns:
        List of database file paths
    """
    db_dir.mkdir(parents=True, exist_ok=True)

    # Divide files into chunks (deterministic)
    chunk_size = len(all_files) // num_agents
    remainder = len(all_files) % num_agents

    db_paths = []
    start_idx = 0

    for agent_id in range(num_agents):
        # Calculate chunk size (distribute remainder across first agents)
        current_chunk_size = chunk_size + (1 if agent_id < remainder else 0)
        end_idx = start_idx + current_chunk_size

        # Extract chunk
        chunk = all_files[start_idx:end_idx]
        file_paths = [entry['path'] for entry in chunk]

        # Create agent-specific database
        db_path = db_dir / f".doc_ingestion_state_agent{agent_id}.db"

        # Initialize state manager with agent's database
        manager = IngestionStateManager(str(db_path))

        # Create temporary manifest for this agent's files
        temp_manifest = {
            "files": file_paths
        }
        temp_manifest_path = db_dir / f"temp_manifest_agent{agent_id}.json"
        with open(temp_manifest_path, 'w') as f:
            json.dump(temp_manifest, f)

        # Sync to populate database
        stats = manager.sync_manifest(str(temp_manifest_path))

        # Clean up temp manifest
        temp_manifest_path.unlink()

        db_paths.append(db_path)

        print(f"✅ Agent {agent_id}: {len(chunk)} files → {db_path.name}")
        print(f"   Seq {chunk[0]['sequence'] if chunk else 'N/A'}-{chunk[-1]['sequence'] if chunk else 'N/A'} | "
              f"New={stats['new']}, Changed={stats['changed']}")

        start_idx = end_idx

    return db_paths


def create_chunk_manifests(
    all_files: List[Dict[str, Any]],
    num_agents: int,
    output_dir: Path
) -> List[Path]:
    """
    Create N manifest files, each containing 1/N of files.

    Args:
        all_files: All file entries from main manifest
        num_agents: Number of parallel agents (5)
        output_dir: Directory to write manifest chunks

    Returns:
        List of manifest file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Divide files into chunks (deterministic)
    chunk_size = len(all_files) // num_agents
    remainder = len(all_files) % num_agents

    manifest_paths = []
    start_idx = 0

    for agent_id in range(num_agents):
        # Calculate chunk size (distribute remainder across first agents)
        current_chunk_size = chunk_size + (1 if agent_id < remainder else 0)
        end_idx = start_idx + current_chunk_size

        # Extract chunk
        chunk = all_files[start_idx:end_idx]
        file_paths = [entry['path'] for entry in chunk]

        manifest_data = {
            "metadata": {
                "agent_id": agent_id,
                "total_agents": num_agents,
                "chunk_size": len(chunk),
                "start_sequence": chunk[0]['sequence'] if chunk else None,
                "end_sequence": chunk[-1]['sequence'] if chunk else None,
                "generated": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "files": file_paths
        }

        # Write manifest
        manifest_path = output_dir / f"manifest_agent_{agent_id}.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)

        manifest_paths.append(manifest_path)

        start_idx = end_idx

    return manifest_paths


def generate_launch_commands(
    manifest_paths: List[Path],
    db_paths: List[Path],
    project_root: Path
) -> List[str]:
    """
    Generate shell commands to launch each agent with isolated database.

    Each command sets DOC_INGEST_STATE_DB_PATH to agent's dedicated database.

    Args:
        manifest_paths: Agent manifest files
        db_paths: Agent database files
        project_root: Project root directory

    Returns:
        List of shell commands (one per agent)
    """
    commands = []

    for agent_id, (manifest_path, db_path) in enumerate(zip(manifest_paths, db_paths)):
        cmd = (
            f"cd {project_root} && "
            f"DOC_INGEST_STATE_DB_PATH={db_path} "
            f"python3 tools/doc_ingestion/process_corpus.py {manifest_path}"
        )
        commands.append(cmd)

    return commands


def main():
    """Coordinate parallel ingestion with isolated databases."""

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    main_manifest = Path("/tmp/documentation_processing_order.json")
    output_dir = PROJECT_ROOT / "tools" / "doc_ingestion" / "manifests"

    print("=" * 60)
    print("📚 Parallel Document Ingestion Coordinator (Isolated DBs)")
    print("=" * 60)
    print()

    # Get all files
    print("🔍 Loading manifest...")
    all_files = get_all_files_from_manifest(str(main_manifest))
    print(f"   Total files: {len(all_files)}")
    print()

    if not all_files:
        print("⚠️  No files found in manifest!")
        return

    num_agents = 5

    # Create isolated databases
    print("🗄️  Creating isolated databases per agent...")
    db_paths = create_agent_databases(all_files, num_agents, output_dir)
    print()

    # Create chunk manifests
    print("📝 Creating agent manifests...")
    manifest_paths = create_chunk_manifests(all_files, num_agents, output_dir)
    print(f"   Created {len(manifest_paths)} manifests")
    print()

    # Generate launch commands
    print("🚀 Generating launch commands...")
    commands = generate_launch_commands(manifest_paths, db_paths, PROJECT_ROOT)
    print()

    # Print summary
    print("=" * 60)
    print("🎯 Ready for Parallel Processing")
    print("=" * 60)
    print(f"Total files: {len(all_files)}")
    print(f"Agents: {num_agents}")
    print(f"Avg files per agent: {len(all_files) // num_agents}")
    print()
    print("✅ Each agent has isolated database (no concurrent write conflicts)")
    print()
    print("Launch commands:")
    for i, cmd in enumerate(commands):
        print(f"\n  Agent {i}:")
        print(f"  {cmd}")
    print()
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
