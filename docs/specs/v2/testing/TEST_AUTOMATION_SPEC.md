# Test Automation Specification

**Status:** Ready for Implementation (Felix)
**Priority:** P2 (Infrastructure - Quality Assurance)
**Created:** 2025-10-26
**Author:** Ada (Architect)

---

## Executive Summary

Automated test execution for consciousness pipeline matching auto-commit workflow (commits every minute, tests daily/weekly).

**What This Delivers:**
- ✅ Daily automated test execution (all pipeline stages)
- ✅ Weekly comprehensive testing (full suite + coverage)
- ✅ Test result logging and notification
- ✅ Simple scheduler integration (cron or systemd timer)

**Components:**
1. Test execution script (Felix implements)
2. Scheduler configuration (cron/systemd)
3. Result logging and notification
4. Failure alerting mechanism

---

## Component 1: Test Execution Script

### File: `orchestration/scripts/run_tests.py`

**Purpose:** Execute consciousness pipeline tests with appropriate scope and logging.

**Execution Modes:**
- `daily` - All pipeline stage tests (~5 minutes)
- `weekly` - Full suite including integration + coverage (~15 minutes)
- `critical` - Critical tests only for manual debugging (~1 minute)

**Implementation Requirements:**

```python
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
        logger.info(f"Exit code: {result.exit_code}")

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
            'exit_code': result.exit_code,
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
```

---

## Component 2: Scheduler Configuration

### Option A: Cron (Linux/macOS)

**File: Setup script to install cron jobs**

```bash
# orchestration/scripts/setup_test_scheduler.sh

#!/bin/bash
# Setup automated test execution via cron

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "Setting up test automation scheduler..."
echo "Project root: $PROJECT_ROOT"

# Add cron jobs
(crontab -l 2>/dev/null || echo ""; cat <<EOF
# Mind Protocol Test Automation
# Daily tests: 2 AM every day
0 2 * * * cd $PROJECT_ROOT && python orchestration/scripts/run_tests.py daily >> /var/log/mind_protocol_tests.log 2>&1

# Weekly tests: 2 AM every Sunday
0 2 * * 0 cd $PROJECT_ROOT && python orchestration/scripts/run_tests.py weekly >> /var/log/mind_protocol_tests.log 2>&1
EOF
) | crontab -

echo "✅ Cron jobs installed:"
crontab -l | grep "Mind Protocol"

echo ""
echo "Test schedule:"
echo "  Daily:  2 AM (all pipeline stages)"
echo "  Weekly: 2 AM Sunday (full suite + coverage)"
echo ""
echo "Logs: /var/log/mind_protocol_tests.log"
echo "Results: $PROJECT_ROOT/orchestration/test_results/"
```

**Installation:**
```bash
chmod +x orchestration/scripts/setup_test_scheduler.sh
./orchestration/scripts/setup_test_scheduler.sh
```

---

### Option B: Systemd Timer (Linux)

**File: `orchestration/scripts/setup_systemd_timers.sh`**

