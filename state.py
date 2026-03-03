from typing import List, TypedDict, Annotated, Union
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # The messages in the conversation
    messages: Annotated[List[BaseMessage], add_messages]
    # The next agent to act
    next: str
    # Shared knowledge and context
    shared_context: Dict[str, str]
    # Human feedback or questions
    human_feedback: Optional[str]
    # Current task being worked on
    current_task: Optional[str]
    # Root folder for this run's files
    workspace_name: str
