# facebook_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from ..models.enums.ResponseSignal import ResponseSignal
from ..models.db_schemas.Post import Post
from ..models.schemas.postSchams import PageInfoSchema, PostUpdateSchema
from src.controllers.facebook import FacebookController
import requests
import json
import os
from ..helpers.config import get_Settings
from src.models.schemas.facebookSchemas import (
    ReplyMessageRequest,
    ReplyCommentRequest,
    FetchPageMessagesRequest,
    FetchPageFeedInteractionsRequest,
)
from typing import List


setting_object = get_Settings()

facebook_router = APIRouter(
    prefix="/facebook", 
    tags=["Facebook"]
)

"""
Note:
The following endpoint documentation is purely conceptual. 
It is intended to clarify the objectives and expected functionality, 
not to represent the final implementation.
"""


@facebook_router.post("/upload_post")
def upload_post(page_id: str, page_Access_Token: str):
    """
    Upload a new post to a Facebook page.

    Input:
    - page_id (str): ID of the Facebook page.
    - post (PostSchema): Pydantic model containing post details.

    Output:
    - Reture dict contain the postid <PAGEID_POSTID>.
    """
    
    url = f"https://graph.facebook.com/v23.0/{page_id}/feed"
    payload = {
        "message": "Hello from AI Agent again 🚀",
        "access_token": page_Access_Token
    }
    
    response = requests.post(url, data=payload)
    result = response.json()
    return result


@facebook_router.get("/page_info", response_model=PageInfoSchema)
def get_page_info(page_id: str, page_access_token: str):
    url = f"https://graph.facebook.com/v23.0/{page_id}"
    params = {
        "fields": "id,name,about,description,category,category_list,website",
        "access_token": page_access_token
    }
    response = requests.get(url, params=params).json()
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return response

@facebook_router.post("/update_post")
def update_post(post_id: str, page_access_token: str, update_data: PostUpdateSchema):
    """
    Update an existing post on a Facebook page.

    Input:
    - post_id (str): ID of the post to update.
    - page_access_token (str): Page access token with correct permissions.
    - update_data (PostUpdateSchema): Fields to update (e.g., message, link).

    Output:
    - Confirmation of the update.
    """
    url = f"https://graph.facebook.com/v23.0/{post_id}"
    payload = update_data.dict(exclude_unset=True)
    payload["access_token"] = page_access_token

    response = requests.post(url, data=payload)
    result = response.json()

    if response.status_code != 200 or not result.get("success"):
        raise HTTPException(status_code=response.status_code, detail=result)

    return {
        "success": True,
        "updated_fields": update_data.dict(exclude_unset=True)
    }




@facebook_router.post("/reply_for_message", status_code=status.HTTP_201_CREATED)
async def reply_for_message(request: ReplyMessageRequest):
    """
    Send a reply message to a user via Messenger Send API.
    """
    result = await FacebookController.reply_to_message(
        request.psid,
        request.reply_text,
        request.page_id,
        request.facebookPageAccessToken,
        request.message_type,
    )
    return result

@facebook_router.post("/reply_for_comment")
async def reply_for_comment(request: ReplyCommentRequest):
    """
    Reply to a specific comment on a Facebook post.
    """
    result = await FacebookController.reply_for_comment(
        request.comment_id, request.reply, request.access_token
    )
    return result


@facebook_router.get("/search_for_pages")
def search_for_pages(keywords: List[str], page_access_token: str, limit: int = 5):
    """
    Search for competitor Facebook pages by keyword.

    Input:
    - keywords (List[str]): Keywords to search with.
    - limit (int, optional): Maximum number of pages to return.

    Output:
    - List of matching pages with relevant metadata.
    """
    GRAPH_API_VERSION = setting_object.GRAPH_API_VERSION
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/search"
    params = {
        "type": "page",
        "q": keywords,              
        "fields": "id,name,category",
        "limit": limit,
        "access_token": page_access_token
    }
    response = requests.get(url=url, params=params)
    result = response.json()
    
    if 'error' in result:
        raise HTTPException(
            status_code=response.status_code,
            detail=result["error"]
        )
    
    # the formmated returned
    pages = [
        {
            "id": page.get("id"),
            "name":page.get("name"),
            "category": page.get("category"),
        }
        for page in result.get('data', [])
    ] 
    return {
        "keywords": keywords,
        "results": pages
    }

# ======================================================================================
# I need to check availability of chat id
# ======================================================================================

@facebook_router.get("/get_chat_history")
def get_chat_history(page_id: str,chat_id: str,page_access_token: str):
    """
    Retrieve the chat history of a specific conversation between the page and a customer.

    Input:
    - page_id (str): ID of the Facebook page.
    - chat_id (str): ID of the chat thread (conversation ID).
    - page_access_token (str): Valid page access token with 'pages_messaging' and 'pages_read_engagement' permissions.

    Output:
    - List of messages in the conversation, formatted for AI processing.
    """

    GRAPH_API_VERSION = setting_object.GRAPH_API_VERSION
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{chat_id}/messages"
    params = {
        "fields": "message,from,to,created_time",
        "access_token": page_access_token
    }

    response = requests.get(url, params=params)
    result = response.json()

    # Handle API errors
    if "error" in result:
        raise HTTPException(
            status_code=response.status_code,
            detail=result["error"]
        )

    # Format messages for readability / AI input
    messages = [
        {
            "sender_id": msg["from"]["id"],
            "sender_name": msg["from"].get("name", "Unknown"),
            "recipient_id": msg["to"]["data"][0]["id"] if msg.get("to") else None,
            "message": msg.get("message"),
            "created_time": msg["created_time"]
        }
        for msg in result.get("data", [])
    ]

    return {
        "page_id": page_id,
        "chat_id": chat_id,
        "messages": messages
    }


# ===========================================================================================

@facebook_router.post("/fetch_page_messages")
async def fetch_page_messages(request: FetchPageMessagesRequest):
    """
    Retrieve all messages from a page’s inbox.
    """
    result = await FacebookController.fetch_page_messages(
        request.page_id, request.access_token
    )
    return result
    
@facebook_router.post("/fetch_page_feed_interactions")
async def fetch_page_feed_interactions(request: FetchPageFeedInteractionsRequest):
    """
    Retrieve all interactions (comments, reactions) across all posts on a page.
    """
    result = await FacebookController.fetch_page_feed_interactions(
        request.page_id, request.access_token
    )
    return result