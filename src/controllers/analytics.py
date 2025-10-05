from typing import List, Dict, Any
import httpx
from fastapi import HTTPException
from ..helpers.config import get_Settings
import requests
import logging
from aiohttp import ClientSession

logger = logging.getLogger(__name__)

GRAPH_URL = "https://graph.facebook.com/v23.0"
class AnalyticsController:
    
    @staticmethod
    async def analyze_interaction_by_page_id(page_id: str, page_access_token: str) -> Dict[str, Any]:
        
        # get the posts data comments and recations
        posts_url = f"{GRAPH_URL}/{page_id}/posts"
        posts_params = {
            "fields": "id,message,created_time,"
                      "comments.limit(10){id,message,from,created_time},"
                      "reactions.summary(true),shares",
            "access_token": page_access_token
        }
        post_response = requests.get(posts_url, params=posts_params)
        posts = post_response.get("data", [])
        
        conversation_url = f"{GRAPH_URL}/{page_id}/conversations"
        conversation_params = {
            "fields": "messages.limit(10){id,from,message,created_time}",
            "access_token": page_access_token
        }
        conversation_response = requests.get(conversation_url, params=conversation_params).json()
        messages = conversation_response.get("data", [])

        # compute the analytics
        total_posts = len(posts)
        total_comments = sum(
            len(p.get("comments", {}).get("data", []))
            for p in posts
        )
        total_messages = sum(
            len(c.get("messages", {}).get("data", []))
            for c in messages
        )
        
        return {
            "page_id": page_id,
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_messages": total_messages,
        }

    
    @staticmethod
    async def analyze_competitors(key_words_list: List, page_access_token: str, max_pages: int = 5):
        GRAPH_URL = "https://graph.facebook.com/v23.0"
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