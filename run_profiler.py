"""Launcher that adds the backend to sys.path and runs the profiler inline."""
import subprocess, sys

# Use venv Python from the backend virtualenv (resolved via known absolute path)
BACKEND = r"C:\Users\ajays\OneDrive\Desktop\Social Media Mental Health Risk Analyzer\u201cbackend"
PYTHON  = BACKEND + r"\venv\Scripts\python.exe"
SCRIPT  = r"C:\Users\ajays\OneDrive\Desktop\pipeline_profiler.py"

result = subprocess.run([PYTHON, SCRIPT], capture_output=False)
sys.exit(result.returncode)