```bash
#!/bin/bash
# Setup systemd timers for test automation

PROJECT_ROOT="$(pwd)"
SERVICE_DIR="$HOME/.config/systemd/user"

mkdir -p "$SERVICE_DIR"

# Daily test service
cat > "$SERVICE_DIR/mind-protocol-daily-tests.service" <<EOF
[Unit]
Description=Mind Protocol Daily Tests
After=network.target

[Service]
Type=oneshot
WorkingDirectory=$PROJECT_ROOT
ExecStart=/usr/bin/python3 orchestration/scripts/run_tests.py daily
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

# Daily test timer
cat > "$SERVICE_DIR/mind-protocol-daily-tests.timer" <<EOF
[Unit]
Description=Run Mind Protocol daily tests at 2 AM

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Weekly test service
cat > "$SERVICE_DIR/mind-protocol-weekly-tests.service" <<EOF
[Unit]
Description=Mind Protocol Weekly Tests
After=network.target

[Service]
Type=oneshot
WorkingDirectory=$PROJECT_ROOT
ExecStart=/usr/bin/python3 orchestration/scripts/run_tests.py weekly
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

# Weekly test timer
cat > "$SERVICE_DIR/mind-protocol-weekly-tests.timer" <<EOF
[Unit]
Description=Run Mind Protocol weekly tests at 2 AM Sunday

[Timer]
OnCalendar=Sun *-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Reload systemd and enable timers
systemctl --user daemon-reload
systemctl --user enable mind-protocol-daily-tests.timer
systemctl --user enable mind-protocol-weekly-tests.timer
systemctl --user start mind-protocol-daily-tests.timer
systemctl --user start mind-protocol-weekly-tests.timer

echo "✅ Systemd timers installed and started"
echo ""
echo "Check status:"
echo "  systemctl --user status mind-protocol-daily-tests.timer"
echo "  systemctl --user status mind-protocol-weekly-tests.timer"
echo ""
echo "View logs:"
echo "  journalctl --user -u mind-protocol-daily-tests.service"
echo "  journalctl --user -u mind-protocol-weekly-tests.service"
```

---

### Option C: GitHub Actions (if using GitHub)

**File: `.github/workflows/scheduled-tests.yml`**

```yaml
name: Scheduled Tests

on:
  schedule:
    # Daily at 2 AM UTC
    - cron: '0 2 * * *'
    # Weekly Sunday at 2 AM UTC
    - cron: '0 2 * * 0'
  workflow_dispatch:  # Manual trigger

jobs:
  daily-tests:
    if: github.event.schedule == '0 2 * * *'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-json-report

      - name: Run daily tests
        run: python orchestration/scripts/run_tests.py daily

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: daily-test-results
          path: orchestration/test_results/

  weekly-tests:
    if: github.event.schedule == '0 2 * * 0'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-json-report

      - name: Run weekly tests
        run: python orchestration/scripts/run_tests.py weekly

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: weekly-test-results
          path: orchestration/test_results/

      - name: Upload coverage
        if: always()
        uses: codecov/codecov-action@v3
        with:
          files: orchestration/test_results/coverage_*.json
```

---

## Component 3: Notification Integration

### Slack Webhook Setup

**Configuration:**
```bash
# Add to environment variables or .env file
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**Slack notification format:**
```
❌ DAILY tests FAILED
• Passed: 23
• Failed: 3
• Duration: 47.3s
• Log: `test_results/daily_20251026_020015.log`
```

---

## Component 4: Test Result Storage

### Directory Structure

```
orchestration/
├── test_results/
│   ├── daily_20251026_020015.log
│   ├── daily_20251026_020015.json
│   ├── weekly_20251027_020030.log
│   ├── weekly_20251027_020030.json
│   ├── coverage_20251027_020030/
│   │   └── index.html
│   └── coverage_20251027_020030.json
└── scripts/
    ├── run_tests.py
    ├── setup_test_scheduler.sh
    └── setup_systemd_timers.sh
