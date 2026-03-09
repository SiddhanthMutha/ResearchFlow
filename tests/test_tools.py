"""Tests for the tools."""

import pytest
from unittest.mock import Mock, patch


class TestWebSearchTool:
    """Tests for the web search tool."""

    def test_web_search_initialization(self):
        """Test web search tool can be initialized."""
        from src.tools.web_search import WebSearchTool
        tool = WebSearchTool()
        assert tool is not None

    @patch('requests.post')
    def test_search_success(self, mock_post):
        """Test successful search."""
        from src.tools.web_search import WebSearchTool
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"title": "Test", "url": "http://test.com", "content": "Test content"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        tool = WebSearchTool()
        results = tool.search("test query")
        
        assert len(results) > 0

    def test_search_no_api_key(self):
        """Test search with no API key."""
        from src.tools.web_search import WebSearchTool
        
        with patch('src.tools.web_search.config') as mock_config:
            mock_config.TAVILY_API_KEY = None
            
            tool = WebSearchTool()
            results = tool.search("test")
            
            assert "error" in results[0]


class TestWebFetchTool:
    """Tests for the web fetch tool."""

    def test_web_fetch_initialization(self):
        """Test web fetch tool can be initialized."""
        from src.tools.web_fetch import WebFetchTool
        tool = WebFetchTool()
        assert tool is not None

    @patch('requests.get')
    def test_fetch_success(self, mock_get):
        """Test successful fetch."""
        from src.tools.web_fetch import WebFetchTool
        
        mock_response = Mock()
        mock_response.content = b"<html><body>Test content</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        tool = WebFetchTool()
        result = tool.fetch("http://test.com")
        
        assert result["status"] == "success"

    @patch('requests.get')
    def test_fetch_timeout(self, mock_get):
        """Test fetch timeout."""
        from src.tools.web_fetch import WebFetchTool
        import requests
        
        mock_get.side_effect = requests.Timeout()

        tool = WebFetchTool()
        result = tool.fetch("http://test.com")
        
        assert "error" in result


class TestWikipediaTool:
    """Tests for the Wikipedia tool."""

    def test_wikipedia_initialization(self):
        """Test Wikipedia tool can be initialized."""
        from src.tools.wikipedia import WikipediaTool
        tool = WikipediaTool()
        assert tool is not None
