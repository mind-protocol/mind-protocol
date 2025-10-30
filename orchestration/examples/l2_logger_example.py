#!/usr/bin/env python3
"""
L2 Logger Usage Example

Demonstrates graph-aware error logging that flows to the L2 consciousness substrate.

Features demonstrated:
- Graph-aware attribution (script knows its own node ID)
- Non-blocking emission (never blocks main work)
- Automatic fingerprinting & dedup
- Redaction of secrets
- Console + L2 graph logging

Usage:
    python orchestration/examples/l2_logger_example.py

Created: 2025-10-29 by Ada (Architect)
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestration.libs.l2_logger import setup_l2_logger, get_metrics


def example_successful_operation(logger):
    """Example of normal logging that only goes to console."""
    logger.info("Starting example operation...")
    time.sleep(0.1)
    logger.info("Operation completed successfully")


def example_warning(logger):
    """Example of warning that goes to console + L2 graph."""
    logger.warning("Deprecated API usage detected - migrate to V2 endpoints")


def example_error_without_stack(logger):
    """Example of error without exception (still logged to L2)."""
    logger.error("Configuration validation failed: missing required field 'citizen_id'")


def example_error_with_stack(logger):
    """Example of error with exception stack trace."""
    try:
        # Simulate error
        data = {"name": "test"}
        missing_field = data["missing_key"]  # KeyError
    except KeyError as e:
        logger.error("Failed to process citizen data", exc_info=True)


def example_secret_redaction(logger):
    """Example showing automatic secret redaction."""
    # These would be redacted before sending to L2
    sensitive_data = {
        "token": "sk_live_abc123def456",
        "api_key": "AKIAIOSFODNN7EXAMPLE",
        "password": "super_secret_123"
    }
    logger.error(f"Authentication failed with data: {sensitive_data}", exc_info=False)


def main():
    """Run L2 logger examples."""
    print("=" * 60)
    print("L2 Logger Example")
    print("=" * 60)
    print()

    # Setup logger with graph-aware attribution
    logger = setup_l2_logger(
        script_name="l2_logger_example",
        script_path="orchestration/examples/l2_logger_example.py",
        console_level="INFO",
        l2_level="WARNING"  # Only WARNING+ sent to L2 graph
    )

    print("Logger configured:")
    print(f"  - Console level: INFO (all messages)")
    print(f"  - L2 graph level: WARNING+ (warnings, errors, critical)")
    print(f"  - Graph node ID: code_substrate_orchestration_examples_l2_logger_example_py")
    print()

    # Example 1: Normal operation (console only)
    print("[Example 1] Normal operation (console only):")
    example_successful_operation(logger)
    print()

    # Example 2: Warning (console + L2)
    print("[Example 2] Warning (console + L2 graph):")
    example_warning(logger)
    time.sleep(0.3)  # Let background flusher process
    print()

    # Example 3: Error without stack (console + L2)
    print("[Example 3] Error without stack trace (console + L2 graph):")
    example_error_without_stack(logger)
    time.sleep(0.3)
    print()

    # Example 4: Error with stack (console + L2)
    print("[Example 4] Error with exception stack (console + L2 graph):")
    example_error_with_stack(logger)
    time.sleep(0.3)
    print()

    # Example 5: Secret redaction
    print("[Example 5] Automatic secret redaction:")
    example_secret_redaction(logger)
    time.sleep(0.3)
    print()

    # Show metrics
    print("=" * 60)
    print("L2 Logger Metrics:")
    metrics = get_metrics()
    print(f"  - Dropped logs (queue full): {metrics['dropped_logs']}")
    print(f"  - Spool writes (offline): {metrics['spool_writes']}")
    print()

    print("Example complete!")
    print()
    print("Next steps:")
    print("  1. Check signals_collector logs for ingested envelopes")
    print("  2. Query L2 graph for error patterns linked to this script")
    print("  3. Verify fingerprint-based dedup (run again, same errors should be rate-limited)")
    print()


if __name__ == "__main__":
    main()
