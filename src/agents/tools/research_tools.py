from langchain_core.tools import tool
try:
    from langchain_community.tools.tavily_search import TavilySearchResults
except ImportError:
    TavilySearchResults = None

from src.helpers.config import get_Settings

@tool
def web_search_competitor(query: str) -> str:
    """
    Performs a live web search to find information about competitors or trends.
    Useful for 'Analysis' tasks.
    """
    if not TavilySearchResults:
        return "Error: langchain_community not installed or Tavily not configured."
        
    try:
        # Configuration is usually automatic via env vars (TAVILY_API_KEY)
        # But we can force it if needed
        search = TavilySearchResults(max_results=3)
        results = search.invoke(query)
        
        # Format results nicely
        formatted = "Search Results:\n"
        for res in results:
            formatted += f"- {res['content']} (Source: {res['url']})\n"
            
        return formatted
    except Exception as e:
        return f"Search failed: {str(e)}"
