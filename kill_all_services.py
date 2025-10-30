"""
Kill all Mind Protocol services and supervisors, leaving Claude Code intact.

This kills:
- MPSv3 supervisor processes
- Service processes (websocket_server, autonomy_orchestrator, signals_collector, conversation_watcher)
- Dashboard (node.exe running npm run dev)

Usage: python kill_all_services.py
"""
import psutil
import os

def find_mind_protocol_processes():
    """Find all Mind Protocol related PIDs."""
    processes = {
        'supervisors': [],
        'services': [],
        'dashboard': []
    }
    current_pid = os.getpid()

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue  # Skip this script

            cmdline = proc.info.get('cmdline', [])
            if not cmdline:
                continue

            cmdline_str = ' '.join(cmdline)

            # Check for supervisor
            if 'mpsv3_supervisor' in cmdline_str:
                processes['supervisors'].append((proc.info['pid'], cmdline_str))

            # Check for services
            elif any(svc in cmdline_str for svc in [
                'websocket_server',
                'autonomy_orchestrator',
                'signals_collector',
                'conversation_watcher',
                'stimulus_injection'
            ]):
                processes['services'].append((proc.info['pid'], cmdline_str))

            # Check for dashboard (node running npm dev in mind-protocol dir)
            elif proc.info['name'] in ['node.exe', 'node'] and 'npm' in cmdline_str and 'dev' in cmdline_str:
                # Verify it's in our project directory
                try:
                    cwd = proc.cwd()
                    if 'mind-protocol' in cwd.lower():
                        processes['dashboard'].append((proc.info['pid'], cmdline_str))
                except:
                    pass

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return processes

def main():
    print("Searching for Mind Protocol processes...")
    processes = find_mind_protocol_processes()

    total = len(processes['supervisors']) + len(processes['services']) + len(processes['dashboard'])

    if total == 0:
        print("✅ No Mind Protocol processes found.")
        return

    print(f"\nFound {total} process(es):\n")

    if processes['supervisors']:
        print("📋 Supervisors:")
        for pid, cmdline in processes['supervisors']:
            print(f"  PID {pid}: {cmdline[:100]}")

    if processes['services']:
        print("\n⚙️  Services:")
        for pid, cmdline in processes['services']:
            print(f"  PID {pid}: {cmdline[:100]}")

    if processes['dashboard']:
        print("\n🖥️  Dashboard:")
        for pid, cmdline in processes['dashboard']:
            print(f"  PID {pid}: {cmdline[:100]}")

    print("\n⚠️  About to terminate ALL these processes.")
    print("   This will NOT kill your Claude Code terminals.")
    print("\nPress Ctrl+C to cancel.")
    input("Press Enter to continue...")

    # Kill in order: supervisors first, then services, then dashboard
    for category in ['supervisors', 'services', 'dashboard']:
        for pid, cmdline in processes[category]:
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                print(f"✅ Terminated PID {pid} ({category})")
            except psutil.NoSuchProcess:
                print(f"⚠️  PID {pid} already gone")
            except psutil.AccessDenied:
                print(f"❌ Access denied for PID {pid} - try running as administrator")
            except Exception as e:
                print(f"❌ Error killing PID {pid}: {e}")

    print("\n✅ Done. All Mind Protocol processes terminated.")
    print("\n📝 Next steps:")
    print("   1. Wait 3 seconds for ports to release")
    print("   2. Start supervisor: python -u orchestration/mpsv3_supervisor.py --config orchestration/services/mpsv3/services.yaml")
    print("   3. Look for [MPSv3] and [FileWatcher] startup messages")

if __name__ == "__main__":
    main()
