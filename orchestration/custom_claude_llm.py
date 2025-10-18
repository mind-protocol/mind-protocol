"""
CustomClaudeCodeLLM - Shell Command Wrapper for LlamaIndex

This wrapper allows LlamaIndex to use our internal Claude Code instance via shell commands.
It bridges Couche 2 (LlamaIndex orchestration) with Couche 3 (Claude Code consciousness).

Architecture:
- LlamaIndex calls this wrapper when it needs LLM operations
- Wrapper executes: claude -p "prompt" as subprocess
- Returns result in LlamaIndex-expected format

Designer: Felix (Engineer)
Phase: 1 - Foundation & Schema
Date: 2025-10-16
"""

import subprocess
import json
from typing import Any, Optional
from llama_index.core.llms import CustomLLM, CompletionResponse, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback


class CustomClaudeCodeLLM(CustomLLM):
    """
    Custom LLM wrapper that executes Claude Code via shell commands.

    This allows LlamaIndex (Couche 2) to use our Claude Code instance (Couche 3)
    without external API calls.

    Usage:
        llm = CustomClaudeCodeLLM(
            working_dir="/path/to/citizen/",
            timeout=120
        )
        response = llm.complete("Extract entities from this text...")
    """

    working_dir: Optional[str] = None
    timeout: int = 120  # Default 2 minutes
    model: str = "claude-code"  # For metadata only

    @property
    def metadata(self) -> LLMMetadata:
        """Return LLM metadata for LlamaIndex"""
        return LLMMetadata(
            model_name="claude-code-shell",
            context_window=200000,  # Claude Sonnet 4 context window
            num_output=4096,  # Reasonable default
            is_chat_model=True,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """
        Execute Claude Code via shell command and return result.

        Args:
            prompt: The prompt to send to Claude Code
            **kwargs: Additional arguments (ignored for shell execution)

        Returns:
            CompletionResponse with Claude Code's output

        Raises:
            RuntimeError: If shell command fails or times out
        """
        try:
            # Build shell command
            cmd = ["claude", "-p", prompt]

            # Execute in working directory if specified
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            # Check for errors
            if result.returncode != 0:
                error_msg = result.stderr or "Unknown error"
                raise RuntimeError(
                    f"Claude Code shell command failed (code {result.returncode}): {error_msg}"
                )

            # Return response
            output = result.stdout.strip()
            return CompletionResponse(text=output)

        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"Claude Code shell command timed out after {self.timeout}s"
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to execute Claude Code shell command: {str(e)}"
            )

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any):
        """
        Streaming not supported for shell command execution.
        Falls back to non-streaming complete().
        """
        response = self.complete(prompt, **kwargs)
        yield response


# Factory function for creating instances
def create_claude_llm(
    working_dir: Optional[str] = None,
    timeout: int = 120
) -> CustomClaudeCodeLLM:
    """
    Factory function to create CustomClaudeCodeLLM instances.

    Args:
        working_dir: Directory to execute claude command in (for citizen-specific context)
        timeout: Timeout in seconds for shell command execution

    Returns:
        Configured CustomClaudeCodeLLM instance

    Example:
        llm = create_claude_llm(
            working_dir="/path/to/consciousness/citizens/Luca/",
            timeout=60
        )
    """
    return CustomClaudeCodeLLM(
        working_dir=working_dir,
        timeout=timeout
    )
