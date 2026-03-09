# Product Requirements Document

## Multi-Agent Research Assistant

**Version 1.0 | March 2025**

---

## 1. Project Overview

Build an AI-powered research assistant where multiple specialized agents work together to answer complex questions. Think of it like a research team where each member has a specific job: one searches the web, another reads documents, another writes summaries, and a coordinator manages everything.

### Goals

- Create a working multi-agent system using LangGraph
- Implement safe tool usage with basic error handling
- Build a simple API that shows real-time progress
- Track costs and performance metrics

---

## 2. Technology Stack

### Core Technologies

- **LangGraph**: For agent workflow orchestration
- **OpenAI GPT-4**: Primary language model
- **FastAPI**: Web framework for the API
- **SQLite**: Simple database for storing research history

### External APIs

- **Tavily or SerpAPI**: For web search
- **Wikipedia API**: For encyclopedia content
- **arXiv API**: For academic papers (optional for v1)

---

## 3. System Architecture

### The Four Agents (Start Simple)

1. **Coordinator Agent**: Receives user question, breaks it into subtasks, decides which agents to use
2. **Search Agent**: Searches the web using Tavily/SerpAPI, returns top 5 relevant results
3. **Reader Agent**: Reads content from URLs, extracts key information, summarizes findings
4. **Writer Agent**: Takes all gathered information and writes a coherent answer

### Agent Workflow (LangGraph Flow)

```
START → Coordinator → Search Agent → Reader Agent → Writer Agent → END
```

**Note:** Keep this simple initially. No loops or validation steps in version 1. Just a straight path through the agents.

---

## 4. Core Features (MVP)

### Feature 1: Basic Tool System

Create simple, safe tools that agents can use:

- **Web Search Tool**: Query Tavily API, return top results
- **Web Fetch Tool**: Download content from a URL (with timeout)
- **Wikipedia Tool**: Look up Wikipedia articles

**Safety Requirements:**

- Add 30-second timeout to all web requests
- Limit search results to max 5 items
- Basic error handling (try/except blocks, return error message)

### Feature 2: Simple Memory System

- Store the current conversation in a Python dictionary (in-memory for now)
- Keep the last 10 messages to provide context to agents
- Save completed research to SQLite database with: query, timestamp, final answer, cost

### Feature 3: Real-Time Progress Updates

Show users what's happening as agents work. Use FastAPI WebSockets to send status updates:

- Which agent is currently active
- What task they're performing
- Progress percentage (estimate)

**Example WebSocket message:**
```json
{
  "agent": "SearchAgent",
  "status": "running",
  "message": "Found 5 relevant articles",
  "progress": 0.4,
  "timestamp": "2025-03-09T10:23:15Z"
}
```

### Feature 4: Cost Tracking

Track how much each research query costs:

- Count tokens used by each agent
- Calculate cost based on OpenAI pricing
- Store in database for later analysis
- Display total cost to user after each query

---

## 5. Project Structure

