from langchain_core.tools import tool
from typing import Optional, Dict, List
import requests
from src.helpers.config import get_Settings 
from datetime import datetime

# ==============================================================================
# CONFIG & HELPERS
# ==============================================================================
# In a real app, you might inject the base URL or API client helper
API_BASE_URL = get_Settings().API_BASE_URL

def _make_api_call(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
    """
    Helper to communicate with our own Backend API from the Agent.

    Args:
        method (str): The HTTP method to use (e.g., 'GET', 'POST', 'PUT').
        endpoint (str): The API endpoint path (should start with '/').
        data (Optional[Dict]): The JSON payload for the request (used in POST/PUT). Defaults to None.
        params (Optional[Dict]): Query parameters for the request (used in GET). Defaults to None.

    Returns:
        Dict: A dictionary containing the JSON response from the API. 
              If an error occurs (network, status code, or JSON parsing), returns a dictionary with 'error' or 'status_code' keys.

    Raises:
        None: This function catches all exceptions and returns an error dictionary.
    """
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        else:
            return {"error": "Unsupported method"}
        
        # We return the JSON even if it's an error code, so the Agent can "see" the error
        try:
            return response.json()
        except:
            return {"status_code": response.status_code, "text": response.text}
    except Exception as e:
        return {"error": f"API Call Failed: {str(e)}"}

# ==============================================================================
# SYSTEM AWARENESS (RETRIEVAL) TOOLS
# ==============================================================================

@tool
def get_brand_voice_context(user_id: str) -> str:
    """
    Retrieves the Brand's Persona, Goals, and Tone.
    Use this to ensure all generated content matches the user's specific business voice.
    It fetches merely all business info except sensitive IDs.

    Args:
        user_id (str): The ID of the owner/user using the agents.

    Returns:
        str: A structured string describing the brand's tone, about section, target audience, goals, and more.
             Returns a friendly error message if the brand info is not found.

    Raises:
        None: Underlying API errors are handled and returned as string messages.
    """
    endpoint = f"/business-info/users/{user_id}"
    data = _make_api_call("GET", endpoint)
    
    if "detail" in data and "Not Found" in str(data["detail"]):
        return "No Brand Info found. Ask the user to fill out their Business Profile first."
        
    # Format essential info for the LLM
    business_name = data.get("businessName", "N/A")
    field = data.get("field", "N/A")
    description = data.get("description", "")
    themes = ", ".join(data.get("theme", []))
    long_term_goals = ", ".join(data.get("longTermGoals", []))
    short_term_goals = ", ".join(data.get("shortTermGoals", []))
    target_audience = ", ".join(data.get("targetAudience", []))
    differentiators = ", ".join(data.get("differentiators", []))
    keywords = ", ".join(data.get("businessKeyWords", []))
    resources = data.get("availableResources", [])
    
    resources_str = ""
    if resources:
        resources_list = [f"- {r.get('name')}: {r.get('description', '')}" for r in resources]
        resources_str = "\n".join(resources_list)
    else:
        resources_str = "None listed"
    
    return f"""
    BRAND CONTEXT:
    - Business Name: {business_name}
    - Field: {field}
    - Description: {description}
    - Themes/Tone: {themes}
    - Target Audience: {target_audience}
    - Unique Differentiators: {differentiators}
    - Key Goals (Long Term): {long_term_goals}
    - Key Goals (Short Term): {short_term_goals}
    - Business Keywords: {keywords}
    - Available Resources:
    {resources_str}
    """

@tool
def check_content_calendar(user_id: str) -> str:
    """
    Checks the schedule to see planned posting times. 
    NOTE: The model will not schedule automatically; the schedule is manual or by request. 
    Use this tool to SEE the schedule of the user and avoid conflicts.

    Args:
        user_id (str): The ID of the owner/user for whom to check the schedule.

    Returns:
        str: A formatted string listing the weekly schedule and posting times.
             Returns an error message if the schedule cannot be fetched.

    Raises:
        None: API errors are caught and returned as error strings.
    """
    endpoint = f"/schedule/users/{user_id}"
    data = _make_api_call("GET", endpoint)
    
    if "detail" in data:
        return f"Could not fetch schedule: {data['detail']}"
        
    days = data.get("schedules", [])
    summary = []
    for day in days:
        if day.get("is_active"):
            times = ", ".join(day.get("post_times", []))
            summary.append(f"{day['day']}: {times}")
            
    return "Weekly Schedule:\n" + "\n".join(summary)

@tool
def review_past_performance(user_id: str, limit: int = 5, skip: int = 0) -> str:
    """
    Retrieves analysis of past posts to see what worked well.
    Use this to make data-driven decisions for new content.

    Args:
        user_id (str): The ID of the owner/user whose performance data is being requested.
        limit (int): The number of records to retrieve. Defaults to 5.
        skip (int): The number of records to skip. Defaults to 0.

    Returns:
        str: A summary string of recent posts including their IDs, likes, and comments.
             Returns a message indicating no data is available if the response is not a list.

    Raises:
        None: API errors are caught and returned as error strings.
    """
    endpoint = f"/analytics/users/{user_id}/analysis/interaction/{limit}/{skip}"
    data = _make_api_call("GET", endpoint)
    
    if isinstance(data, list):
        summary = "Recent Performance Insights:\n"
        for item in data:
            metrics = item.get("metrics", {})
            summary += f"- Post (ID: {item.get('post_id')}): Likes={metrics.get('likes',0)}, Comments={metrics.get('comments',0)}\n"
        return summary
    return "No past performance data available."

@tool
def check_draft_status(user_id: str, limit: int = 100, skip: int = 0) -> int:
    """
    Checks how many drafts are currently waiting for approval.

    Args:
        user_id (str): The ID of the owner/user to check drafts for.
        limit (int): The number of drafts to retrieve to count. Defaults to 100.
        skip (int): The number of drafts to skip. Defaults to 0.

    Returns:
        int: The number of drafts currently pending approval.
             Returns 0 if no drafts are found or if the API call fails/returns unexpected data.

    Raises:
        None: API errors result in a return value of 0.
    """
    endpoint = f"/drafts/users/{user_id}/{limit}/{skip}"
    data = _make_api_call("GET", endpoint)
    
    if isinstance(data, list):
        return len(data)
    return 0

# ==============================================================================
# ACTION TOOLS (EFFECTING CHANGE)
# ==============================================================================

@tool
def create_draft_post(user_id: str, title: str, content: str) -> str:
    """
    Creates a new Social Media Post DRAFT.
    NOTE: This does NOT publish to Facebook. It sends it to the user for approval.

    Args:
        user_id (str): The owner ID.
        title (str): Internal title for the draft.
        content (str): The actual text copy for the post.

    Returns:
        str: A success message including the new draft ID if successful.
             Returns a failure message with error details if the creation fails.

    Raises:
        None: API errors are caught and returned as error strings.
    """
    endpoint = "/drafts/"
    payload = {
        "user_id": user_id,
        "title": title,
        "content": content
    }
    response = _make_api_call("POST", endpoint, data=payload)
    
    if "id" in response:
        return f"SUCCESS: Draft created with ID {response['id']}. Tell the user to review it."
    return f"FAILED to create draft. Error: {response}"

@tool
def send_customer_response(page_id: str, recipient_id: str, message: str) -> str:
    """
    Sends a direct reply to a customer via Facebook Messenger.
    ONLY use this if you are confident the answer is correct or if it's a general greeting.

    Args:
        page_id (str): The Facebook Page ID.
        recipient_id (str): The user's PSID (Page-Scoped ID).
        message (str): The text content of the reply message.

    Returns:
        str: A success message if the response has a 'recipient_id'.
             Returns a failure message with error details otherwise.

    Raises:
        None: API errors are caught and returned as error strings.
    """
    endpoint = f"/facebook/pages/{page_id}/messages/{recipient_id}/reply"
    payload = {
        "reply_text": message,
        "message_type": "RESPONSE"
    }
    response = _make_api_call("POST", endpoint, data=payload)
    
    if "recipient_id" in response:
        return "SUCCESS: Message sent."
    return f"FAILED to send message. Error: {response}"

@tool
def save_market_analysis(user_id: str, topic: str, content: str) -> str:
    """
    Saves a research/analysis report to the database for future reference.
    """
    endpoint = "/analytics/analysis"
    payload = {
        "user_id": user_id,
        "type": "COMPETITOR", # Could be dynamic
        "content": content,
        "metrics": {"topic": topic}
    }
    response = _make_api_call("POST", endpoint, data=payload)
    
    if "id" in response:
        return "Analysis saved to memory."
    return "Failed to save analysis."

@tool
def save_strategic_recommendation(user_id: str, title: str, content: str) -> str:
    """
    Saves a formal Strategic Recommendation to the database.
    Use this when you want to suggest actionable steps to the user (e.g., "Post more videos").
    """
    endpoint = "/analytics/recommendations"
    payload = {
        "user_id": user_id,
        "title": title,
        "content": content
    }
    response = _make_api_call("POST", endpoint, data=payload)
    
    if "id" in response:
        return f"Recommendation '{title}' saved."
    return "Failed to save recommendation."

