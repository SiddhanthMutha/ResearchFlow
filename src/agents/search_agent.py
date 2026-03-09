"""Search Agent - searches the web for information."""

from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from src.tools.web_search import web_search_tool
from src.tools.wikipedia import wikipedia_tool
from src.utils.config import config


class SearchAgent:
    """Agent that searches the web for information."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            temperature=config.OPENAI_TEMPERATURE,
            api_key=config.OPENAI_API_KEY
        )
        self.search_tool = web_search_tool
        self.wikipedia_tool = wikipedia_tool

        self.system_prompt = """You are a search expert. Your job is to:
1. Understand the user's question
2. Create an effective search query that will find relevant information
3. Use the search tool to find relevant information
4. Return the top results

Guidelines:
- Keep search queries concise and focused
- Prioritize recent information when appropriate
- Look for authoritative sources
- Return search results in a structured format

Return your response as a JSON object with:
- "query": The search query used
- "results": The search results from the tool"""

    def run(self, question: str, use_wikipedia: bool = True) -> Dict[str, Any]:
        """
        Process a question and return search results.

        Args:
            question: User's research question
            use_wikipedia: Whether to also search Wikipedia

        Returns:
            Dictionary with search query and results
        """
        try:
            # Create search query using LLM
            query_prompt = f"""Create a concise search query for this question: {question}

Respond with just the search query, nothing else."""

            query_response = self.llm.invoke([HumanMessage(content=query_prompt)])
            search_query = query_response.content.strip()

            # Execute web search
            search_results = self.search_tool.search(search_query)

            # Also search Wikipedia if requested
            wiki_results = []
            if use_wikipedia:
                try:
                    wiki_results = self.wikipedia_tool.search(search_query)
                except Exception:
                    pass

            return {
                "query": search_query,
                "search_results": search_results,
                "wikipedia_results": wiki_results,
                "agent": "SearchAgent",
                "status": "success"
            }

        except Exception as e:
            return {
                "query": "",
                "search_results": [],
                "wikipedia_results": [],
                "agent": "SearchAgent",
                "status": "error",
                "error": str(e)
            }


# Singleton instance
search_agent = SearchAgent()
