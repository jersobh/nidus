import subprocess
from langchain_core.tools import tool

@tool
def git_status():
    """Run git status and return the output."""
    try:
        result = subprocess.run(["git", "status"], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running git status: {e.stderr}"

@tool
def git_add(path: str = "."):
    """Run git add for a specific path."""
    try:
        subprocess.run(["git", "add", path], check=True)
        return f"Successfully added {path} to staging."
    except subprocess.CalledProcessError as e:
        return f"Error running git add: {e}"

@tool
def git_commit(message: str):
    """Run git commit with a message."""
    try:
        result = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True, check=True)
        return f"Committed successfully: {result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Error running git commit: {e.stderr}"

@tool
def git_clone(url: str, path: str):
    """Clone a git repository."""
    try:
        subprocess.run(["git", "clone", url, path], check=True)
        return f"Successfully cloned {url} to {path}"
    except subprocess.CalledProcessError as e:
        return f"Error cloning repository: {e}"
