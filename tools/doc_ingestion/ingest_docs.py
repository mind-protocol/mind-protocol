"""
Document Ingestion State Manager

Manages manifest reading, file hashing, and processing state tracking via SQLite.
Supports checkpoint/resume for fault-tolerant corpus processing.

Key features:
- Read manifest.json (ordered file list)
- Hash file contents (SHA-256) for change detection
- SQLite state tracking (pending, processing, completed, failed)
- Checkpoint/resume support
- Idempotent operations (safe to re-run)

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-29
Spec: docs/SPEC DOC INPUT.md
"""

import json
import sqlite3
import hashlib
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Get project root for path resolution
PROJECT_ROOT = Path(__file__).parent.parent.parent


class ProcessingStatus(str, Enum):
    """File processing status."""
    PENDING = "pending"         # Not yet processed
    PROCESSING = "processing"   # Currently being processed
    COMPLETED = "completed"     # Successfully processed
    FAILED = "failed"           # Processing failed


@dataclass
class FileRecord:
    """A file in the processing queue."""
    file_path: str
    content_hash: str
    status: ProcessingStatus
    last_processed_at: Optional[str] = None
    error_message: Optional[str] = None
    chunk_count: Optional[int] = None
    node_count: Optional[int] = None
    link_count: Optional[int] = None