```
research-assistant/
├── src/
│   ├── agents/
│   │   ├── coordinator.py
│   │   ├── search_agent.py
│   │   ├── reader_agent.py
│   │   └── writer_agent.py
│   ├── tools/
│   │   ├── web_search.py
│   │   ├── web_fetch.py
│   │   └── wikipedia.py
│   ├── graph/
│   │   └── workflow.py      # LangGraph flow definition
│   ├── api/
│   │   ├── main.py          # FastAPI server
│   │   └── websocket.py     # Real-time updates
│   ├── memory/
│   │   └── storage.py       # SQLite operations
│   └── utils/
│       ├── cost_tracker.py
│       └── config.py
├── tests/
│   ├── test_agents.py
│   └── test_tools.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 6. API Endpoints (Keep Simple)

- **POST /research**: Start a new research query
- **GET /research/{id}**: Get results of a completed query
- **GET /research/history**: List past research queries
- **WebSocket /ws**: Real-time progress updates

---

## 7. Implementation Phases

### Phase 1: Basic Setup (Week 1)

1. Set up project structure and install dependencies
2. Create basic FastAPI server
3. Implement simple web search tool
4. Test tool with direct API calls

### Phase 2: Build Individual Agents (Week 2-3)

1. Create Search Agent (uses web search tool)
2. Create Reader Agent (fetches and summarizes URLs)
3. Create Writer Agent (combines information into answer)
4. Test each agent independently

### Phase 3: Connect with LangGraph (Week 4)

1. Create LangGraph workflow connecting all agents
2. Add Coordinator Agent to route tasks
3. Test end-to-end flow with sample queries

### Phase 4: Add Features (Week 5)

1. Implement SQLite storage
2. Add WebSocket for real-time updates
3. Implement cost tracking

### Phase 5: Polish & Deploy (Week 6)

1. Add error handling and logging
2. Write tests for critical paths
3. Create Dockerfile for easy deployment
4. Write comprehensive README with examples

---

## 8. Key Concepts to Learn

### LangGraph Basics

- Understanding state machines and nodes
- How to pass state between agents
- Creating conditional edges (for later versions)

### Tool Design

- How to structure tool inputs/outputs
- Adding timeouts and error handling
- Rate limiting basics (simple counter works fine)

### Agent Prompting

- Writing clear system prompts for each agent role
- Keeping context concise to save tokens
- Formatting outputs for the next agent

---

## 9. Success Criteria

The project is successful if it can:

- Answer a complex question like "What are the latest developments in quantum computing?" by searching multiple sources
- Show real-time progress as agents work
- Complete a research task in under 2 minutes
- Handle errors gracefully (bad URLs, API failures, etc.)
- Cost less than $0.10 per query on average

---

## 10. What We Simplified

This PRD simplifies the original project for beginners. Here's what we removed or postponed:

- **Removed**: Redis, Celery, Kubernetes, Prometheus/Grafana - too complex for now
- **Simplified**: Using SQLite instead of PostgreSQL
- **Postponed**: Critic Agent and validation loops - add in v2
- **Postponed**: arXiv paper reading - focus on web search first
- **Postponed**: Advanced memory with context pruning - simple is fine for v1

---

## 11. Next Steps After Reading This PRD

1. Set up a Python virtual environment
2. Install LangGraph, LangChain, FastAPI, and OpenAI SDK
3. Get API keys for OpenAI and Tavily
4. Follow the implementation phases starting with Phase 1
5. Start with the web search tool - get that working first before building agents

---

## Example Tool Implementation

Here's what a simple web search tool might look like:

```python
import os
from typing import List, Dict
import requests

class WebSearchTool:
    """Simple web search using Tavily API"""
    
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com/search"
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search the web and return top results
        
        Args:
            query: Search query string
            max_results: Maximum number of results (default: 5)
            
        Returns:
            List of search results with title, url, and snippet
        """
        try:
            response = requests.post(
                self.base_url,
                json={
                    "query": query,
                    "max_results": max_results
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30  # 30 second timeout
            )
            response.raise_for_status()
            return response.json().get("results", [])
            
        except requests.Timeout:
            return {"error": "Search timed out after 30 seconds"}
        except requests.RequestException as e:
            return {"error": f"Search failed: {str(e)}"}
```

---

## Example Agent Structure

Here's what a simple agent might look like:

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class SearchAgent:
    """Agent that searches the web for information"""
    
    def __init__(self, search_tool):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.search_tool = search_tool
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a search expert. Your job is to:
            1. Understand the user's question
            2. Create an effective search query
            3. Use the search tool to find relevant information
            4. Return the top results
            
            Keep search queries concise and focused."""),
            ("user", "{question}")
        ])
    
    def run(self, question: str) -> dict:
        """
        Process a question and return search results
        
        Args:
            question: User's research question
            
        Returns:
            Dictionary with search query and results
        """
        # Generate search query
        response = self.llm.invoke(
            self.prompt.format_messages(question=question)
        )
        search_query = response.content
        
        # Execute search
        results = self.search_tool.search(search_query)
        
        return {
            "query": search_query,
            "results": results,
            "agent": "SearchAgent"
        }
```

---

## Dependencies (requirements.txt)

```
# Core
langgraph>=0.0.40
langchain>=0.1.0
langchain-openai>=0.0.5
openai>=1.0.0

# API
fastapi>=0.109.0
uvicorn>=0.27.0
websockets>=12.0
python-multipart>=0.0.6

# Tools
requests>=2.31.0
beautifulsoup4>=4.12.0
wikipedia>=1.4.0

# Storage
aiosqlite>=0.19.0

# Utils
python-dotenv>=1.0.0
pydantic>=2.5.0
```

---

_Remember: Start small, test often, and add complexity gradually. You've got this!_
