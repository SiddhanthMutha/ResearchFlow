"""LangGraph workflow for the multi-agent research assistant."""

from typing import TypedDict, List, Dict, Any, Optional, Callable
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from src.agents.coordinator import coordinator_agent
from src.agents.search_agent import search_agent
from src.agents.reader_agent import reader_agent
from src.agents.writer_agent import writer_agent


class ResearchState(TypedDict):
    """State for the research workflow."""
    question: str
    clarified_question: str
    search_query: str
    search_results: List[Dict[str, Any]]
    wikipedia_results: List[Dict[str, Any]]
    summaries: List[Dict[str, Any]]
    final_answer: str
    sources: List[Dict[str, str]]
    progress: float
    current_agent: str
    status: str
    error: Optional[str]
    messages: List[Dict[str, str]]


def create_research_graph() -> StateGraph:
    """Create the LangGraph workflow for research."""
    
    # Define the graph
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("search", search_node)
    workflow.add_node("reader", reader_node)
    workflow.add_node("writer", writer_node)
    
    # Set entry point
    workflow.set_entry_point("coordinator")
    
    # Add edges
    workflow.add_edge("coordinator", "search")
    workflow.add_edge("search", "reader")
    workflow.add_edge("reader", "writer")
    workflow.add_edge("writer", END)
    
    return workflow.compile()


def coordinator_node(state: ResearchState) -> ResearchState:
    """Coordinator node - validates and prepares the question."""
    question = state["question"]
    
    result = coordinator_agent.run(question)
    
    return {
        **state,
        "clarified_question": result.get("clarified_question", question),
        "progress": 0.1,
        "current_agent": "CoordinatorAgent",
        "status": "coordinator_complete" if result.get("status") == "success" else "error",
        "error": result.get("error")
    }


def search_node(state: ResearchState) -> ResearchState:
    """Search node - searches for relevant information."""
    question = state.get("clarified_question", state["question"])
    
    result = search_agent.run(question)
    
    return {
        **state,
        "search_query": result.get("search_query", ""),
        "search_results": result.get("search_results", []),
        "wikipedia_results": result.get("wikipedia_results", []),
        "progress": 0.4,
        "current_agent": "SearchAgent",
        "status": "search_complete" if result.get("status") == "success" else "error",
        "error": result.get("error")
    }


def reader_node(state: ResearchState) -> ResearchState:
    """Reader node - fetches and summarizes content from URLs."""
    search_results = state.get("search_results", [])
    question = state.get("clarified_question", state["question"])
    
    result = reader_agent.run(search_results, question)
    
    return {
        **state,
        "summaries": result.get("summaries", []),
        "progress": 0.7,
        "current_agent": "ReaderAgent",
        "status": "reader_complete" if result.get("status") == "success" else "error",
        "error": result.get("error")
    }


def writer_node(state: ResearchState) -> ResearchState:
    """Writer node - combines information into a coherent answer."""
    question = state.get("clarified_question", state["question"])
    search_results = state.get("search_results", [])
    summaries = state.get("summaries", [])
    wikipedia_results = state.get("wikipedia_results", [])
    
    result = writer_agent.run(question, search_results, summaries, wikipedia_results)
    
    return {
        **state,
        "final_answer": result.get("final_answer", ""),
        "sources": result.get("sources", []),
        "progress": 1.0,
        "current_agent": "WriterAgent",
        "status": "completed" if result.get("status") == "success" else "error",
        "error": result.get("error")
    }


def run_research(question: str, progress_callback: Optional[Callable] = None) -> ResearchState:
    """
    Run the research workflow.
    
    Args:
        question: User's research question
        progress_callback: Optional callback for progress updates
        
    Returns:
        Final state with the research results
    """
    # Create initial state
    initial_state: ResearchState = {
        "question": question,
        "clarified_question": "",
        "search_query": "",
        "search_results": [],
        "wikipedia_results": [],
        "summaries": [],
        "final_answer": "",
        "sources": [],
        "progress": 0.0,
        "current_agent": "",
        "status": "started",
        "error": None,
        "messages": []
    }
    
    # Create and run the graph
    graph = create_research_graph()
    
    # Run with progress tracking
    final_state = None
    for state in graph.stream(initial_state):
        final_state = state
        
        # Call progress callback if provided
        if progress_callback:
            for node_name, node_state in state.items():
                if isinstance(node_state, dict):
                    progress_callback({
                        "agent": node_state.get("current_agent", node_name),
                        "status": node_state.get("status", ""),
                        "progress": node_state.get("progress", 0),
                        "message": f"Completed {node_state.get('current_agent', node_name)} step"
                    })
    
    # Get the final state from the last node
    if final_state:
        # Get the last node's state
        last_node_state = list(final_state.values())[0] if final_state else {}
        return last_node_state if isinstance(last_node_state, dict) else initial_state
    return initial_state


# Create a singleton instance
research_graph = create_research_graph()
