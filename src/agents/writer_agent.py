"""Writer Agent - combines information into a coherent answer."""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

from src.utils.config import config


class WriterAgent:
    """Agent that combines all gathered information into a coherent answer."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            temperature=config.OPENAI_TEMPERATURE,
            api_key=config.OPENAI_API_KEY
        )

        self.system_prompt = """You are a research writer. Your job is to:
1. Combine information from multiple sources
2. Write a clear, coherent answer to the user's question
3. Cite sources when possible
4. Present information in a well-structured format

Guidelines:
- Start with a brief overview
- Organize information logically
- Include relevant details and facts
- End with a conclusion if appropriate
- Keep the answer focused and informative"""

    def run(
        self,
        question: str,
        search_results: List[Dict[str, Any]],
        summaries: List[Dict[str, Any]],
        wikipedia_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Combine all gathered information into a coherent answer.

        Args:
            question: Original research question
            search_results: Raw search results
            summaries: Summaries from the reader agent
            wikipedia_results: Wikipedia search results

        Returns:
            Dictionary with the final answer
        """
        try:
            # Build context from all sources
            context = self._build_context(
                question,
                search_results,
                summaries,
                wikipedia_results
            )

            # Generate final answer
            prompt = f"""Write a comprehensive answer to this research question:

Question: {question}

Context from various sources:
{context}

Provide a well-structured answer:"""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            final_answer = response.content.strip()

            return {
                "question": question,
                "final_answer": final_answer,
                "sources": self._collect_sources(summaries, wikipedia_results),
                "agent": "WriterAgent",
                "status": "success"
            }

        except Exception as e:
            return {
                "question": question,
                "final_answer": f"An error occurred while generating the answer: {str(e)}",
                "sources": [],
                "agent": "WriterAgent",
                "status": "error",
                "error": str(e)
            }

    def _build_context(
        self,
        question: str,
        search_results: List[Dict[str, Any]],
        summaries: List[Dict[str, Any]],
        wikipedia_results: List[Dict[str, Any]]
    ) -> str:
        """Build context string from all sources."""
        context_parts = []

        # Add Wikipedia results
        if wikipedia_results:
            context_parts.append("=== WIKIPEDIA ===")
            for wiki in wikipedia_results[:3]:
                context_parts.append(f"\n{wiki.get('title', '')}")
                context_parts.append(f"Summary: {wiki.get('summary', '')}")

        # Add web search summaries
        if summaries:
            context_parts.append("\n=== WEB SUMMARIES ===")
            for summary in summaries:
                context_parts.append(f"\n{summary.get('title', '')}")
                context_parts.append(f"URL: {summary.get('url', '')}")
                context_parts.append(f"Summary: {summary.get('summary', '')}")

        # Add quick answers from search
        for result in search_results:
            if result.get("is_answer"):
                context_parts.append(f"\n=== QUICK ANSWER ===")
                context_parts.append(result.get("snippet", ""))

        return "\n".join(context_parts)[:8000]  # Limit context length

    def _collect_sources(
        self,
        summaries: List[Dict[str, Any]],
        wikipedia_results: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Collect unique sources."""
        sources = []

        # Add Wikipedia sources
        for wiki in wikipedia_results[:3]:
            if wiki.get("url"):
                sources.append({
                    "title": wiki.get("title", ""),
                    "url": wiki.get("url", "")
                })

        # Add web sources
        for summary in summaries[:5]:
            if summary.get("url"):
                sources.append({
                    "title": summary.get("title", ""),
                    "url": summary.get("url", "")
                })

        # Remove duplicates
        seen_urls = set()
        unique_sources = []
        for source in sources:
            if source["url"] not in seen_urls:
                seen_urls.add(source["url"])
                unique_sources.append(source)

        return unique_sources


# Singleton instance
writer_agent = WriterAgent()
