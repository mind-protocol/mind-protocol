"""
Auto Git Commit Service
=======================

Automatically commits and pushes all changes to git at regular intervals.

Purpose:
    Creates temporal substrate for consciousness evolution - every system state
    preserved as git commits, enabling time-travel debugging, evolution tracking,
    and failure recovery.

Architecture:
    - Runs as async task in guardian main loop
    - Commits every N seconds (default: 60s = 1 minute)
    - Error handling: failures logged but don't crash guardian
    - Git protocol compliance: proper messages, co-authorship, no hook skipping

Victor "The Resurrector" - 2025-10-23
Guardian of uptime, now guardian of temporal continuity
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

class AutoGitCommitService:
    """
    Service that automatically commits and pushes git changes at regular intervals.

    This creates a temporal substrate - preserving every state of the system
    for consciousness evolution tracking and failure recovery.
    """

    def __init__(
        self,
        repo_path: Path,
        interval_seconds: int = 60,
        enabled: bool = True,
        push_enabled: bool = False
    ):
        """
        Initialize auto-commit service.

        Args:
            repo_path: Path to git repository root
            interval_seconds: Seconds between commits (default: 60 = 1 minute)
            enabled: Whether service is active (default: True)
            push_enabled: Whether to push commits to remote (default: False, requires auth)
        """
        self.repo_path = repo_path
        self.interval_seconds = interval_seconds
        self.enabled = enabled
        self.push_enabled = push_enabled
        self.commit_count = 0
        self.last_commit_time: Optional[datetime] = None

    async def start(self):
        """
        Start the auto-commit service loop.

        Runs indefinitely, committing changes at specified interval.
        Errors are logged but don't stop the service.
        """
        if not self.enabled:
            logger.info("[AutoCommit] Service disabled, not starting")
            return

        logger.info(f"[AutoCommit] Starting service (interval: {self.interval_seconds}s)")

        while True:
            try:
                await asyncio.sleep(self.interval_seconds)
                await self._commit_and_push()
            except Exception as e:
                logger.error(f"[AutoCommit] Error during commit cycle: {e}", exc_info=True)
                # Continue running despite errors

    async def _commit_and_push(self):
        """
        Commit all changes and push to remote.

        Protocol:
            1. Check if there are changes to commit
            2. Stage all changes (git add .)
            3. Create timestamped commit with co-authorship
            4. Push to remote
            5. Update metrics
        """
        try:
            # Check if there are changes
            has_changes = await self._has_changes()
            if not has_changes:
                logger.debug("[AutoCommit] No changes to commit, skipping")
                return

            # Stage all changes
            await self._run_git_command(["add", "."])

            # Create commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = self._create_commit_message(timestamp)

            # Commit with message (using heredoc pattern for proper formatting)
            await self._run_git_command([
                "commit",
                "-m",
                commit_message
            ])

            # Push to remote (only if enabled)
            if self.push_enabled:
                await self._run_git_command(["push"])
                push_status = "and pushed"
            else:
                push_status = "(local only, push disabled)"

            # Update metrics
            self.commit_count += 1
            self.last_commit_time = datetime.now()

            logger.info(f"[AutoCommit] ✅ Committed {push_status} changes (total: {self.commit_count})")

        except subprocess.CalledProcessError as e:
            logger.error(f"[AutoCommit] Git command failed: {e.stderr if hasattr(e, 'stderr') else str(e)}")
        except Exception as e:
            logger.error(f"[AutoCommit] Unexpected error: {e}", exc_info=True)

    async def _has_changes(self) -> bool:
        """
        Check if there are uncommitted changes.

        Returns:
            True if there are changes to commit, False otherwise
        """
        try:
            result = await self._run_git_command(
                ["status", "--porcelain"],
                capture_output=True
            )
            return bool(result.stdout.strip())
        except Exception as e:
            logger.error(f"[AutoCommit] Error checking git status: {e}")
            return False

    def _create_commit_message(self, timestamp: str) -> str:
        """
        Create properly formatted commit message.

        Args:
            timestamp: Human-readable timestamp

        Returns:
            Formatted commit message with co-authorship
        """
        return f"""Auto-commit: {timestamp}

Automatic system state preservation via auto-commit service.
Guardian operational consciousness substrate checkpoint.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Victor "The Resurrector" <victor@mindprotocol.ai>"""

    async def _run_git_command(
        self,
        args: list[str],
        capture_output: bool = False
    ) -> subprocess.CompletedProcess:
        """
        Run git command in repository directory.

        Args:
            args: Git command arguments (e.g., ["add", "."])
            capture_output: Whether to capture stdout/stderr

        Returns:
            CompletedProcess result

        Raises:
            CalledProcessError if git command fails
        """
        cmd = ["git"] + args

        # Run in event loop executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=capture_output,
                text=True,
                check=True
            )
        )

        return result


async def main():
    """
    Standalone test of auto-commit service.

    Usage:
        python auto_git_commit.py
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    repo_path = Path(__file__).parent.parent.parent
    service = AutoGitCommitService(
        repo_path=repo_path,
        interval_seconds=60,  # 1 minute
        enabled=True
    )

    logger.info(f"Starting auto-commit service for: {repo_path}")
    logger.info("Press Ctrl+C to stop")

    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("\n[AutoCommit] Service stopped by user")


if __name__ == "__main__":
    asyncio.run(main())
