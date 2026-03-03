from typing import Dict, List
from langgraph.graph import StateGraph, END
from agents import create_agent_node, create_supervisor_node
from config import load_config, FrameworkConfig
from state import AgentState
from tools.file_tools import write_file, read_file, list_files, update_knowledge_doc
from tools.git_tools import git_status, git_add, git_commit, git_clone
from tools.web_tools import web_search, read_website, open_documentation
from interface import display_agent_output, get_human_input, print_welcome
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
import sys

# Define available tools
TOOLS_MAP = {
    "file_write": write_file,
    "file_read": read_file,
    "file_list": list_files,
    "knowledge_update": update_knowledge_doc,
    "git_status": git_status,
    "git_add": git_add,
    "git_commit": git_commit,
    "git_clone": git_clone,
    "web_search": web_search,
    "web_read": read_website,
    "doc_search": open_documentation
}

def build_graph(config: FrameworkConfig):
    workflow = StateGraph(AgentState)
    
    agent_names = [a.name for a in config.agents]
    
    # Add nodes for each agent
    for agent_config in config.agents:
        # Map tool names to actual tool objects
        agent_tools = [TOOLS_MAP[t] for t in agent_config.tools if t in TOOLS_MAP]
        node = create_agent_node(agent_config, agent_tools)
        workflow.add_node(agent_config.name, node)
    
    # Add supervisor node
    supervisor = create_supervisor_node(config.agents[0].model, agent_names)
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
    
    # Checkpointer for memory
    memory = InMemorySaver()
    return workflow.compile(checkpointer=memory)

def run_framework(config_path: str, initial_task: str):
    config = load_config(config_path)
    graph = build_graph(config)
    
    inputs = {
        "messages": [HumanMessage(content=initial_task)],
        "shared_context": {},
        "current_task": initial_task,
        "workspace_name": config.workspace_name
    }
    
    config_run = {"configurable": {"thread_id": "1"}}
    
    print_welcome(config.name, config.description)
    
    for output in graph.stream(inputs, config_run):
        for key, value in output.items():
            if key != "__metadata__" and key != "supervisor":
                if "messages" in value:
                    display_agent_output(key, value["messages"][-1].content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_yaml>")
        sys.exit(1)
        
    run_framework(sys.argv[1], "Initialize the project and create a README.md")
