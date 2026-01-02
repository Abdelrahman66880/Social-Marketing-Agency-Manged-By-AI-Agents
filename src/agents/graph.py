from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.state import AgentState
from src.agents.prompts.prompts import ANALYST_PROMPT, CREATOR_PROMPT, CHAT_PROMPT
from src.agents.tools import ALL_TOOLS
# Import specific tools for binding
from src.agents.tools.general_tools import (
    get_brand_voice_context, check_content_calendar, review_past_performance,
    check_draft_status, create_draft_post, save_market_analysis
)
from src.agents.tools.research_tools import web_search_competitor
from src.helpers.config import get_Settings

settings = get_Settings()

# ==============================================================================
# 1. SETUP LLM & TOOLS
# ==============================================================================

# Initialize the main model
llm = ChatOpenAI(
    model="gpt-4o", 
    api_key=settings.OPENAI_API_KEY,
    temperature=0.5
)

# Define toolsets for each agent
analyst_tools = [web_search_competitor, review_past_performance, save_market_analysis]
creator_tools = [get_brand_voice_context, check_content_calendar, check_draft_status, create_draft_post]

# Bind tools to the LLM for specific agents
analyst_llm = llm.bind_tools(analyst_tools)
creator_llm = llm.bind_tools(creator_tools)
chat_llm = llm # No tools for general chat for now, or maybe generic ones

# ==============================================================================
# 2. DEFINE NODE FUNCTIONS
# ==============================================================================

def router_node(state: AgentState):
    """
    Decides which agent should act next based on the LAST message.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # Simple keyword routing (You can upgrade this to an LLM router later)
    # Using a mini-LLM call for routing is more robust
    router_response = llm.invoke(
        [SystemMessage(content="Classify the user intent into: 'analyst', 'creator', or 'chat'. Return ONLY the word."), 
         last_message]
    )
    choice = router_response.content.lower().strip()
    
    if "analyst" in choice:
        return {"next_agent": "analyst"}
    elif "creator" in choice:
        return {"next_agent": "creator"}
    else:
        return {"next_agent": "chat"}


def analyst_node(state: AgentState):
    """
    The Analyst Agent Node.
    """
    messages = state["messages"]
    # Prepend System Prompt if not present (simplified)
    # Ideally, we manage a separate history per agent, but for a shared history:
    response = analyst_llm.invoke(
        [SystemMessage(content=ANALYST_PROMPT)] + messages
    )
    return {"messages": [response]}


def creator_node(state: AgentState):
    """
    The Creator Agent Node.
    """
    messages = state["messages"]
    response = creator_llm.invoke(
        [SystemMessage(content=CREATOR_PROMPT)] + messages
    )
    return {"messages": [response]}


def chat_node(state: AgentState):
    """
    The General Chat Node.
    """
    messages = state["messages"]
    response = chat_llm.invoke(
        [SystemMessage(content=CHAT_PROMPT)] + messages
    )
    return {"messages": [response]}

# ==============================================================================
# 3. DEFINE THE GRAPH
# ==============================================================================

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("router", router_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("creator", creator_node)
workflow.add_node("chat", chat_node)

# Add Tool Nodes (Prebuilt from LangGraph)
# We create separate tool nodes to keep execution clean
analyst_tool_node = ToolNode(analyst_tools)
creator_tool_node = ToolNode(creator_tools)

workflow.add_node("analyst_tools", analyst_tool_node)
workflow.add_node("creator_tools", creator_tool_node)

# ==============================================================================
# 4. DEFINE EDGES (LOGIC)
# ==============================================================================

# Start -> Router
workflow.add_edge(START, "router")

# Router -> Specific Agent (Conditional)
def route_decision(state: AgentState):
    return state["next_agent"]

workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "analyst": "analyst",
        "creator": "creator",
        "chat": "chat"
    }
)

# Agent -> Tools (Conditional: Did the agent call a tool?)
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "continue"
    return "end"

# Analyst Flow
workflow.add_conditional_edges(
    "analyst",
    should_continue,
    {
        "continue": "analyst_tools",
        "end": END
    }
)
workflow.add_edge("analyst_tools", "analyst") # Loop back to agent

# Creator Flow
workflow.add_conditional_edges(
    "creator",
    should_continue,
    {
        "continue": "creator_tools",
        "end": END
    }
)
workflow.add_edge("creator_tools", "creator") # Loop back to agent

# Chat Flow (Simple)
workflow.add_edge("chat", END)

# ==============================================================================
# 5. COMPILE
# ==============================================================================
# NOTE: Checkpointer will be passed when invoking, or set here.
# For now, we return the compiled graph.
app = workflow.compile()
