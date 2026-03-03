from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from config import AgentConfig, FrameworkConfig
from state import AgentState
import functools

def get_llm(provider: str, model_name: str):
    """Factory to get the correct LLM instance."""
    if provider == "openai":
        return ChatOpenAI(model=model_name)
    elif provider == "anthropic":
        return ChatAnthropic(model=model_name)
    elif provider == "google":
        return ChatGoogleGenerativeAI(model=model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def create_agent_node(agent_config: AgentConfig, tools: List):
    """Creates a ReAct agent node for a specific agent configuration."""
    llm = get_llm(agent_config.provider, agent_config.model)
    
    def agent_node(state: AgentState):
        workspace_info = f"\nYour current workspace is: {state['workspace_name']}. All files you create, read, or edit must be within this workspace. You MUST provide the 'workspace_name' parameter to all file tools."
        system_prompt = (agent_config.system_prompt or f"You are a {agent_config.role}. Goal: {agent_config.goal}") + workspace_info
        
        agent = create_react_agent(llm, tools, prompt=system_prompt)
        result = agent.invoke(state)
        
        # Display internal tool calls for visibility
        new_msgs = result["messages"][len(state["messages"]):]
        for msg in new_msgs:
            if msg.type == "ai" and getattr(msg, "tool_calls", None):
                for tc in msg.tool_calls:
                    print(f"[{agent_config.name} used tool: {tc['name']}]")
            elif msg.type == "tool":
                snippet = str(msg.content)[:100].replace("\n", " ")
                print(f"[{agent_config.name} tool result: {snippet}...]")
                
        raw_return_content = result["messages"][-1].content
        if isinstance(raw_return_content, list):
            final_content = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in raw_return_content])
        else:
            final_content = str(raw_return_content)
            
        return {
            "messages": [HumanMessage(content=final_content, name=agent_config.name)],
        }
    
    return agent_node

def create_supervisor_node(provider: str, llm_model: str, agent_names: List[str]):
    """Creates a supervisor node that decides the next agent to act."""
    llm = get_llm(provider, llm_model)
    
    system_prompt = (
        "You are a supervisor managing a team of agents: {agents}. "
        "Based on the conversation and the current task, decide who should act next. "
        "If the task is complete, respond with 'FINISH'. "
        "If you need clarification from the human, respond with 'HUMAN'."
    ).format(agents=", ".join(agent_names))
    
    def supervisor_node(state: AgentState):
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = llm.invoke(messages)
        
        raw_content = response.content
        if isinstance(raw_content, list):
            content = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in raw_content])
        else:
            content = str(raw_content)
            
        content = content.strip()
        
        # Simple routing logic based on LLM response
        next_agent = "FINISH"
        if "HUMAN" in content:
            next_agent = "HUMAN"
        elif any(name in content for name in agent_names):
            # Pick the first matching agent name
            for name in agent_names:
                if name in content:
                    next_agent = name
                    break
        
        # Add supervisor's message to state to ensure visibility for the user and other agents
        return {"next": next_agent, "messages": [AIMessage(content=content, name="Supervisor")]}
    
    return supervisor_node
