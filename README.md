# Multi-Agent Research Assistant

**Version 1.1 | March 2026**

An AI-powered research assistant where multiple specialized agents work together to answer complex questions using LangGraph.

## Features

- **Multi-Agent System**: Four specialized agents work together
  - **Coordinator Agent**: Receives user question, breaks it into subtasks
  - **Search Agent**: Searches the web using Tavily API
  - **Reader Agent**: Fetches content from URLs and summarizes
  - **Writer Agent**: Combines all information into a coherent answer

- **Real-Time Progress**: WebSocket updates as agents work
- **Cost Tracking**: Track token usage and costs
- **Research History**: SQLite database for storing past research

## Prerequisites

- Python 3.9+
- OpenAI API key
- Tavily API key (for web search)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd research-assistant
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```

Edit `.env` with your keys:
```
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## Running the Server

Start the FastAPI server:
```bash
python -m uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Start a Research Query
```bash
POST /research
{
  "question": "What are the latest developments in quantum computing?"
}
```

Response:
```json
{
  "id": "uuid-of-research",
  "status": "started",
  "message": "Research task started..."
}
```

### Get Research Results
```bash
GET /research/{research_id}
```

### Get Research History
```bash
GET /research/history?limit=20&offset=0
```

### WebSocket for Real-Time Updates
```bash
ws://localhost:8000/ws/{research_id}
```

## Project Structure

```
research-assistant/
├── src/
│   ├── agents/           # Agent implementations
│   │   ├── coordinator.py
│   │   ├── search_agent.py
│   │   ├── reader_agent.py
│   │   └── writer_agent.py
│   ├── tools/            # Tool implementations
│   │   ├── web_search.py
│   │   ├── web_fetch.py
│   │   └── wikipedia.py
│   ├── graph/            # LangGraph workflow
│   │   └── workflow.py
│   ├── api/              # FastAPI server
│   │   ├── main.py
│   │   └── websocket.py
│   ├── memory/           # SQLite storage
│   │   └── storage.py
│   └── utils/            # Utilities
│       ├── config.py
│       └── cost_tracker.py
├── tests/                # Unit tests
│   ├── test_agents.py
│   ├── test_tools.py
│   └── test_workflow.py
├── requirements.txt
├── .env.example
└── README.md
```

## Testing

Run tests:
```bash
pytest tests/
```

## Example Usage

### Using cURL

```bash
# Start research
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"question": "What is quantum computing?"}'

# Get results (after completion)
curl http://localhost:8000/research/{research_id}
```

### Using Python

```python
import requests

# Start research
response = requests.post(
    "http://localhost:8000/research",
    json={"question": "What is quantum computing?"}
)
research_id = response.json()["id"]

# Get results
response = requests.get(f"http://localhost:8000/research/{research_id}")
print(response.json()["final_answer"])
```

## Architecture

```
User → FastAPI → Coordinator → Search → Reader → Writer → User
         ↓
      WebSocket (progress updates)
         ↓
       SQLite (history)
```

## Cost Tracking

The system tracks token usage for each agent and calculates costs based on OpenAI's pricing:

- GPT-4 Input: $0.01 per 1K tokens
- GPT-4 Output: $0.03 per 1K tokens

## Development

### Running in Development Mode

```bash
# With auto-reload
python -m uvicorn src.api.main:app --reload --reload-dir src

# With debug mode
python -m uvicorn src.api.main:app --reload --log-level debug
```

## License

MIT License
