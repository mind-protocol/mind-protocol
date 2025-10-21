import psutil
import time

killed = []
for proc in psutil.process_iter(['pid', 'cmdline']):
    try:
        cmdline = proc.info.get('cmdline')
        if cmdline and 'guardian.py' in ' '.join(cmdline):
            pid = proc.pid
            print(f'Killing guardian PID {pid}')
            p = psutil.Process(pid)
            p.terminate()
            killed.append(pid)
    except Exception as e:
        continue

time.sleep(2)

# Force kill
for pid in killed:
    try:
        if psutil.pid_exists(pid):
            psutil.Process(pid).kill()
    except:
        pass

print(f'Killed {len(killed)} guardians')
