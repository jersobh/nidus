import os
from typing import Annotated
from langchain_core.tools import tool

WORKSPACE_ROOT = "workspaces"

def resolve_path(path: str, workspace_name: str) -> str:
    """Ensures the path is within the designated workspace."""
    # Remove leading slash or '..' to prevent directory traversal
    clean_path = path.lstrip("/").replace("..", "")
    full_path = os.path.join(WORKSPACE_ROOT, workspace_name, clean_path)
    return full_path

@tool
def write_file(path: str, content: str, workspace_name: str = "default"):
    """Write content to a file at the specified path within the workspace."""
    full_path = resolve_path(path, workspace_name)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)
    return f"File written successfully to {full_path}"

@tool
def read_file(path: str, workspace_name: str = "default"):
    """Read the content of a file at the specified path within the workspace."""
    full_path = resolve_path(path, workspace_name)
    if not os.path.exists(full_path):
        return f"Error: File {full_path} not found."
    with open(full_path, "r") as f:
        return f.read()

@tool
def list_files(directory: str = ".", workspace_name: str = "default"):
    """List all files in a directory within the workspace."""
    full_path = resolve_path(directory, workspace_name)
    if not os.path.exists(full_path):
        return f"Error: Directory {full_path} not found."
    return "\n".join(os.listdir(full_path))

@tool
def update_knowledge_doc(name: str, section: str, content: str, workspace_name: str = "default"):
    """
    Update a specialized knowledge markdown file (e.g., plan, todo, findings) within the workspace.
    Creates the file if it doesn't exist.
    """
    rel_path = f"knowledge/{name}.md"
    full_path = resolve_path(rel_path, workspace_name)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    header = f"# {name.replace('_', ' ').capitalize()}\n\n"
    section_header = f"## {section}\n"
    
    current_content = ""
    if os.path.exists(full_path):
        with open(full_path, "r") as f:
            current_content = f.read()
    else:
        current_content = header

    # Simple append/update logic
    if section_header in current_content:
        # Replacement could be more complex, but for now we append to section
        parts = current_content.split(section_header)
        # Find next section or end
        next_section_idx = parts[1].find("\n## ")
        if next_section_idx != -1:
            updated_section = parts[1][:next_section_idx] + "\n" + content + "\n" + parts[1][next_section_idx:]
        else:
            updated_section = parts[1] + "\n" + content + "\n"
        new_content = parts[0] + section_header + updated_section
    else:
        new_content = current_content + "\n" + section_header + content + "\n"
        
    with open(full_path, "w") as f:
        f.write(new_content)
    
    return f"Knowledge doc {full_path} updated in section {section}."
