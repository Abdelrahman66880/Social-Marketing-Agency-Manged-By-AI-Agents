import requests
from fastapi import HTTPException
from src.helpers.config import get_Settings

class FacebookAuthService:
    @staticmethod
    def exchange_token(short_lived_token: str) -> str:
        """
        Exchanges a short-lived User or Page access token for a long-lived one.
        
        Args:
            short_lived_token (str): The short-lived access token.
            
        Returns:
            str: The long-lived access token.
            
        Raises:
            HTTPException: If the exchange fails.
        """
        settings = get_Settings()
        
        url = "https://graph.facebook.com/v23.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": settings.FACEBOOK_APP_ID,
            "client_secret": settings.FACEBOOK_APP_SECRET,
            "fb_exchange_token": short_lived_token
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if "error" in data:
                error_msg = data["error"].get("message", "Unknown Facebook Error")
                raise HTTPException(status_code=400, detail=f"Token exchange failed: {error_msg}")
                
            return data.get("access_token")
            
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Network error during token exchange: {str(e)}")
