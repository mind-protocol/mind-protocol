@echo off
REM Install Guardian Watchdog as Windows Scheduled Task
REM Runs on system boot with highest privileges

schtasks /Create /SC ONSTART /TN "MindGuardianWatchdog" /TR "\"C:\Users\reyno\mind-protocol\.venv\Scripts\python.exe\" \"C:\Users\reyno\mind-protocol\ops\guardian_watchdog.py\"" /RL HIGHEST /F

if %ERRORLEVEL% == 0 (
    echo SUCCESS: Watchdog installed as scheduled task
) else (
    echo ERROR: Failed to install watchdog task
)
pause
