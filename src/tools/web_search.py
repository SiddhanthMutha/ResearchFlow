"""Web search tool using Tavily API."""

from typing import List, Dict, Any, Optional
import requests
from src.utils.config import config


class WebSearchTool:
    """Simple web search using Tavily API."""

    def __init__(self):
        self.api_key = config.TAVILY_API_KEY
        self.base_url = config.TAVILY_BASE_URL
        self.timeout = config.SEARCH_TIMEOUT
        self.max_results = config.MAX_SEARCH_RESULTS

    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search the web and return top results.

        Args:
            query: Search query string
            max_results: Maximum number of results (default: 5)

        Returns:
            List of search results with title, url, and snippet
        """
        if not self.api_key:
            return [{"error": "TAVILY_API_KEY not configured"}]

        if max_results is None:
            max_results = self.max_results

        try:
            response = requests.post(
                self.base_url,
                json={
                    "query": query,
                    "max_results": max_results,
                    "include_answer": True,
                    "include_raw_content": False,
                    "include_images": False
                },
                headers={
                    "Content-Type": "application/json"
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                    "score": item.get("score", 0)
                })

            # Also include the answer if available
            if data.get("answer"):
                results.insert(0, {
                    "title": "Quick Answer",
                    "url": "",
                    "snippet": data.get("answer", ""),
                    "score": 1.0,
                    "is_answer": True
                })

            return results

        except requests.Timeout:
            return [{"error": "Search timed out after 30 seconds"}]
        except requests.RequestException as e:
            return [{"error": f"Search failed: {str(e)}"}]
        except Exception as e:
            return [{"error": f"Unexpected error: {str(e)}"}]


# Singleton instance
web_search_tool = WebSearchTool()
