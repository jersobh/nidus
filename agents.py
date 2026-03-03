from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
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
        
        agent = create_react_agent(llm, tools, state_modifier=system_prompt)
        result = agent.invoke(state)
        return {
            "messages": [HumanMessage(content=result["messages"][-1].content, name=agent_config.name)],
        }
    
    return agent_node

def create_supervisor_node(llm_model: str, agent_names: List[str]):
    """Creates a supervisor node that decides the next agent to act."""
    llm = ChatOpenAI(model=llm_model)
    
    system_prompt = (
        "You are a supervisor managing a team of agents: {agents}. "
        "Based on the conversation and the current task, decide who should act next. "
        "If the task is complete, respond with 'FINISH'. "
        "If you need clarification from the human, respond with 'HUMAN'."
    ).format(agents=", ".join(agent_names))
    
    def supervisor_node(state: AgentState):
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = llm.invoke(messages)
        content = response.content.strip()
        
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
        
        return {"next": next_agent}
    
    return supervisor_node
