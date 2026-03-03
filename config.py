from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import yaml
import os

class ToolConfig(BaseModel):
    name: str
    params: Optional[Dict] = None

class AgentConfig(BaseModel):
    name: str
    role: str
    goal: str
    provider: str = Field(default="openai") # openai, anthropic, google
    model: str = Field(default="gpt-4o")
    tools: List[str] = Field(default_factory=list)
    system_prompt: Optional[str] = None

class FrameworkConfig(BaseModel):
    name: str
    description: str
    agents: List[AgentConfig]
    tasks: List[str]
    workspace_name: str = Field(default="default")
    memory_enabled: bool = True
    checkpoint_db_url: Optional[str] = None
    vector_db_path: str = "./chroma_db"

def load_config(config_path: str) -> FrameworkConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    return FrameworkConfig(**config_data)

if __name__ == "__main__":
    # Example usage / validation
    example_yaml = """
name: DevTeam
description: A mock software development team
agents:
  - name: Architect
    role: "Solution Architect"
    goal: "Design the system architecture and define todos"
    model: "gpt-4o"
    tools: ["file_write", "file_read"]
  - name: Developer
    role: "Software Engineer"
    goal: "Implement code according to architecture"
    model: "gpt-4o"
    tools: ["file_write", "file_read", "git_commit"]
tasks:
  - "Create a simple calculator in Python"
"""
    with open("example_config.yaml", "w") as f:
        f.write(example_yaml)
    
    config = load_config("example_config.yaml")
    print(config)
