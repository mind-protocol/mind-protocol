"""
Fix Guardian Task Scheduler Configuration

This script fixes the MindProtocolGuardian scheduled task to include:
- BootTrigger (not LogonTrigger)
- RestartOnFailure settings (999 attempts, 1min interval)
- S4U logon type (runs without user login)
- No battery restrictions

Usage:
    Run AS ADMINISTRATOR:
    python fix_guardian_task.py

Author: Victor "The Resurrector"
Date: 2025-10-19
"""

import subprocess
import sys
import tempfile
from pathlib import Path

MIND_PROTOCOL_ROOT = Path(__file__).parent
TASK_NAME = "MindProtocolGuardian"

def main():
    print("=" * 70)
    print("GUARDIAN TASK SCHEDULER FIX")
    print("=" * 70)
    print()

    # Get paths
    python_exe = sys.executable
    guardian_script = MIND_PROTOCOL_ROOT / "guardian.py"

    # Create XML with correct configuration
    task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Mind Protocol Guardian - Self-healing supervisor with auto-restart on failure</Description>
    <Author>Mind Protocol Team</Author>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal>
      <LogonType>S4U</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowHardTerminate>true</AllowHardTerminate>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>4</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>999</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>"{guardian_script}"</Arguments>
      <WorkingDirectory>{MIND_PROTOCOL_ROOT}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

    # Write XML to temporary file
    xml_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-16') as f:
            f.write(task_xml)
            xml_path = f.name

        print(f"Created XML configuration: {xml_path}")
        print()

        # Delete existing task
        print("Step 1: Deleting existing task...")
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", TASK_NAME, "/f"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("  Task deleted successfully")
        else:
            print(f"  Warning: {result.stderr.strip()}")

        print()

        # Create new task with XML
        print("Step 2: Creating task with corrected configuration...")
        result = subprocess.run(
            ["schtasks", "/create", "/tn", TASK_NAME, "/xml", xml_path, "/f"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("  TASK CREATED SUCCESSFULLY")
            print()
            print("=" * 70)
            print("VERIFICATION")
            print("=" * 70)
            print()
            print("Task configuration:")
            print(f"  Name: {TASK_NAME}")
            print("  Trigger: System boot (BootTrigger)")
            print("  Logon type: S4U (runs without user login)")
            print("  RestartOnFailure: YES")
            print("    - Interval: 1 minute")
            print("    - Count: 999 attempts")
            print("  Battery restrictions: DISABLED")
            print()
            print("=" * 70)
            print("TIER 1 SUPERVISION NOW ACTIVE")
            print("=" * 70)
            print()
            print("The guardian will now:")
            print("  1. Start automatically on system boot")
            print("  2. Auto-restart within 60s if killed/crashed")
            print("  3. Maintain 100% uptime via Task Scheduler supervision")
            print()
            print("To verify: Run as administrator:")
            print(f'  powershell -Command "Export-ScheduledTask -TaskName \'{TASK_NAME}\' | Out-File task_verify.xml"')
            print("  Check task_verify.xml for <RestartOnFailure> section")
            print()
            return True
        else:
            print(f"  FAILED: {result.stderr}")
            print()
            print("This usually means you need to run this script AS ADMINISTRATOR.")
            print("Right-click PowerShell/CMD and select 'Run as Administrator', then:")
            print(f"  python {Path(__file__).name}")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

    finally:
        # Clean up temporary XML
        if xml_path:
            try:
                Path(xml_path).unlink()
            except Exception:
                pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
