from typing import List, Dict
import httpx
from fastapi import HTTPException
from src.helpers.config import get_Settings
from src.models.schemas.facebookSchemas import FacebookReplyRequest

settings = get_Settings()


class FacebookController:
    """
    Controller for handling Facebook Graph API operations:
    - Sending replies to Messenger messages
    - Fetching page messages (inbox)
    - Fetching feed interactions (posts, comments, reactions)
    - Replying to comments on posts
    """

    # ----------------------
    # Messenger Send API
    # ----------------------
    @classmethod
    async def reply_to_message(
        cls,
        psid: str,
        text: str,
        page_id: str,
        facebookPageAccessToken: str,
        messaging_type: str = "RESPONSE",
    ) -> Dict:
        """
        Send a reply to a user's Messenger message.

        Args:
            psid (str): Page-scoped ID of the user.
            text (str): The reply message text.
            page_id (str): ID of the Facebook Page.
            facebookPageAccessToken (str): Valid Page Access Token with `pages_messaging`.
            messaging_type (str, optional): Messaging type. Default = "RESPONSE".

        Returns:
            Dict: API response with recipient ID and message ID.
        """
        url = f"https://graph.facebook.com/{settings.GRAPH_API_VERSION}/{page_id}/messages"
        params = {"access_token": facebookPageAccessToken}

        payload = FacebookReplyRequest(
            recipient={"id": psid},
            message={"text": text},
            messaging_type=messaging_type,
        ).model_dump()

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, params=params, json=payload)

        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.json())

        return resp.json()

    # ----------------------
    # Page Messages (Inbox)
    # ----------------------
    @classmethod
    async def fetch_page_messages(cls, page_id: str, access_token: str) -> List[Dict]:
        """
        Retrieve all conversation threads and messages for a Page.

        Args:
            page_id (str): ID of the Facebook Page.
            access_token (str): Valid Page Access Token with `pages_messaging`.

        Returns:
            List[Dict]: A list of conversations with participants and messages.
        """
        url = f"https://graph.facebook.com/{settings.GRAPH_API_VERSION}/{page_id}/conversations"
        params = {
            "access_token": access_token,
            "fields": "participants,messages{from,message,created_time}",
        }

        return await cls._fetch_all_pages(url, params)

    # ----------------------
    # Page Feed (Posts, Comments, Reactions)
    # ----------------------
    @classmethod
    async def fetch_page_feed_interactions(cls, page_id: str, access_token: str) -> List[Dict]:
        """
        Retrieve all posts from a Page including comments and reactions.

        Args:
            page_id (str): ID of the Facebook Page.
            access_token (str): Valid Page Access Token with `pages_read_engagement`.

        Returns:
            List[Dict]: A list of posts with comments and reactions.
        """
        url = f"https://graph.facebook.com/{settings.GRAPH_API_VERSION}/{page_id}/posts"
        params = {
            "access_token": access_token,
            "fields": "id,message,created_time,"
                      "comments{from,id,message,created_time},"
                      "reactions{type,id,name}"
        }

        return await cls._fetch_all_pages(url, params)

    # ----------------------
    # Comment Replies
    # ----------------------
    @classmethod
    async def reply_for_comment(
        cls,
        comment_id: str,
        reply: str,
        access_token: str,
    ) -> Dict:
        """
        Post a reply to a specific comment on a Page post.

        Args:
            comment_id (str): ID of the comment to reply to.
            reply (str): Reply text.
            access_token (str): Valid Page Access Token with `pages_manage_engagement`.

        Returns:
            Dict: API response containing the ID of the reply comment.
        """
        url = f"https://graph.facebook.com/{settings.GRAPH_API_VERSION}/{comment_id}/comments"
        payload = {"message": reply, "access_token": access_token}

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, data=payload)

        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.json())

        return resp.json()

    # ----------------------
    # Helper (Pagination)
    # ----------------------
    @classmethod
    async def _fetch_all_pages(cls, url: str, params: Dict) -> List[Dict]:
        """
        Helper method to handle Graph API pagination.

        Args:
            url (str): Initial Graph API endpoint.
            params (Dict): Query params including access_token and fields.

        Returns:
            List[Dict]: Aggregated list of results from all pages.
        """
        all_data = []

        async with httpx.AsyncClient() as client:
            while url:
                resp = await client.get(url, params=params if "after" not in url else None)
                if resp.status_code != 200:
                    raise HTTPException(status_code=resp.status_code, detail=resp.json())

                result = resp.json()
                data = result.get("data", [])
                all_data.extend(data)

                paging = result.get("paging", {})
                url = paging.get("next")  # Use "next" URL directly (includes cursor)

        return all_data
    
    # =====================================================================================
