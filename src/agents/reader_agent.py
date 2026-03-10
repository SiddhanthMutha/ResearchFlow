"""Reader Agent - fetches and summarizes content from URLs."""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from src.tools.web_fetch import web_fetch_tool
from src.utils.config import config


class ReaderAgent:
    """Agent that fetches content from URLs and extracts key information."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            temperature=config.OPENAI_TEMPERATURE,
            api_key=config.OPENAI_API_KEY
        )
        self.fetch_tool = web_fetch_tool

        self.system_prompt = """You are a research assistant specialized in reading and summarizing content.
Your job is to:
1. Read content from provided URLs
2. Extract key information relevant to the user's question
3. Summarize findings in a clear, concise manner

Guidelines:
- Focus on information relevant to the research question
- Note important facts, statistics, and key points
- Identify any contradictions or differing viewpoints
- Keep summaries concise but informative"""

    def run(self, search_results: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        """
        Read content from URLs and extract key information.

        Args:
            search_results: List of search results with URLs
            question: Original research question

        Returns:
            Dictionary with fetched content and summaries
        """
        try:
            # Extract URLs from search results
            urls = []
            for result in search_results:
                if result.get("url") and not result.get("is_answer"):
                    urls.append(result["url"])

            # Limit to top 5 URLs
            urls = urls[:5]

            if not urls:
                return {
                    "fetched_content": [],
                    "summaries": [],
                    "agent": "ReaderAgent",
                    "status": "success",
                    "message": "No URLs to fetch"
                }

            # Fetch content from URLs
            fetched_content = self.fetch_tool.fetch_multiple(urls)

            # Filter successful fetches
            successful_content = [
                content for content in fetched_content
                if content.get("status") == "success"
            ]

            # Generate summaries using LLM
            summaries = []
            for content in successful_content:
                if content.get("content"):
                    summary = self._summarize_content(
                        content["content"],
                        content.get("title", ""),
                        question
                    )
                    summaries.append({
                        "title": content.get("title", ""),
                        "url": content.get("url", ""),
                        "summary": summary
                    })

            return {
                "fetched_content": successful_content,
                "summaries": summaries,
                "agent": "ReaderAgent",
                "status": "success"
            }

        except Exception as e:
            return {
                "fetched_content": [],
                "summaries": [],
                "agent": "ReaderAgent",
                "status": "error",
                "error": str(e)
            }

    def _summarize_content(self, content: str, title: str, question: str) -> str:
        """Generate a summary of the content relevant to the question."""
        try:
            prompt = f"""Based on the following content from "{title}", 
provide a summary relevant to this question: {question}

Content:
{content[:3000]}

Summary (2-3 sentences):"""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()

        except Exception:
            # Return truncated content if summarization fails
            return content[:500] + "..." if len(content) > 500 else content


# Singleton instance
reader_agent = ReaderAgent()
