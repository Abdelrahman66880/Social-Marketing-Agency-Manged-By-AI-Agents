from typing import TypedDict, Annotated, List, Union
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    The shared state of the agent graph.
    """
    # The history of messages in the conversation
    messages: Annotated[List[BaseMessage], operator.add]
    
    brand_context: str
    
    user_id: str
