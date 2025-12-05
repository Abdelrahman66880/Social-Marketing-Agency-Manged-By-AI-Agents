# facebook_routes.py
from fastapi import APIRouter, HTTPException, status, Path
from typing import List, Dict, Any
import requests
from ..models.schemas.postSchams import (
    PageInfoSchema,
    PostUploadSchema
)
from ..models.schemas.InteractionsResponse import InteractionResponse
from src.controllers.facebook import FacebookController
from ..helpers.config import get_Settings
from src.models.schemas.facebookSchemas import (
    ReplyMessageRequest,
    ReplyCommentRequest,
)

setting_object = get_Settings()

facebook_router = APIRouter(
    prefix="/facebook",
    tags=["Facebook"]
)

# ================================================================
# Utility: Consistent Facebook API error handler
# ================================================================
def handle_facebook_error(response):
    """
    Helper to handle Facebook Graph API errors consistently.
    Raises an HTTPException with a clear message if an error occurs.
    """
    data = response.json()
    if "error" in data:
        error = data["error"]
        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": error.get("message", "Facebook API Error"),
                "type": error.get("type"),
                "code": error.get("code"),
                "fbtrace_id": error.get("fbtrace_id"),
            },
        )
    return data


# ================================================================
# ROUTES
# ================================================================
@facebook_router.post(
    "/pages/{page_id}/post",
    status_code=status.HTTP_201_CREATED
)
def upload_post(page_id: str, page_access_token: str, post: PostUploadSchema) -> Dict[str, Any]:
    """
    Upload a post (text, image, or video) to a Facebook Page.

    Args:
        page_id (str): ID of the Facebook Page.
        page_access_token (str): Valid Page access token.
        post (PostUploadSchema): Pydantic model containing post details (message, image_url, video_url).

    Returns:
        Dict[str, Any]: Facebook Graph API response (post ID or error message).
    """

    # Base payload for all post types
    payload = {
        "message": post.message,
        "access_token": page_access_token,
    }

    # Determine post type
    if post.image_url:
        # Upload image post
        url = f"https://graph.facebook.com/v23.0/{page_id}/photos"
        payload["url"] = post.image_url

    elif post.video_url:
        # Upload video post
        url = f"https://graph.facebook.com/v23.0/{page_id}/videos"
        payload["file_url"] = post.video_url

    else:
        # Upload text-only post
        url = f"https://graph.facebook.com/v23.0/{page_id}/feed"

    # Send request
    response = requests.post(url, data=payload)

    # Handle possible API errors
    result = handle_facebook_error(response)
    return result


@facebook_router.get(
    "/pages/{page_id}/info",
    response_model=PageInfoSchema,
    status_code=status.HTTP_200_OK
)
def get_page_info(page_id: str, page_access_token: str):
    """
    Retrieve detailed information about a Facebook Page.

    Args:
        page_id (str): The Facebook Page ID.
        page_access_token (str): A valid Page access token.

    Returns:
        PageInfoSchema: Page metadata (name, about, description, etc.).

    Raises:
        HTTPException: If the Facebook Graph API returns an error.
    """
    url = f"https://graph.facebook.com/v23.0/{page_id}"
    params = {
        "fields": "id,name,about,description,category,category_list,website",
        "access_token": page_access_token
    }

    response = requests.get(url, params=params)
    result = handle_facebook_error(response)
    return result

@facebook_router.put(
    "/pages/{page_id}/posts/{post_id}",
    status_code=status.HTTP_200_OK
)
def update_post(page_id: str, post_id: str, page_access_token: str, message: str):
    """
    Update ONLY the message of an existing Facebook Page post.
    Facebook does NOT allow updating link, media, or attachments.
    """

    url = f"https://graph.facebook.com/v23.0/{post_id}"

    # Facebook allows ONLY the 'message' field to be updated
    payload = {
        "message": message,
        "access_token": page_access_token,
    }

    response = requests.post(url, data=payload)
    result = handle_facebook_error(response)

    return {
        "success": True,
        "updated_fields": {"message": message},
        "result": result
    }

@facebook_router.delete(
    "/pages/{page_id}/posts/{post_id}",
    status_code=status.HTTP_200_OK
)
def delete_post(page_id: str, post_id: str, page_access_token: str):
    """
    Delete a Facebook Page post.

    Args:
        page_id (str): Facebook Page ID.
        post_id (str): Post ID to delete.
        page_access_token (str): Page Access Token with `pages_manage_posts`.

    Returns:
        Dict[str, Any]: Success status.
    """

    # Ensure full post ID format
    if "_" not in post_id:
        post_id = f"{page_id}_{post_id}"

    url = f"https://graph.facebook.com/v23.0/{post_id}"
    params = {
        "access_token": page_access_token
    }

    response = requests.delete(url, params=params)
    result = handle_facebook_error(response)

    return {
        "success": result.get("success", True),
        "post_id": post_id
    }

