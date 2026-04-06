import subprocess
import sys
import os
import time
import threading

root = os.path.dirname(os.path.abspath(__file__))
backend = os.path.join(root, "backend")
frontend = os.path.join(root, "frontend")

if sys.platform == "win32":
    python = os.path.join(root, "venv", "Scripts", "python.exe")
    npm = "npm.cmd"
else:
    python = os.path.join(root, "venv", "bin", "python")
    npm = "npm"

print("Starting Instance 2 — ports 8001 and 5174...")

def run_backend():
    subprocess.run(
        [python, "-m", "uvicorn", "main:app", "--port", "8001", "--reload"],
        cwd=backend
    )

def run_frontend():
    subprocess.run(
        [npm, "run", "dev", "--", "--port", "5174", "--mode", "instance2"],
        cwd=frontend,
        shell=(sys.platform == "win32")
    )

backend_thread = threading.Thread(target=run_backend, daemon=True)
backend_thread.start()

print("Waiting for backend to start...")
time.sleep(3)

frontend_thread = threading.Thread(target=run_frontend, daemon=True)
frontend_thread.start()

print("Backend:  http://127.0.0.1:8001")
print("Frontend: http://localhost:5174")
print("\nBoth running — press Ctrl+C to stop")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down...")