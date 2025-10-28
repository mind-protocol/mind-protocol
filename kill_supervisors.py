"""
Kill only MPSv3 supervisor processes, leaving Claude Code and other Python processes intact.

Usage: python kill_supervisors.py
"""
import psutil
import os

def find_supervisor_pids():
    """Find PIDs of mpsv3_supervisor.py processes."""
    supervisor_pids = []
    current_pid = os.getpid()

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('mpsv3_supervisor' in arg for arg in cmdline):
                    if proc.info['pid'] != current_pid:  # Don't include this script
                        supervisor_pids.append((proc.info['pid'], ' '.join(cmdline)))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return supervisor_pids

def main():
    print("Searching for MPSv3 supervisor processes...")
    supervisor_pids = find_supervisor_pids()

    if not supervisor_pids:
        print("✅ No supervisor processes found.")
        return

    print(f"\n Found {len(supervisor_pids)} supervisor process(es):\n")
    for pid, cmdline in supervisor_pids:
        print(f"  PID {pid}: {cmdline}")

    print("\n⚠️  About to terminate these processes. Press Ctrl+C to cancel.")
    input("Press Enter to continue...")

    for pid, cmdline in supervisor_pids:
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            print(f"✅ Terminated PID {pid}")
        except psutil.NoSuchProcess:
            print(f"⚠️  PID {pid} already gone")
        except psutil.AccessDenied:
            print(f"❌ Access denied for PID {pid} - try running as administrator")
        except Exception as e:
            print(f"❌ Error killing PID {pid}: {e}")

    print("\n✅ Done. All supervisor processes terminated.")
    print("   You can now restart with: python -u orchestration/mpsv3_supervisor.py --config orchestration/services/mpsv3/services.yaml")

if __name__ == "__main__":
    main()
