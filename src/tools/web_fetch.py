"""Web fetch tool for downloading and parsing web content."""

from typing import Dict, Any, Optional, List
import requests
from bs4 import BeautifulSoup
from src.utils.config import config


class WebFetchTool:
    """Download content from a URL and extract key information."""

    def __init__(self):
        self.timeout = config.FETCH_TIMEOUT

    def fetch(self, url: str) -> Dict[str, Any]:
        """
        Fetch content from a URL.

        Args:
            url: URL to fetch content from

        Returns:
            Dictionary with title, content, and metadata
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get title
            title = ""
            if soup.title:
                title = soup.title.string or ""
            elif soup.find("h1"):
                title = soup.find("h1").get_text(strip=True)

            # Get main content
            # Try to find the main content area
            main_content = soup.find("main") or soup.find("article") or soup.find("div", class_="content")
            if main_content:
                content = main_content.get_text(separator="\n", strip=True)
            else:
                # Fallback to body
                content = soup.body.get_text(separator="\n", strip=True) if soup.body else ""

            # Limit content length
            content = content[:10000] if len(content) > 10000 else content

            return {
                "url": url,
                "title": title,
                "content": content,
                "status": "success"
            }

        except requests.Timeout:
            return {
                "url": url,
                "error": f"Request timed out after {self.timeout} seconds",
                "status": "error"
            }
        except requests.RequestException as e:
            return {
                "url": url,
                "error": f"Failed to fetch: {str(e)}",
                "status": "error"
            }
        except Exception as e:
            return {
                "url": url,
                "error": f"Unexpected error: {str(e)}",
                "status": "error"
            }

    def fetch_multiple(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch content from multiple URLs.

        Args:
            urls: List of URLs to fetch

        Returns:
            List of results
        """
        results = []
        for url in urls:
            result = self.fetch(url)
            results.append(result)
        return results


# Singleton instance
web_fetch_tool = WebFetchTool()