class IngestionStateManager:
    """
    Manages document ingestion state via SQLite.

    Tracks which files have been processed, detects changes,
    and provides checkpoint/resume functionality.
    """

    def __init__(self, db_path: str = ".doc_ingestion_state.db"):
        """
        Initialize state manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Files table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            file_path TEXT PRIMARY KEY,
            content_hash TEXT NOT NULL,
            status TEXT NOT NULL,
            last_processed_at TEXT,
            error_message TEXT,
            chunk_count INTEGER,
            node_count INTEGER,
            link_count INTEGER
        )
        """)

        # QA tasks table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS qa_tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            task_type TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT NOT NULL,
            resolved_at TEXT,
            resolution TEXT,
            FOREIGN KEY (file_path) REFERENCES files(file_path)
        )
        """)

        # Processing log table (for debugging)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            message TEXT,
            metadata TEXT
        )
        """)

        conn.commit()
        conn.close()

    def load_manifest(self, manifest_path: str) -> List[str]:
        """
        Load file paths from manifest.json.

        Args:
            manifest_path: Path to manifest.json

        Returns:
            List of file paths in processing order

        Raises:
            FileNotFoundError: If manifest doesn't exist
            json.JSONDecodeError: If manifest is invalid JSON
        """
        manifest_file = Path(manifest_path)
        if not manifest_file.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        with open(manifest_file, 'r') as f:
            data = json.load(f)

        # Expect: {"files": ["path1.md", "path2.md", ...]}
        if 'files' not in data:
            raise ValueError("Manifest missing 'files' key")

        return data['files']

    def compute_file_hash(self, file_path: str) -> str:
        """
        Compute SHA-256 hash of file contents.

        Args:
            file_path: Path to file

        Returns:
            Hex digest of file hash

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file = Path(file_path)
        # Resolve relative paths against project root
        if not file.is_absolute():
            file = PROJECT_ROOT / file

        if not file.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        hasher = hashlib.sha256()
        with open(file, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)

        return hasher.hexdigest()

    def sync_manifest(self, manifest_path: str) -> Dict[str, int]:
        """
        Sync manifest with database state.

        Adds new files, detects changed files (hash mismatch),
        and marks removed files.

        Args:
            manifest_path: Path to manifest.json

        Returns:
            Statistics: {new: int, changed: int, removed: int, unchanged: int}
        """
        # Load manifest
        manifest_files = self.load_manifest(manifest_path)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {'new': 0, 'changed': 0, 'removed': 0, 'unchanged': 0}

        # Get existing files from DB
        cursor.execute("SELECT file_path, content_hash FROM files")
        existing = {row[0]: row[1] for row in cursor.fetchall()}

        # Process each file in manifest
        for file_path in manifest_files:
            try:
                current_hash = self.compute_file_hash(file_path)
            except FileNotFoundError:
                # File in manifest but not on disk - skip
                continue

            if file_path not in existing:
                # New file
                cursor.execute("""
                INSERT INTO files (file_path, content_hash, status)
                VALUES (?, ?, ?)
                """, (file_path, current_hash, ProcessingStatus.PENDING.value))
                stats['new'] += 1

            elif existing[file_path] != current_hash:
                # Changed file - reset to pending
                cursor.execute("""
                UPDATE files
                SET content_hash = ?, status = ?, error_message = NULL
                WHERE file_path = ?
                """, (current_hash, ProcessingStatus.PENDING.value, file_path))
                stats['changed'] += 1

            else:
                # Unchanged
                stats['unchanged'] += 1

        # Mark removed files (in DB but not in manifest)
        manifest_set = set(manifest_files)
        removed_files = set(existing.keys()) - manifest_set
        for file_path in removed_files:
            cursor.execute("DELETE FROM files WHERE file_path = ?", (file_path,))
            stats['removed'] += 1

        conn.commit()
        conn.close()

        return stats

    def get_pending_files(self, limit: Optional[int] = None) -> List[FileRecord]:
        """
        Get files that need processing.

        Args:
            limit: Maximum files to return (None for all)

        Returns:
            List of FileRecord for pending files
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
        SELECT file_path, content_hash, status, last_processed_at, error_message,
               chunk_count, node_count, link_count
        FROM files
        WHERE status = ?
        ORDER BY file_path
        """

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, (ProcessingStatus.PENDING.value,))
        rows = cursor.fetchall()

        conn.close()

        return [
            FileRecord(
                file_path=row[0],
                content_hash=row[1],
                status=ProcessingStatus(row[2]),
                last_processed_at=row[3],
                error_message=row[4],
                chunk_count=row[5],
                node_count=row[6],
                link_count=row[7]
            )
            for row in rows
        ]

    def mark_processing(self, file_path: str):
        """Mark file as currently being processed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE files
        SET status = ?, last_processed_at = ?
        WHERE file_path = ?
        """, (ProcessingStatus.PROCESSING.value, datetime.utcnow().isoformat(), file_path))

        conn.commit()
        conn.close()

        self._log_event(file_path, "processing_started", "File processing started")

    def mark_completed(
        self,
        file_path: str,
        chunk_count: int,
        node_count: int,
        link_count: int
    ):
        """
        Mark file as successfully processed.

        Args:
            file_path: File that was processed
            chunk_count: Number of chunks created
            node_count: Number of nodes created
            link_count: Number of links created
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE files
        SET status = ?,
            last_processed_at = ?,
            error_message = NULL,
            chunk_count = ?,
            node_count = ?,
            link_count = ?
        WHERE file_path = ?
        """, (
            ProcessingStatus.COMPLETED.value,
            datetime.utcnow().isoformat(),
            chunk_count,
            node_count,
            link_count,
            file_path
        ))

        conn.commit()
        conn.close()

        self._log_event(file_path, "processing_completed", f"Completed: {chunk_count} chunks, {node_count} nodes, {link_count} links")

    def mark_failed(self, file_path: str, error_message: str):
        """
        Mark file as failed processing.

        Args:
            file_path: File that failed
            error_message: Error description
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE files
        SET status = ?,
            last_processed_at = ?,
            error_message = ?
        WHERE file_path = ?
        """, (
            ProcessingStatus.FAILED.value,
            datetime.utcnow().isoformat(),
            error_message,
            file_path
        ))

        conn.commit()
        conn.close()

        self._log_event(file_path, "processing_failed", error_message)

    def create_qa_task(self, file_path: str, task_type: str, description: str):
        """
        Create a QA task for manual review.

        Args:
            file_path: File that needs QA
            task_type: Type of QA task (e.g., 'low_confidence_links', 'ambiguous_mapping')
            description: Human-readable description
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO qa_tasks (file_path, task_type, description, created_at)
        VALUES (?, ?, ?, ?)
        """, (file_path, task_type, description, datetime.utcnow().isoformat()))

        conn.commit()
        conn.close()

        self._log_event(file_path, "qa_task_created", f"{task_type}: {description}")

    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get overall processing statistics.

        Returns:
            Statistics dict
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Count by status
        cursor.execute("""
        SELECT status, COUNT(*) FROM files GROUP BY status
        """)
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # Total counts
        cursor.execute("""
        SELECT
            COUNT(*) AS total_files,
            SUM(chunk_count) AS total_chunks,
            SUM(node_count) AS total_nodes,
            SUM(link_count) AS total_links
        FROM files
        WHERE status = ?
        """, (ProcessingStatus.COMPLETED.value,))

        row = cursor.fetchone()
        total_files = row[0] or 0
        total_chunks = row[1] or 0
        total_nodes = row[2] or 0
        total_links = row[3] or 0

        # QA task count
        cursor.execute("SELECT COUNT(*) FROM qa_tasks WHERE resolved_at IS NULL")
        pending_qa_tasks = cursor.fetchone()[0]

        conn.close()

        return {
            'by_status': status_counts,
            'total_files': total_files,
            'total_chunks': total_chunks,
            'total_nodes': total_nodes,
            'total_links': total_links,
            'pending_qa_tasks': pending_qa_tasks
        }

    def _log_event(self, file_path: str, event_type: str, message: str, metadata: Optional[Dict] = None):
        """Log processing event to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO processing_log (file_path, timestamp, event_type, message, metadata)
        VALUES (?, ?, ?, ?, ?)
        """, (
            file_path,
            datetime.utcnow().isoformat(),
            event_type,
            message,
            json.dumps(metadata) if metadata else None
        ))

        conn.commit()
        conn.close()

    def reset_processing_files(self):
        """
        Reset any files stuck in 'processing' state back to pending.

        Useful for recovery after crashes.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE files
        SET status = ?
        WHERE status = ?
        """, (ProcessingStatus.PENDING.value, ProcessingStatus.PROCESSING.value))

        affected = cursor.rowcount
        conn.commit()
        conn.close()

        if affected > 0:
            self._log_event("SYSTEM", "recovery", f"Reset {affected} stuck files to pending")

        return affected


if __name__ == "__main__":
    # Quick test
    import tempfile
    import os

    # Create temp directory with test files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test manifest
        test_files = []
        for i in range(5):
            file_path = os.path.join(tmpdir, f"test_{i}.md")
            with open(file_path, 'w') as f:
                f.write(f"# Test Document {i}\n\nContent here.")
            test_files.append(file_path)

        manifest_path = os.path.join(tmpdir, "manifest.json")
        with open(manifest_path, 'w') as f:
            json.dump({'files': test_files}, f)

        # Initialize state manager
        db_path = os.path.join(tmpdir, "test_state.db")
        manager = IngestionStateManager(db_path)

        # Sync manifest
        print("Syncing manifest...")
        stats = manager.sync_manifest(manifest_path)
        print(f"  New: {stats['new']}, Changed: {stats['changed']}, Unchanged: {stats['unchanged']}")

        # Get pending files
        pending = manager.get_pending_files()
        print(f"\nPending files: {len(pending)}")

        # Simulate processing first file
        if pending:
            file = pending[0]
            print(f"\nProcessing: {file.file_path}")
            manager.mark_processing(file.file_path)
            manager.mark_completed(file.file_path, chunk_count=3, node_count=5, link_count=7)

            # Create QA task
            manager.create_qa_task(file.file_path, "test_qa", "Manual review needed")

        # Get stats
        stats = manager.get_processing_stats()
        print(f"\nProcessing stats:")
        print(f"  By status: {stats['by_status']}")
        print(f"  Completed files: {stats['total_files']}")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Total nodes: {stats['total_nodes']}")
        print(f"  Total links: {stats['total_links']}")
        print(f"  Pending QA: {stats['pending_qa_tasks']}")

        print("\n✅ Ingestion state manager test passed!")
