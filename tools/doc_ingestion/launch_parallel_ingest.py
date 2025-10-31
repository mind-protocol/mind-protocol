#!/usr/bin/env python3
"""
Launch Parallel Document Ingestion (2 Agents)

Launches 2 parallel ingestors with proper file dispatch to isolated databases.

Usage:
    python launch_parallel_ingest.py --manifest path/to/manifest.json

Author: Ada (Architect)
Date: 2025-10-30
"""

import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import time

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.doc_ingestion.ingest_docs import IngestionStateManager


def get_all_files_from_manifest(manifest_path: str) -> List[str]:
    """
    Get all files from manifest.

    Returns:
        List of file paths
    """
    with open(manifest_path, 'r') as f:
        manifest_data = json.load(f)

    # Support both formats: {"files": [...]} or {"processing_order": [...]}
    if 'files' in manifest_data:
        return manifest_data['files']
    elif 'processing_order' in manifest_data:
        return [entry['path'] for entry in manifest_data['processing_order']]
    else:
        raise ValueError("Manifest must have 'files' or 'processing_order' key")


def create_agent_databases(
    all_files: List[str],
    num_agents: int,
    db_dir: Path
) -> List[Path]:
    """
    Create isolated database for each agent with its file subset.

    Args:
        all_files: All file paths from manifest
        num_agents: Number of parallel agents (2)
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

    print(f"\n📊 Dispatching {len(all_files)} files to {num_agents} agents:")

    for agent_id in range(num_agents):
        # Calculate chunk size (distribute remainder across first agents)
        current_chunk_size = chunk_size + (1 if agent_id < remainder else 0)
        end_idx = start_idx + current_chunk_size

        # Extract chunk
        chunk = all_files[start_idx:end_idx]

        print(f"  Agent {agent_id}: {len(chunk)} files (indices {start_idx}-{end_idx-1})")

        # Create agent-specific database
        db_path = db_dir / f".doc_ingestion_state_agent{agent_id}.db"

        # Initialize state manager with agent's database
        manager = IngestionStateManager(str(db_path))

        # Create temporary manifest for this agent's files
        temp_manifest = {
            "files": chunk
        }
        temp_manifest_path = db_dir / f"temp_manifest_agent{agent_id}.json"
        with open(temp_manifest_path, 'w') as f:
            json.dump(temp_manifest, f, indent=2)

        # Sync to populate database
        stats = manager.sync_manifest(str(temp_manifest_path))

        print(f"    ✓ Database initialized: {db_path.name}")
        print(f"    ✓ New files: {stats['new']}, Changed: {stats['changed']}")

        # Keep temp manifest for agent to use
        # (Don't delete - agents will read it)

        db_paths.append(db_path)
        start_idx = end_idx

    return db_paths


def launch_agents(
    db_paths: List[Path],
    manifest_dir: Path,
    repo_root: Path,
    config_path: str
) -> List[subprocess.Popen]:
    """
    Launch parallel agent processes.

    Args:
        db_paths: List of agent database paths
        manifest_dir: Directory containing temp manifests
        repo_root: Repository root path
        config_path: Path to config.toml

    Returns:
        List of subprocess.Popen objects
    """
    processes = []

    print(f"\n🚀 Launching {len(db_paths)} parallel agents:")

    for agent_id, db_path in enumerate(db_paths):
        # Find temp manifest for this agent
        temp_manifest = manifest_dir / f"temp_manifest_agent{agent_id}.json"

        # Construct command (positional manifest arg only)
        cmd = [
            sys.executable,
            str(repo_root / "tools" / "doc_ingestion" / "process_corpus.py"),
            str(temp_manifest)
        ]

        # Set environment variable for database path override
        import os
        env = os.environ.copy()
        env['DOC_INGEST_STATE_DB_PATH'] = str(db_path)

        # Launch process
        log_file = manifest_dir / f"agent{agent_id}_output.log"
        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                cmd,
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=str(repo_root),
                env=env  # Pass environment with database override
            )

        print(f"  Agent {agent_id}:")
        print(f"    - PID: {process.pid}")
        print(f"    - Database: {db_path.name}")
        print(f"    - Log: {log_file.name}")

        processes.append(process)

    return processes


def monitor_agents(processes: List[subprocess.Popen], db_paths: List[Path]):
    """
    Monitor agent processes and display progress.

    Args:
        processes: List of agent processes
        db_paths: List of agent database paths
    """
    print(f"\n📊 Monitoring {len(processes)} agents (Ctrl+C to stop):")
    print(f"{'Agent':<8} {'Status':<12} {'Completed':<12} {'Failed':<10} {'Total':<10}")
    print("-" * 60)

    try:
        while True:
            all_done = True

            for agent_id, (process, db_path) in enumerate(zip(processes, db_paths)):
                # Check if process is still running
                poll_result = process.poll()

                if poll_result is None:
                    status = "Running"
                    all_done = False
                elif poll_result == 0:
                    status = "Done ✓"
                else:
                    status = f"Failed ({poll_result})"

                # Get stats from database
                try:
                    manager = IngestionStateManager(str(db_path))
                    stats = manager.get_processing_stats()
                    completed = stats['completed']
                    failed = stats['failed']
                    total = stats['total']
                except Exception:
                    completed = "?"
                    failed = "?"
                    total = "?"

                print(f"Agent {agent_id:<4} {status:<12} {completed:<12} {failed:<10} {total:<10}")

            if all_done:
                print("\n✅ All agents completed")
                break

            print("\033[F" * (len(processes) + 1))  # Move cursor up
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted - stopping agents...")
        for process in processes:
            process.terminate()
        time.sleep(2)
        for process in processes:
            if process.poll() is None:
                process.kill()
        print("✓ All agents stopped")


def main():
    parser = argparse.ArgumentParser(description='Launch parallel document ingestion (2 agents)')
    parser.add_argument('--manifest', required=True, help='Path to manifest.json')
    parser.add_argument('--config', default='config.toml', help='Path to config.toml')
    parser.add_argument('--db-dir', default='.parallel_ingest', help='Directory for agent databases')

    args = parser.parse_args()

    # Resolve paths
    repo_root = PROJECT_ROOT
    manifest_path = Path(args.manifest).resolve()
    db_dir = Path(args.db_dir).resolve()
    config_path = args.config

    print("=" * 60)
    print("PARALLEL DOCUMENT INGESTION (2 AGENTS)")
    print("=" * 60)
    print(f"Manifest: {manifest_path}")
    print(f"Database directory: {db_dir}")
    print(f"Config: {config_path}")

    # Step 1: Load manifest
    print(f"\n📄 Loading manifest...")
    try:
        all_files = get_all_files_from_manifest(str(manifest_path))
        print(f"  ✓ Found {len(all_files)} files")
    except Exception as e:
        print(f"  ✗ Error loading manifest: {e}")
        sys.exit(1)

    # Step 2: Create agent databases with file dispatch
    print(f"\n💾 Creating agent databases...")
    try:
        db_paths = create_agent_databases(all_files, num_agents=2, db_dir=db_dir)
        print(f"  ✓ {len(db_paths)} databases ready")
    except Exception as e:
        print(f"  ✗ Error creating databases: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 3: Launch agents
    try:
        processes = launch_agents(db_paths, db_dir, repo_root, config_path)
    except Exception as e:
        print(f"  ✗ Error launching agents: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 4: Monitor agents
    monitor_agents(processes, db_paths)

    # Step 5: Aggregate results
    print("\n📊 Final Statistics:")
    print("-" * 60)

    total_completed = 0
    total_failed = 0
    total_files = 0

    for agent_id, db_path in enumerate(db_paths):
        manager = IngestionStateManager(str(db_path))
        stats = manager.get_processing_stats()

        print(f"Agent {agent_id}:")
        print(f"  - Completed: {stats['completed']}")
        print(f"  - Failed: {stats['failed']}")
        print(f"  - Total: {stats['total']}")

        total_completed += stats['completed']
        total_failed += stats['failed']
        total_files += stats['total']

    print("-" * 60)
    print(f"Overall:")
    print(f"  - Completed: {total_completed}/{total_files}")
    print(f"  - Failed: {total_failed}/{total_files}")
    print(f"  - Success rate: {(total_completed/total_files*100):.1f}%")

    print("\n✅ Parallel ingestion complete")
    print(f"Logs available in: {db_dir}")


if __name__ == "__main__":
    main()
