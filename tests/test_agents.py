"""Tests for the agents."""

import pytest
from unittest.mock import Mock, patch


class TestSearchAgent:
    """Tests for the search agent."""

    @patch('src.agents.search_agent.ChatOpenAI')
    def test_search_agent_initialization(self, mock_llm):
        """Test search agent can be initialized."""
        from src.agents.search_agent import SearchAgent
        
        with patch('src.agents.search_agent.config') as mock_config:
            mock_config.OPENAI_MODEL = "gpt-4"
            mock_config.OPENAI_TEMPERATURE = 0.0
            mock_config.OPENAI_API_KEY = "test-key"
            
            agent = SearchAgent()
            assert agent is not None


class TestReaderAgent:
    """Tests for the reader agent."""

    @patch('src.agents.reader_agent.ChatOpenAI')
    def test_reader_agent_initialization(self, mock_llm):
        """Test reader agent can be initialized."""
        from src.agents.reader_agent import ReaderAgent
        
        with patch('src.agents.reader_agent.config') as mock_config:
            mock_config.OPENAI_MODEL = "gpt-4"
            mock_config.OPENAI_TEMPERATURE = 0.0
            mock_config.OPENAI_API_KEY = "test-key"
            
            agent = ReaderAgent()
            assert agent is not None


class TestWriterAgent:
    """Tests for the writer agent."""

    @patch('src.agents.writer_agent.ChatOpenAI')
    def test_writer_agent_initialization(self, mock_llm):
        """Test writer agent can be initialized."""
        from src.agents.writer_agent import WriterAgent
        
        with patch('src.agents.writer_agent.config') as mock_config:
            mock_config.OPENAI_MODEL = "gpt-4"
            mock_config.OPENAI_TEMPERATURE = 0.0
            mock_config.OPENAI_API_KEY = "test-key"
            
            agent = WriterAgent()
            assert agent is not None


class TestCoordinatorAgent:
    """Tests for the coordinator agent."""

    @patch('src.agents.coordinator.ChatOpenAI')
    def test_coordinator_agent_initialization(self, mock_llm):
        """Test coordinator agent can be initialized."""
        from src.agents.coordinator import CoordinatorAgent
        
        with patch('src.agents.coordinator.config') as mock_config:
            mock_config.OPENAI_MODEL = "gpt-4"
            mock_config.OPENAI_TEMPERATURE = 0.0
            mock_config.OPENAI_API_KEY = "test-key"
            
            agent = CoordinatorAgent()
            assert agent is not None
