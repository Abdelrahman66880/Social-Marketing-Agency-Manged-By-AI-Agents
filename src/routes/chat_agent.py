# src/routes/chat_agent.py
from fastapi import APIRouter, Request, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List

from langchain_core.messages import HumanMessage
from src.agents.graph import workflow
from src.agents.checkpointer import AsyncMongoDBSaver
from src.models.db_schemas.User import User
from src.routes.authentication.authentication import get_current_user

# Initialize Router
agent_router = APIRouter(
    prefix="/agent",
    tags=["Agent Chat"]
)

class ChatRequest(BaseModel):
    message: str
    thread_id: str  # Unique ID for this conversation (e.g., "session_123")
    is_chat_mode: bool = True # Flag to enable/disable persistent history

class ChatResponse(BaseModel):
    response: str
    thread_id: str

@agent_router.post(
    "/chat", 
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK
)
async def chat_with_agent(
    req: Request, 
    body: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Talk to the Social Marketing Agency Agent.
    If is_chat_mode is True, it saves history to MongoDB.
    If False, it treats the request as a one-off command (Stateless).
    """
    # 1. Initialize Persistence (Memory)
    saver = None
    if body.is_chat_mode:
        try:
            # We use the existing MongoDB connection from the request
            saver = AsyncMongoDBSaver(req.app.mongo_conn) 
        except AttributeError:
            raise HTTPException(500, "Database connection not authenticated.")

    # 2. Compile the Graph (Conditionally with Persistence)
    app = workflow.compile(checkpointer=saver)


    # 3. Prepare Input
    # We inject the current USER_ID into the system prompt context so the agent knows who it is serving.
    user_id_str = str(current_user.id)
    input_message = HumanMessage(content=body.message)

    # 4. Run the Agent
    config = {"configurable": {"thread_id": body.thread_id}}
    
    # We pass the user_id to the state so tools can access it
    initial_state = {
        "messages": [input_message],
        "user_id": user_id_str 
    }

    # ainvoke runs the graph until it hits END or an interrupt
    final_state = await app.ainvoke(
        initial_state, 
        config=config
    )

    # 5. Extract the Final Response
    # The last message in the list is the Agent's reply
    messages = final_state["messages"]
    last_msg = messages[-1]
    
    return ChatResponse(
        response=str(last_msg.content),
        thread_id=body.thread_id
    )
