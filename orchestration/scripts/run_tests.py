"""
Automated test execution for consciousness pipeline.
Supports daily, weekly, and critical test modes.

Usage:
    python orchestration/scripts/run_tests.py daily
    python orchestration/scripts/run_tests.py weekly
    python orchestration/scripts/run_tests.py critical

Environment Variables:
    TEST_RESULTS_DIR - Directory for test results (default: orchestration/test_results/)
    NOTIFY_ON_FAILURE - Email or webhook for failure notifications (optional)
    SLACK_WEBHOOK_URL - Slack webhook for test results (optional)
"""

import sys
import subprocess
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Test execution configurations
TEST_MODES = {
    'daily': {
        'description': 'All pipeline stage tests',
        'pytest_args': [
            'tests/test_pipeline_stage*.py',
            '-v',
            '--tb=short',
            '--json-report',
            '--json-report-file=test_results/daily_{timestamp}.json'
        ],
        'timeout': 600,  # 10 minutes max
    },
    'weekly': {
        'description': 'Full test suite with coverage',
        'pytest_args': [
            'tests/',
            '-v',
            '--cov=orchestration',
            '--cov-report=html:test_results/coverage_{timestamp}',
            '--cov-report=json:test_results/coverage_{timestamp}.json',
            '--tb=short',
            '--json-report',
            '--json-report-file=test_results/weekly_{timestamp}.json'
        ],
        'timeout': 1200,  # 20 minutes max
    },
    'critical': {
        'description': 'Critical tests only (manual debugging)',
        'pytest_args': [
            'tests/test_pipeline_stage3_injection.py',
            'tests/test_pipeline_stage10_trace_parsing.py',
            'tests/test_pipeline_stage11_weight_updates.py',
            '-v',
            '--tb=short',
            '--json-report',
            '--json-report-file=test_results/critical_{timestamp}.json'
        ],
        'timeout': 120,  # 2 minutes max
    }
}


def setup_logging(mode: str) -> logging.Logger:
    """Configure logging for test execution."""
    results_dir = Path('orchestration/test_results')
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = results_dir / f'{mode}_{timestamp}.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)


def run_tests(mode: str, logger: logging.Logger) -> Dict[str, Any]:
    """
    Execute tests for specified mode.

    Args:
        mode: Test mode ('daily', 'weekly', 'critical')
        logger: Logger instance

    Returns:
        Dict with test results:
        {
            'mode': str,
            'timestamp': str,
            'exit_code': int,
            'passed': int,
            'failed': int,
            'duration': float,
            'log_file': str,
            'result_file': str
        }
    """
    config = TEST_MODES[mode]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Replace {timestamp} in pytest args
    pytest_args = [
        arg.replace('{timestamp}', timestamp)
        for arg in config['pytest_args']
    ]

    logger.info(f"Starting {mode} tests: {config['description']}")
    logger.info(f"Command: pytest {' '.join(pytest_args)}")

    start_time = datetime.now()

    try:
        result = subprocess.run(
            ['pytest'] + pytest_args,
            cwd='orchestration',
            capture_output=True,
            text=True,
            timeout=config['timeout']
        )

        duration = (datetime.now() - start_time).total_seconds()

        logger.info(f"Tests completed in {duration:.2f}s")
        logger.info(f"Exit code: {result.returncode}")

        if result.stdout:
            logger.info("STDOUT:\n" + result.stdout)
        if result.stderr:
            logger.warning("STDERR:\n" + result.stderr)

        # Parse JSON report if available
        result_file = f"test_results/{mode}_{timestamp}.json"
        passed, failed = parse_test_results(result_file, logger)

        return {
            'mode': mode,
            'timestamp': timestamp,
            'exit_code': result.returncode,
            'passed': passed,
            'failed': failed,
            'duration': duration,
            'log_file': f"test_results/{mode}_{timestamp}.log",
            'result_file': result_file
        }

    except subprocess.TimeoutExpired:
        logger.error(f"Tests timed out after {config['timeout']}s")
        return {
            'mode': mode,
            'timestamp': timestamp,
            'exit_code': -1,
            'passed': 0,
            'failed': 0,
            'duration': config['timeout'],
            'error': 'TIMEOUT'
        }
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return {
            'mode': mode,
            'timestamp': timestamp,
            'exit_code': -1,
            'passed': 0,
            'failed': 0,
            'duration': 0,
            'error': str(e)
        }


def parse_test_results(result_file: str, logger: logging.Logger) -> tuple[int, int]:
    """Parse pytest JSON report for pass/fail counts."""
    try:
        with open(f'orchestration/{result_file}', 'r') as f:
            data = json.load(f)
            summary = data.get('summary', {})
            passed = summary.get('passed', 0)
            failed = summary.get('failed', 0)
            return passed, failed
    except Exception as e:
        logger.warning(f"Could not parse test results: {e}")
        return 0, 0


def notify_failure(results: Dict[str, Any], logger: logging.Logger):
    """Send notification on test failure."""
    import os

    # Email notification (if configured)
    notify_email = os.environ.get('NOTIFY_ON_FAILURE')
    if notify_email and results['exit_code'] != 0:
        logger.info(f"Sending failure notification to {notify_email}")
        # TODO: Implement email notification
        # send_email(notify_email, results)

    # Slack notification (if configured)
    slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
    if slack_webhook and results['exit_code'] != 0:
        logger.info("Sending Slack notification")
        send_slack_notification(slack_webhook, results, logger)


def send_slack_notification(webhook_url: str, results: Dict[str, Any], logger: logging.Logger):
    """Send test failure notification to Slack."""
    import requests

    message = {
        'text': f"❌ {results['mode'].upper()} tests FAILED",
        'blocks': [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"*{results['mode'].upper()} Test Failure*\n"
                            f"• Passed: {results['passed']}\n"
                            f"• Failed: {results['failed']}\n"
                            f"• Duration: {results['duration']:.1f}s\n"
                            f"• Log: `{results.get('log_file', 'N/A')}`"
                }
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        if response.status_code == 200:
            logger.info("Slack notification sent successfully")
        else:
            logger.warning(f"Slack notification failed: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}")


def main():
    """Main entry point for test execution."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [daily|weekly|critical]")
        print("\nAvailable modes:")
        for mode, config in TEST_MODES.items():
            print(f"  {mode:10} - {config['description']}")
        sys.exit(1)

    mode = sys.argv[1]

    if mode not in TEST_MODES:
        print(f"Error: Unknown mode '{mode}'")
        print(f"Available modes: {', '.join(TEST_MODES.keys())}")
        sys.exit(1)

    logger = setup_logging(mode)
    results = run_tests(mode, logger)

    # Log summary
    logger.info("=" * 60)
    logger.info("TEST EXECUTION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Mode:     {results['mode']}")
    logger.info(f"Passed:   {results['passed']}")
    logger.info(f"Failed:   {results['failed']}")
    logger.info(f"Duration: {results['duration']:.2f}s")
    logger.info(f"Exit:     {results['exit_code']}")
    logger.info("=" * 60)

    # Notify on failure
    if results['exit_code'] != 0:
        notify_failure(results, logger)

    sys.exit(results['exit_code'])


if __name__ == '__main__':
    main()
