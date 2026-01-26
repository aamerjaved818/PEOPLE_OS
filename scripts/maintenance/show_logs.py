"""
Real-time log viewer for PEOPLE OS
Monitors the backend for requests and shows what's happening
"""
import subprocess
import time
import sys
import os

# Kill existing backend if running
os.system('Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*backend*"} | Stop-Process -Force 2>$null')
time.sleep(1)

print("\n" + "="*80)
print(" "*20 + "PEOPLE OS BACKEND - REAL-TIME LOGS")
print("="*80 + "\n")

print("Starting backend with detailed logging...\n")

# Start backend with full output
proc = subprocess.Popen(
    [sys.executable, "-m", "backend.main"],
    cwd="d:\\Project\\PEOPLE_OS",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True,
    bufsize=1
)

try:
    for line in proc.stdout:
        # Print each line as it comes
        sys.stdout.write(line)
        sys.stdout.flush()
except KeyboardInterrupt:
    print("\n\n[Stopping log viewer...]")
    proc.terminate()
    proc.wait()
