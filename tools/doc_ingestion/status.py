"""
Processing Status Reporter

Operational reporting from SQLite state database.
Displays processing progress, QA task queue, and recent history.

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-29
Spec: docs/SPEC DOC INPUT.md
"""

import json
import sqlite3
import sys
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path


class StatusReporter:
    """
    Generates operational reports from SQLite state database.

    Provides both human-readable and JSON output formats.
    """

    def __init__(self, db_path: str = ".doc_ingestion_state.db"):
        """
        Initialize reporter.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path

        if not Path(db_path).exists():
            raise FileNotFoundError(f"State database not found: {db_path}")

    def get_processing_summary(self) -> Dict[str, Any]:
        """
        Get overall processing summary.

        Returns:
            Summary statistics dict
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Count by status
        cursor.execute("SELECT status, COUNT(*) FROM files GROUP BY status")
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # Aggregate statistics
        cursor.execute("""
        SELECT
            SUM(chunk_count) AS total_chunks,
            SUM(node_count) AS total_nodes,
            SUM(link_count) AS total_links
        FROM files
        WHERE status = 'completed'
        """)

        row = cursor.fetchone()
        total_chunks = row[0] or 0
        total_nodes = row[1] or 0
        total_links = row[2] or 0

        # QA tasks
        cursor.execute("SELECT COUNT(*) FROM qa_tasks WHERE resolved_at IS NULL")
        pending_qa = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM qa_tasks WHERE resolved_at IS NOT NULL")
        resolved_qa = cursor.fetchone()[0]

        # Recent activity
        cursor.execute("""
        SELECT last_processed_at
        FROM files
        WHERE last_processed_at IS NOT NULL
        ORDER BY last_processed_at DESC
        LIMIT 1
        """)
        row = cursor.fetchone()
        last_activity = row[0] if row else None

        conn.close()

        return {
            'by_status': status_counts,
            'total_chunks': total_chunks,
            'total_nodes': total_nodes,
            'total_links': total_links,
            'pending_qa_tasks': pending_qa,
            'resolved_qa_tasks': resolved_qa,
            'last_activity': last_activity
        }

    def get_failed_files(self) -> List[Dict[str, Any]]:
        """
        Get list of failed files with error messages.

        Returns:
            List of failed file records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT file_path, error_message, last_processed_at
        FROM files
        WHERE status = 'failed'
        ORDER BY last_processed_at DESC
        """)

        failed = [
            {
                'file_path': row[0],
                'error_message': row[1],
                'last_processed_at': row[2]
            }
            for row in cursor.fetchall()
        ]

        conn.close()
        return failed

    def get_pending_qa_tasks(self) -> List[Dict[str, Any]]:
        """
        Get pending QA tasks.

        Returns:
            List of QA task records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT task_id, file_path, task_type, description, created_at
        FROM qa_tasks
        WHERE resolved_at IS NULL
        ORDER BY created_at DESC
        LIMIT 20
        """)

        tasks = [
            {
                'task_id': row[0],
                'file_path': row[1],
                'task_type': row[2],
                'description': row[3],
                'created_at': row[4]
            }
            for row in cursor.fetchall()
        ]

        conn.close()
        return tasks

    def get_recent_processing_log(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent processing log entries.

        Args:
            limit: Maximum entries to return

        Returns:
            List of log entries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT log_id, file_path, timestamp, event_type, message, metadata
        FROM processing_log
        ORDER BY timestamp DESC
        LIMIT ?
        """, (limit,))

        logs = [
            {
                'log_id': row[0],
                'file_path': row[1],
                'timestamp': row[2],
                'event_type': row[3],
                'message': row[4],
                'metadata': json.loads(row[5]) if row[5] else None
            }
            for row in cursor.fetchall()
        ]

        conn.close()
        return logs

    def get_progress_percentage(self) -> float:
        """
        Calculate overall progress percentage.

        Returns:
            Progress as percentage (0-100)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM files")
        total = cursor.fetchone()[0]

        if total == 0:
            return 0.0

        cursor.execute("SELECT COUNT(*) FROM files WHERE status = 'completed'")
        completed = cursor.fetchone()[0]

        conn.close()

        return (completed / total) * 100

    def format_human_readable(self) -> str:
        """
        Format status as human-readable report.

        Returns:
            Multi-line string report
        """
        summary = self.get_processing_summary()
        failed = self.get_failed_files()
        qa_tasks = self.get_pending_qa_tasks()
        progress = self.get_progress_percentage()

        lines = ["=" * 60]
        lines.append("Doc Ingestion Pipeline - Processing Status")
        lines.append("=" * 60)
        lines.append("")

        # Progress
        lines.append(f"Overall Progress: {progress:.1f}%")
        lines.append("")

        # File counts by status
        lines.append("[File Status]")
        status_counts = summary['by_status']
        for status, count in sorted(status_counts.items()):
            icon = {
                'pending': '⏳',
                'processing': '🔄',
                'completed': '✅',
                'failed': '❌'
            }.get(status, '•')
            lines.append(f"  {icon} {status.capitalize():12} {count:5} files")
        lines.append("")

        # Aggregate statistics
        lines.append("[Completed Work]")
        lines.append(f"  Total chunks:    {summary['total_chunks']:5}")
        lines.append(f"  Total nodes:     {summary['total_nodes']:5}")
        lines.append(f"  Total links:     {summary['total_links']:5}")
        lines.append("")

        # QA tasks
        lines.append("[QA Tasks]")
        lines.append(f"  Pending:         {summary['pending_qa_tasks']:5}")
        lines.append(f"  Resolved:        {summary['resolved_qa_tasks']:5}")
        lines.append("")

        # Last activity
        if summary['last_activity']:
            lines.append(f"[Last Activity]")
            lines.append(f"  {summary['last_activity']}")
            lines.append("")

        # Failed files (if any)
        if failed:
            lines.append("[Failed Files]")
            for f in failed[:5]:  # Show first 5
                lines.append(f"  ❌ {f['file_path']}")
                lines.append(f"     {f['error_message'][:100]}")
            if len(failed) > 5:
                lines.append(f"  ... and {len(failed) - 5} more")
            lines.append("")

        # Pending QA tasks (if any)
        if qa_tasks:
            lines.append("[Pending QA Tasks]")
            for task in qa_tasks[:5]:  # Show first 5
                lines.append(f"  [{task['task_id']}] {task['task_type']}")
                lines.append(f"     {task['description'][:80]}")
                lines.append(f"     File: {task['file_path']}")
            if len(qa_tasks) > 5:
                lines.append(f"  ... and {len(qa_tasks) - 5} more")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    def format_json(self) -> str:
        """
        Format status as JSON for machine consumption.

        Returns:
            JSON string
        """
        summary = self.get_processing_summary()
        failed = self.get_failed_files()
        qa_tasks = self.get_pending_qa_tasks()
        progress = self.get_progress_percentage()
        recent_logs = self.get_recent_processing_log(limit=10)

        data = {
            'progress_percentage': progress,
            'summary': summary,
            'failed_files': failed,
            'pending_qa_tasks': qa_tasks,
            'recent_logs': recent_logs,
            'timestamp': datetime.utcnow().isoformat()
        }

        return json.dumps(data, indent=2)


def main():
    """CLI entrypoint."""
    import argparse

    parser = argparse.ArgumentParser(description='View processing status')
    parser.add_argument('--db', default='.doc_ingestion_state.db', help='Path to state database')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    try:
        reporter = StatusReporter(args.db)

        if args.json:
            print(reporter.format_json())
        else:
            print(reporter.format_human_readable())

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("\nNo processing has been run yet.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
