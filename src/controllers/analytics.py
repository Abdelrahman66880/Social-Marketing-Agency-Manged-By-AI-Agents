from typing import List, Dict, Any
import httpx
from fastapi import HTTPException
from ..helpers.config import get_Settings
import requests

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
        pass