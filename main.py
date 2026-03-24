from typing import Dict, List
from langgraph.graph import StateGraph, END
from agents import create_agent_node, create_supervisor_node
from config import load_config, FrameworkConfig
from state import AgentState
from tools.file_tools import write_file, read_file, list_files, update_knowledge_doc, execute_command, edit_file, append_file
import json
from tools.git_tools import git_status, git_add, git_commit, git_clone
from tools.web_tools import web_search, read_website, scrape_with_playwright, open_documentation
from tools.lint_tools import run_linter
from interface import display_agent_output, get_human_input, print_welcome
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
import sys
import os

# Load environment variables from .env file
load_dotenv()

def build_graph(config: FrameworkConfig, tools_map: dict, checkpointer):
    workflow = StateGraph(AgentState)
    
    agent_names = [a.name for a in config.agents]
    
    # Add nodes for each agent
    for agent_config in config.agents:
        # Map tool names to actual tool objects
        agent_tools = [tools_map[t] for t in agent_config.tools if t in tools_map]
        node = create_agent_node(agent_config, agent_tools)
        workflow.add_node(agent_config.name, node)
    
    # Add supervisor node
    # Defaulting supervisor to use the first agent's provider/model
    supervisor = create_supervisor_node(config.agents[0].provider, config.agents[0].model, agent_names)
    workflow.add_node("supervisor", supervisor)
    
    # Define edges
    for name in agent_names:
        workflow.add_edge(name, "supervisor")
    
    # Conditional edges from supervisor
    conditional_map = {name: name for name in agent_names}
    conditional_map["FINISH"] = END
    conditional_map["HUMAN"] = "human_interrupt"
    
    workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
    
    # Human interrupt node
    def human_node(state: AgentState):
        feedback = get_human_input(state["messages"][-1].content)
        return {"messages": [HumanMessage(content=feedback, name="Human")], "next": "supervisor"}
    
    # Actually we can use the 'interrupt' feature of LangGraph for a more robust version later,
    # but for a simple CLI we can define a node.
    workflow.add_node("human_interrupt", human_node)
    workflow.add_edge("human_interrupt", "supervisor")
    
    workflow.set_entry_point("supervisor")
    
    return workflow.compile(checkpointer=checkpointer)

def run_framework(config_path: str):
    config = load_config(config_path)
    
    print_welcome(config.name, config.description)
    
    from database import init_databases, get_query_memory_tool
    init_databases(config.checkpoint_db_url, config.vector_db_path)
    
    tools_map = {
        "file_write": write_file,
        "file_append": append_file,
        "file_read": read_file,
        "file_list": list_files,
        "execute_command": execute_command,
        "edit_file": edit_file,
        "knowledge_update": update_knowledge_doc,
        "run_linter": run_linter,
        "query_memory": get_query_memory_tool(config.vector_db_path),
        "git_status": git_status,
        "git_add": git_add,
        "git_commit": git_commit,
        "git_clone": git_clone,
        "web_search": web_search,
        "web_read": read_website,
        "scrape_with_playwright": scrape_with_playwright,
        "doc_search": open_documentation
    }
    
    from tools.file_tools import resolve_path
    memory_file_path = resolve_path("memory.md", config.workspace_name)
    state_file_path = resolve_path("run_state.json", config.workspace_name)
    os.makedirs(os.path.dirname(memory_file_path), exist_ok=True)
    
    # Load state
    completed_tasks = []
    if os.path.exists(state_file_path):
        try:
            with open(state_file_path, "r") as f:
                state_data = json.load(f)
                completed_tasks = state_data.get("completed_tasks", [])
        except Exception as e:
            print(f"Warning: could not read state file: {e}")
            
    pending_tasks = [t for t in config.tasks if t not in completed_tasks]
    if not pending_tasks:
        print("All tasks are already completed according to run_state.json.")
        print("Add new tasks to your config file to continue.")
        return
        
    tasks_str = "\n".join([f"- {t}" for t in pending_tasks])
    initial_task = f"Here are the pending tasks to complete:\n{tasks_str}\n\nDo not repeat already completed tasks."
    
    inputs = {
        "messages": [HumanMessage(content=initial_task, name="Human")],
        "shared_context": {},
        "current_task": initial_task,
        "workspace_name": config.workspace_name
    }
    
    # Use workspace name as thread_id so each workspace has its own memory thread
    config_run = {"configurable": {"thread_id": config.workspace_name}}
    
    # Initialize/append memory.md at the start of a run
    mode = "a" if completed_tasks else "w"
    with open(memory_file_path, mode) as f:
        if mode == "w":
            f.write("# Agent Run Memory Log\n\n")
        f.write(f"**Adding new pending tasks:**\n{initial_task}\n\n---\n\n")
    
    if config.checkpoint_db_url:
        from psycopg_pool import ConnectionPool
        from langgraph.checkpoint.postgres import PostgresSaver
        pool = ConnectionPool(conninfo=config.checkpoint_db_url)
        checkpointer = PostgresSaver(pool)
    else:
        checkpointer = InMemorySaver()
        pool = None
        
    try:
        graph = build_graph(config, tools_map, checkpointer)
        for output in graph.stream(inputs, config_run):
            for key, value in output.items():
                if key != "__metadata__":
                    if "messages" in value:
                        msg_content = value["messages"][-1].content
                        display_agent_output(key, msg_content)
                        
                        # Append to memory.md
                        with open(memory_file_path, "a") as f:
                            f.write(f"### {key.capitalize()}\n\n")
                            f.write(f"{msg_content}\n\n---\n\n")
    finally:
        # Save state marking the pending tasks as completed successfully
        with open(state_file_path, "w") as f:
            completed_tasks.extend(pending_tasks)
            json.dump({"completed_tasks": completed_tasks}, f, indent=2)
            
        if pool:
            pool.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_yaml>")
        sys.exit(1)
        
    run_framework(sys.argv[1])
