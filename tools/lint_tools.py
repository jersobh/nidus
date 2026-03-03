import os
import subprocess
from langchain_core.tools import tool
from tools.file_tools import resolve_path

@tool
def run_linter(path: str = ".", workspace_name: str = "default"):
    """
    Run `flake8` and `black --check` on Python files in the given path to detect formatting and syntax issues.
    """
    full_path = resolve_path(path, workspace_name)
    if not os.path.exists(full_path):
        return f"Error: Path {full_path} not found."

    results = []

    # Run Black
    black_cmd = f"black --check {full_path}"
    try:
        black_res = subprocess.run(black_cmd, shell=True, capture_output=True, text=True)
        results.append("Black Formatting Check:")
        if black_res.returncode == 0:
            results.append("All clear.")
        else:
            results.append(black_res.stderr)
    except Exception as e:
        results.append(f"Black failed to run: {e}")

    # Run flake8
    flake_cmd = f"flake8 {full_path}"
    try:
        flake_res = subprocess.run(flake_cmd, shell=True, capture_output=True, text=True)
        results.append("\nFlake8 Syntax Check:")
        if flake_res.returncode == 0:
            results.append("All clear.")
        else:
            results.append(flake_res.stdout)
    except Exception as e:
        results.append(f"Flake8 failed to run: {e}")

    return "\n".join(results)
