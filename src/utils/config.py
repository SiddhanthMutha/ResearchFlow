"""Configuration management for ResearchFlow."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE: float = 0.0

    # Tavily Search API
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    TAVILY_BASE_URL: str = "https://api.tavily.com/search"

    # SerpAPI (alternative)
    SERPAPI_API_KEY: Optional[str] = os.getenv("SERPAPI_API_KEY")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./research_history.db")

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Tool Settings
    SEARCH_TIMEOUT: int = 30  # seconds
    MAX_SEARCH_RESULTS: int = 5
    FETCH_TIMEOUT: int = 30  # seconds
    MAX_CONTEXT_MESSAGES: int = 10

    # Cost Tracking
    GPT4_INPUT_COST_PER_1K: float = 0.01  # $0.01 per 1K input tokens
    GPT4_OUTPUT_COST_PER_1K: float = 0.03  # $0.03 per 1K output tokens


config = Config()
