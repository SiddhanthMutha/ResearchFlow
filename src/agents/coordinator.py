"""Coordinator Agent - manages the research workflow."""

from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

from src.utils.config import config


class CoordinatorAgent:
    """Agent that coordinates the research workflow and routes tasks."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            temperature=config.OPENAI_TEMPERATURE,
            api_key=config.OPENAI_API_KEY
        )

        self.system_prompt = """You are the Coordinator of a research team. Your job is to:
1. Understand the user's research question
2. Break it down into subtasks
3. Decide which agents to use and in what order

The available agents are:
- SearchAgent: Searches the web for information
- ReaderAgent: Reads content from URLs and summarizes
- WriterAgent: Combines all information into a coherent answer

For version 1, the workflow is simple:
START → Coordinator → SearchAgent → ReaderAgent → WriterAgent → END

Your role is to:
- Validate the question is clear and answerable
- Pass the question to the SearchAgent first
- Monitor progress through the workflow"""

    def run(self, question: str) -> Dict[str, Any]:
        """
        Process the initial question and prepare for agent workflow.

        Args:
            question: User's research question

        Returns:
            Dictionary with task breakdown
        """
        try:
            # Validate and clarify the question
            prompt = f"""Analyze this research question and confirm it's ready for processing:

Question: {question}

Respond with a JSON object containing:
- "valid": boolean - whether the question is answerable
- "clarified_question": string - the question to use (may add context)
- "task_breakdown": array of strings - the subtasks to complete
- "estimated_sources": integer - estimated number of sources needed"""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Try to parse as JSON
            try:
                import json
                # Extract JSON from response
                content = response.content
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                result = json.loads(content.strip())
                
                return {
                    "original_question": question,
                    "clarified_question": result.get("clarified_question", question),
                    "task_breakdown": result.get("task_breakdown", []),
                    "estimated_sources": result.get("estimated_sources", 5),
                    "agent": "CoordinatorAgent",
                    "status": "success"
                }
            except (json.JSONDecodeError, AttributeError):
                # Fallback if JSON parsing fails
                return {
                    "original_question": question,
                    "clarified_question": question,
                    "task_breakdown": [
                        "Search for relevant information",
                        "Read and summarize key sources",
                        "Write comprehensive answer"
                    ],
                    "estimated_sources": 5,
                    "agent": "CoordinatorAgent",
                    "status": "success"
                }

        except Exception as e:
            return {
                "original_question": question,
                "clarified_question": question,
                "task_breakdown": [],
                "estimated_sources": 5,
                "agent": "CoordinatorAgent",
                "status": "error",
                "error": str(e)
            }

    def plan_research(self, question: str) -> Dict[str, Any]:
        """
        Create a detailed research plan.

        Args:
            question: User's research question

        Returns:
            Dictionary with research plan
        """
        try:
            prompt = f"""Create a detailed research plan for this question:

Question: {question}

Consider:
- What information is needed
- What sources would be most helpful
- What angles to cover

Respond with a JSON object:
- "search_queries": array of strings - suggested search queries
- "key_topics": array of strings - topics to cover
- "sources_needed": array of strings - types of sources"""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            try:
                import json
                content = response.content
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                result = json.loads(content.strip())
                return {
                    "question": question,
                    "plan": result,
                    "agent": "CoordinatorAgent",
                    "status": "success"
                }
            except:
                return {
                    "question": question,
                    "plan": {},
                    "agent": "CoordinatorAgent",
                    "status": "success"
                }

        except Exception as e:
            return {
                "question": question,
                "plan": {},
                "agent": "CoordinatorAgent",
                "status": "error",
                "error": str(e)
            }


# Singleton instance
coordinator_agent = CoordinatorAgent()
