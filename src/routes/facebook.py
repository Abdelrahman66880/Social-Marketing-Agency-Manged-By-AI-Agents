# facebook_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.controllers.facebook import FacebookController
from src.models.schemas.facebookSchemas import (
    ReplyMessageRequest,
    ReplyCommentRequest,
    FetchPageMessagesRequest,
    FetchPageFeedInteractionsRequest,
)
from typing import List
router = APIRouter(prefix="/facebook", tags=["Facebook"])

"""
Note:
The following endpoint documentation is purely conceptual. 
It is intended to clarify the objectives and expected functionality, 
not to represent the final implementation.
"""

@router.post("/upload_post")
def upload_post():
    """
    Upload a new post to a Facebook page.

    Input:
    - page_id (str): ID of the Facebook page.
    - post (PostSchema): Pydantic model containing post details.

    Output:
    - Confirmation of the upload (e.g., post ID, success status).
    """
    return


@router.post("/update_page_info")
def update_page_info():
    """
    Update a Facebook page’s information.

    Input:
    - page_id (str): ID of the Facebook page.
    - update_info (PageUpdateSchema): Fields to update (e.g., email, about, caption).

    Output:
    - Confirmation of the update with updated fields.
    """
    return


@router.post("/reply_for_message", status_code=status.HTTP_201_CREATED)
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

@router.post("/reply_for_comment")
async def reply_for_comment(request: ReplyCommentRequest):
    """
    Reply to a specific comment on a Facebook post.
    """
    result = await FacebookController.reply_for_comment(
        request.comment_id, request.reply, request.access_token
    )
    return result


@router.get("/search_for_pages")
def search_for_pages():
    """
    Search for competitor Facebook pages by keyword.

    Input:
    - keywords (List[str]): Keywords to search with.
    - limit (int, optional): Maximum number of pages to return.

    Output:
    - List of matching pages with relevant metadata.
    """
    return


@router.get("/get_chat_history")
def get_chat_history():
    """
    Retrieve the chat history of a specific conversation.

    Input:
    - page_id (str): ID of the Facebook page.
    - chat_id (str): ID of the chat thread.

    Output:
    - List of messages in the conversation, formatted for AI processing.
    """
    return

@router.post("/fetch_page_messages")
async def fetch_page_messages(request: FetchPageMessagesRequest):
    """
    Retrieve all messages from a page’s inbox.
    """
    result = await FacebookController.fetch_page_messages(
        request.page_id, request.access_token
    )
    return result
    
@router.post("/fetch_page_feed_interactions")
async def fetch_page_feed_interactions(request: FetchPageFeedInteractionsRequest):
    """
    Retrieve all interactions (comments, reactions) across all posts on a page.
    """
    result = await FacebookController.fetch_page_feed_interactions(
        request.page_id, request.access_token
    )
    return result