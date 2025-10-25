from typing import List, Dict, Any
import httpx
from fastapi import HTTPException
from src.helpers.config import get_Settings
from src.models.schemas.facebookSchemas import FacebookReplyRequest
import requests
from aiohttp import ClientSession

settings = get_Settings()

GRAPH_URL = "https://graph.facebook.com/v23.0"
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
    @staticmethod
    async def analyze_interaction_by_page_id(page_id: str, page_access_token: str) -> Dict[str, Any]:
        """
        Fetch posts, comments, and conversations for a page to calculate basic metrics.
        """
        # 1️⃣ Fetch posts (with comments and reactions)
        posts_url = f"{GRAPH_URL}/{page_id}/posts"
        posts_params = {
            "fields": "id,message,created_time,"
                      "comments.limit(10){id,message,from,created_time},"
                      "reactions.summary(true),shares",
            "access_token": page_access_token
        }
        post_response = requests.get(posts_url, params=posts_params).json()
        posts = post_response.get("data", [])

        # 2️⃣ Fetch conversations (Messenger threads)
        conversation_url = f"{GRAPH_URL}/{page_id}/conversations"
        conversation_params = {
            "fields": "messages.limit(10){id,from,message,created_time}",
            "access_token": page_access_token
        }
        conversation_response = requests.get(conversation_url, params=conversation_params).json()
        messages = conversation_response.get("data", [])

        # 3️⃣ Compute basic metrics
        total_posts = len(posts)
        total_comments = sum(len(p.get("comments", {}).get("data", [])) for p in posts)
        total_messages = sum(len(c.get("messages", {}).get("data", [])) for c in messages)
        
        return {
            "page_id": page_id,
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_messages": total_messages,
        }

    # ===========================================================

    @classmethod
    async def analyze_competitors(key_words_list: List[str], page_access_token: str, max_pages: int = 5):
        """
        Search competitor pages by keyword and compute average engagement.
        """
        results = []
        
        async with ClientSession() as session:
            for kw in key_words_list:
                search_url = f"{GRAPH_URL}/search"
                params = {
                    "type": "page",
                    "q": kw,
                    "fields": "id,name,category,fan_count",
                    "limit": max_pages,
                    "access_token": page_access_token
                }
                async with session.get(search_url, params=params) as resp:
                    search_data = await resp.json()
                    pages = search_data.get("data", [])
                    
                for p in pages:
                    page_id = p.get("id")
                    name = p.get("name")

                    posts_url = f"{GRAPH_URL}/{page_id}/posts"
                    post_params = {
                        "fields": "id,message,created_time,reactions.summary(true),comments.summary(true),shares",
                        "limit": 10,
                        "access_token": page_access_token
                    }
                    async with session.get(posts_url, params=post_params) as resp:
                        post_data = await resp.json()
                        posts = post_data.get("data", [])
                    
                    total_engagement = 0
                    for post in posts:
                        reactions = post.get("reactions", {}).get("summary", {}).get("total_count", 0)
                        comments = post.get("comments", {}).get("summary", {}).get("total_count", 0)
                        shares = post.get("shares", {}).get("count", 0)
                        total_engagement += (reactions + comments + shares)

                    avg_engagement_rate = (total_engagement / len(posts)) if posts else 0

                    results.append({
                        "page_id": page_id,
                        "name": name,
                        "avg_engagement_rate": avg_engagement_rate,
                        "category": p.get("category"),
                    })

        return results

    # ===========================================================

    @classmethod
    async def generate_recommendations(page_id: str, page_access_token: str, business_profile: Dict = None):
        """
        Combine page analytics and competitor analysis to prepare AI recommendation input.
        """
        # 1️⃣ Analyze current page performance
        interaction_summary = await FacebookController.analyze_interaction_by_page_id(page_id, page_access_token)

        # 2️⃣ Extract competitor keywords
        keywords = []
        if business_profile:
            if business_profile.get("industry"):
                keywords.append(business_profile["industry"])
            if business_profile.get("competitors"):
                keywords.extend(business_profile["competitors"])

        # 3️⃣ Analyze competitors
        competitor_insights = []
        if keywords:
            competitor_insights = await FacebookController.analyze_competitors(
                keywords, page_access_token, max_pages=3
            )

        # 4️⃣ Combine all insights
        inputs = {
            "summary": interaction_summary,
            "competitors": competitor_insights,
            "business_profile": business_profile or {}
        }

        # Later: send to AI model for recommendations
        return inputs