@facebook_router.post(
    "/pages/{page_id}/messages/{psid}/reply",
    status_code=status.HTTP_201_CREATED
)
async def reply_for_message(page_id: str, psid: str, request: ReplyMessageRequest):
    """
    Send a reply message to a user through the Facebook Messenger Send API.

    Args:
        page_id (str): The Facebook Page ID.
        psid (str): The Page-scoped user ID (PSID) of the recipient.
        request (ReplyMessageRequest): Message content, token, and type.

    Returns:
        Dict[str, Any]: Facebook Send API response.

    Raises:
        HTTPException: If message sending fails.
    """
    result = await FacebookController.reply_to_message(
        psid,
        request.reply_text,
        page_id,
        request.facebookPageAccessToken,
        request.message_type,
    )
    return result


@facebook_router.post(
    "/pages/{page_id}/comments/{comment_id}/reply",
    status_code=status.HTTP_201_CREATED
)
async def reply_for_comment(comment_id: str, request: ReplyCommentRequest):
    """
    Reply to a specific comment on a Facebook post.

    Args:
        comment_id (str): ID of the comment to reply to.
        request (ReplyCommentRequest): Pydantic model with reply text and token.

    Returns:
        Dict[str, Any]: Facebook Graph API response.

    Raises:
        HTTPException: If the reply fails.
    """
    result = await FacebookController.reply_for_comment(
        comment_id, request.reply, request.access_token
    )
    return result


@facebook_router.post(
    "/pages/{page_id}/search",
    status_code=status.HTTP_200_OK
)
def search_for_pages(
    page_id: str,
    keywords: List[str],
    user_access_token: str,
    limit: int
):
    """
    Search for competitor Facebook Pages by keywords.

    Args:
        page_id (str): Facebook Page ID.
        keywords (List[str]): Keywords to search with.
        user_access_token (str): Valid USER access token.
        limit (int): Max number of results per keyword.

    Returns:
        Dict[str, Any]: List of matching pages with metadata.

    Raises:
        HTTPException: If the Facebook Graph API returns an error.
    """
    GRAPH_API_VERSION = "v23.0"
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/search"

    all_results = []

    for keyword in keywords:
        params = {
            "type": "page",
            "q": keyword,
            "fields": "id,name,category,link",
            "limit": limit,
            "access_token": user_access_token
        }

        response = requests.get(url, params=params)
        data = handle_facebook_error(response)

        all_results.extend(data.get("data", []))

    pages = [
        {
            "id": p.get("id"),
            "name": p.get("name"),
            "category": p.get("category"),
            "link": p.get("link")
        }
        for p in all_results
    ]

    return {"keywords": keywords, "results": pages}


@facebook_router.get(
    "/pages/{page_id}/chats/{chat_id}/messages",
    status_code=status.HTTP_200_OK
)
def get_chat_history(page_id: str, chat_id: str, page_access_token: str):
    """
    Retrieve the message history of a specific chat (conversation) between the Page and a user.

    Args:
        page_id (str): Facebook Page ID.
        chat_id (str): Chat thread (conversation) ID.
        page_access_token (str): Valid Page access token with messaging permissions.

    Returns:
        Dict[str, Any]: List of messages in chronological order.

    Raises:
        HTTPException: If the chat ID is invalid or Facebook API fails.
    """
    GRAPH_API_VERSION = setting_object.GRAPH_API_VERSION
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{chat_id}/messages"
    params = {
        "fields": "message,from,to,created_time",
        "access_token": page_access_token
    }

    response = requests.get(url, params=params)
    data = handle_facebook_error(response)

    messages = [
        {
            "sender_id": msg["from"]["id"],
            "sender_name": msg["from"].get("name", "Unknown"),
            "recipient_id": msg["to"]["data"][0]["id"] if msg.get("to") else None,
            "message": msg.get("message"),
            "created_time": msg["created_time"]
        }
        for msg in data.get("data", [])
    ]

    return {
        "page_id": page_id,
        "chat_id": chat_id,
        "messages": messages
    }


@facebook_router.get(
    "/pages/{page_id}/messages",
    status_code=status.HTTP_200_OK
)
async def fetch_page_messages(
    access_token: str,
    page_id: str = Path(..., description="Facebook Page ID"),
 ):
    """
    Retrieve all messages from a Page's inbox.

    Args:
        page_id (str): Facebook Page ID.
        access_token (str): Valid Page access token with `pages_messaging`.

    Returns:
        Dict[str, Any]: Facebook API response containing all messages.

    Raises:
        HTTPException: If fetching messages fails.
    """
    result = await FacebookController.fetch_page_messages(page_id, access_token)
    return result


@facebook_router.get(
    "/pages/{page_id}/posts/interactions",
    status_code=status.HTTP_200_OK
)
async def fetch_page_feed_interactions(page_id: str, access_token: str):
    """
    Retrieve all interactions (comments, reactions, etc.) across all posts on a Page.

    Args:
        page_id (str): Facebook Page ID.
        access_token (str): Valid Page access token.

    Returns:
        Dict[str, Any]: Aggregated interactions for all posts.

    Raises:
        HTTPException: If Graph API fails.
    """
    result = await FacebookController.fetch_page_feed_interactions(page_id, access_token)
    return result