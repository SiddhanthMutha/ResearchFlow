"""Wikipedia tool for looking up encyclopedia articles."""

from typing import Dict, Any, Optional, List
import wikipedia
from src.utils.config import config


class WikipediaTool:
    """Look up Wikipedia articles and extract key information."""

    def __init__(self):
        # Set language to English
        wikipedia.set_lang("en")

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search Wikipedia for articles.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results with title and summary
        """
        try:
            search_results = wikipedia.search(query, results=max_results)
            results = []

            for title in search_results:
                try:
                    page = wikipedia.page(title)
                    results.append({
                        "title": page.title,
                        "url": page.url,
                        "summary": page.summary[:500],  # Limit summary length
                        "content": page.content[:5000]  # Limit content length
                    })
                except wikipedia.exceptions.DisambiguationError as e:
                    # Handle disambiguation pages
                    results.append({
                        "title": e.title,
                        "url": "",
                        "summary": f"Disambiguation page. Options: {', '.join(e.options[:5])}",
                        "content": ""
                    })
                except wikipedia.exceptions.PageError:
                    continue
                except Exception:
                    continue

            return results

        except Exception as e:
            return [{"error": f"Wikipedia search failed: {str(e)}"}]

    def get_article(self, title: str) -> Dict[str, Any]:
        """
        Get a specific Wikipedia article.

        Args:
            title: Article title

        Returns:
            Dictionary with article content
        """
        try:
            page = wikipedia.page(title)
            return {
                "title": page.title,
                "url": page.url,
                "summary": page.summary,
                "content": page.content[:10000],  # Limit content length
                "status": "success"
            }
        except wikipedia.exceptions.DisambiguationError as e:
            return {
                "title": e.title,
                "url": "",
                "summary": f"Disambiguation page. Options: {', '.join(e.options[:5])}",
                "content": "",
                "status": "disambiguation"
            }
        except wikipedia.exceptions.PageError:
            return {
                "title": title,
                "error": "Page not found",
                "status": "error"
            }
        except Exception as e:
            return {
                "title": title,
                "error": f"Failed to fetch article: {str(e)}",
                "status": "error"
            }

    def get_summary(self, query: str) -> str:
        """
        Get a quick summary for a query.

        Args:
            query: Search query

        Returns:
            Summary text
        """
        try:
            summary = wikipedia.summary(query, sentences=3)
            return summary
        except Exception as e:
            return f"Failed to get summary: {str(e)}"


# Singleton instance
wikipedia_tool = WikipediaTool()
