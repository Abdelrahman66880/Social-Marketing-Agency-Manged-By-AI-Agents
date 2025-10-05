# src/controllers/analytics.py
from typing import List, Dict, Any
import requests
import logging
from aiohttp import ClientSession

logger = logging.getLogger(__name__)
GRAPH_URL = "https://graph.facebook.com/v23.0"


class AnalyticsController:
    
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

    @staticmethod
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

    @staticmethod
    async def generate_recommendations(page_id: str, page_access_token: str, business_profile: Dict = None):
        """
        Combine page analytics and competitor analysis to prepare AI recommendation input.
        """
        # 1️⃣ Analyze current page performance
        interaction_summary = await AnalyticsController.analyze_interaction_by_page_id(page_id, page_access_token)

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
            competitor_insights = await AnalyticsController.analyze_competitors(
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