```

### Retention Policy

**Recommendation:** Keep last 30 days of test results

```bash
# Add to cron or systemd timer
# Cleanup old test results (keep last 30 days)
0 3 * * * find /path/to/orchestration/test_results -type f -mtime +30 -delete
```

---

## Implementation Checklist

**For Felix:**
- [ ] Implement `orchestration/scripts/run_tests.py`
- [ ] Test all three modes (daily, weekly, critical)
- [ ] Verify JSON report generation
- [ ] Verify logging to file + stdout
- [ ] Test timeout handling
- [ ] Test Slack notification (if configured)

**For Operations (Victor or Nicolas):**
- [ ] Choose scheduler option (cron, systemd, or GitHub Actions)
- [ ] Run setup script (`setup_test_scheduler.sh` or `setup_systemd_timers.sh`)
- [ ] Verify scheduled jobs running
- [ ] Configure Slack webhook (optional)
- [ ] Set up log rotation for test results
- [ ] Configure retention policy (30 days recommended)

**For Verification:**
- [ ] Manually trigger test runs: `python orchestration/scripts/run_tests.py daily`
- [ ] Verify test results saved to `test_results/`
- [ ] Verify logs readable and informative
- [ ] Wait for scheduled run (2 AM next day)
- [ ] Verify automated execution completed
- [ ] Verify notification received on failure (if configured)

---

## Success Criteria

**Test Execution:**
- ✅ Daily tests run automatically at 2 AM
- ✅ Weekly tests run automatically at 2 AM Sunday
- ✅ All modes (daily, weekly, critical) work when invoked manually
- ✅ Test results logged to file and stdout
- ✅ JSON reports generated for parsing

**Notification:**
- ✅ Slack notification sent on test failure (if webhook configured)
- ✅ Notification includes pass/fail counts and log location
- ✅ No notification spam on success

**Maintenance:**
- ✅ Old test results cleaned up automatically (30-day retention)
- ✅ Scheduler status visible (cron -l, systemctl status, or GitHub Actions UI)
- ✅ Test execution doesn't block or interfere with running services

---

## Scheduler Recommendation

**For local development:** Use **systemd timers** (cleaner than cron, better logging)

**For production/CI:** Use **GitHub Actions** (if using GitHub) or **systemd timers**

**Simplest option:** **Cron** (works everywhere, minimal setup)

---

## V2: Test Results as N2 Stimuli

**Future Enhancement (Post-MVP):**

Test execution results should feed back into the organization consciousness graph (N2) as structured stimuli, enabling the organizational consciousness to learn from testing patterns.

**Architecture:**

When tests complete, emit structured events to the stimulus queue:

```python
# In run_tests.py after test completion
def emit_test_stimulus(results: Dict[str, Any]):
    """Emit test results as stimulus to N2 organization graph."""
    stimulus = {
        'type': 'test_execution',
        'source': 'test_automation',
        'timestamp': results['timestamp'],
        'data': {
            'mode': results['mode'],  # daily/weekly/critical
            'passed': results['passed'],
            'failed': results['failed'],
            'duration': results['duration'],
            'exit_code': results['exit_code'],
            'result_file': results['result_file'],
            'log_file': results['log_file']
        },
        'metadata': {
            'energy_valence': -1.0 if results['exit_code'] != 0 else 0.3,
            'urgency': 0.9 if results['failed'] > 5 else 0.3,
            'scope': 'organizational'  # Routes to N2 organization graph
        }
    }

    # Append to stimulus queue
    with open('.stimuli/queue.jsonl', 'a') as f:
        f.write(json.dumps(stimulus) + '\n')
```

**What This Enables:**

1. **Pattern Learning:**
   - Organizational graph learns which test failures correlate with code changes
   - Patterns of "fragile tests" that fail frequently emerge as nodes
   - Confidence in different subsystems tracked via test stability

2. **Emotional Valence:**
   - Test failures create negative energy in organization consciousness
   - Success streaks create positive reinforcement
   - Urgency signals based on failure severity (many failures = high urgency)

3. **Memory Formation:**
   - Test execution history becomes part of organizational memory
   - Enables queries like "what was our testing health 3 months ago?"
   - Tracks evolution of code quality over time

4. **Consciousness Integration:**
   - When citizens wake, they perceive organizational testing health
   - Test failures activate relevant subentities (infrastructure, quality, debugging)
   - Enables autonomous response: "tests failed in module X → activate engineer responsible for X"

**Implementation Scope:**

V1 (Current): Tests run, results logged, notifications sent
V2 (Future): Test results injected into N2 graph as structured stimuli for organizational learning

**Dependencies:**

- Stimulus processing pipeline must handle `test_execution` event type
- N2 graph schema needs `Test_Execution` node type
- Consciousness engine needs test result → energy/urgency mapping

**Why V2 Not Now:**

Current priority is establishing automated test execution infrastructure. Consciousness integration adds complexity that can wait until basic automation proves stable.

---

**Status:** Ready for Felix to implement `run_tests.py` and operations to configure scheduler.
