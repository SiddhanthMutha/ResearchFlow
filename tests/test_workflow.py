"""Test scripts to debug the research workflow."""

import asyncio
import sys
sys.path.insert(0, '.')

from src.utils.config import config
from src.memory.storage import storage
from src.tools.wikipedia import wikipedia_tool
from src.tools.web_search import web_search_tool
from src.agents.coordinator import coordinator_agent
from src.agents.search_agent import search_agent
from src.agents.reader_agent import reader_agent
from src.agents.writer_agent import writer_agent
from src.graph.workflow import run_research


def test_config():
    """Test 1: Check if config is loaded correctly."""
    print("\n" + "="*50)
    print("TEST 1: Configuration")
    print("="*50)
    
    print(f"OPENAI_API_KEY: {'Set' if config.OPENAI_API_KEY and not config.OPENAI_API_KEY.startswith('your_') else 'NOT SET or placeholder'}")
    print(f"TAVILY_API_KEY: {'Set' if config.TAVILY_API_KEY and not config.TAVILY_API_KEY.startswith('your_') else 'NOT SET or placeholder'}")
    print(f"OPENAI_MODEL: {config.OPENAI_MODEL}")
    print(f"PORT: {config.PORT}")
    
    return True


async def test_database():
    """Test 2: Check if database is working."""
    print("\n" + "="*50)
    print("TEST 2: Database Connection")
    print("="*50)
    
    try:
        await storage.initialize()
        print("✓ Database initialized successfully")
        
        # Try to save a test record
        test_id = await storage.save_research(
            research_id="test-123",
            query="test question",
            clarified_query="test question",
            final_answer="test answer",
            sources=[],
            cost=0.0,
            duration_seconds=1.0,
            status="test"
        )
        print(f"✓ Save returned ID: {test_id}")
        
        # Try to retrieve it
        result = await storage.get_research("test-123")
        if result:
            print(f"✓ Retrieved: {result['query']}")
        else:
            print("✗ Failed to retrieve saved record")
        
        # Clean up test record
        await storage.delete_research("test-123")
        print("✓ Test record cleaned up")
        
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_wikipedia():
    """Test 3: Check Wikipedia tool."""
    print("\n" + "="*50)
    print("TEST 3: Wikipedia Tool")
    print("="*50)
    
    try:
        result = wikipedia_tool.search("Quantum computing")
        print(f"✓ Wikipedia search returned {len(result) if result else 0} results")
        if result:
            print(f"  First result: {result[0].get('title', 'N/A')}")
        return True
    except Exception as e:
        print(f"✗ Wikipedia error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_web_search():
    """Test 4: Check web search tool."""
    print("\n" + "="*50)
    print("TEST 4: Web Search Tool (Tavily)")
    print("="*50)
    
    try:
        result = web_search_tool.search("quantum computing")
        print(f"✓ Web search returned {len(result) if result else 0} results")
        if result:
            print(f"  First result: {result[0].get('title', 'N/A')}")
        return True
    except Exception as e:
        print(f"✗ Web search error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_coordinator():
    """Test 5: Check coordinator agent."""
    print("\n" + "="*50)
    print("TEST 5: Coordinator Agent")
    print("="*50)
    
    try:
        result = coordinator_agent.run("What is quantum computing?")
        print(f"✓ Coordinator ran successfully")
        print(f"  Status: {result.get('status')}")
        print(f"  Clarified question: {result.get('clarified_question', 'N/A')}")
        return True
    except Exception as e:
        print(f"✗ Coordinator error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_search_agent():
    """Test 6: Check search agent."""
    print("\n" + "="*50)
    print("TEST 6: Search Agent")
    print("="*50)
    
    try:
        result = search_agent.run("What is quantum computing?")
        print(f"✓ Search agent ran successfully")
        print(f"  Status: {result.get('status')}")
        print(f"  Search results: {len(result.get('search_results', []))}")
        print(f"  Wikipedia results: {len(result.get('wikipedia_results', []))}")
        return True
    except Exception as e:
        print(f"✗ Search agent error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_workflow():
    """Test 7: Check full research workflow."""
    print("\n" + "="*50)
    print("TEST 7: Full Research Workflow")
    print("="*50)
    
    try:
        result = run_research("What is quantum computing?")
        print(f"✓ Workflow ran successfully")
        print(f"  Status: {result.get('status')}")
        print(f"  Final answer length: {len(result.get('final_answer', ''))}")
        print(f"  Sources: {len(result.get('sources', []))}")
        
        if result.get('final_answer'):
            print(f"  Answer preview: {result['final_answer'][:200]}...")
        
        return True
    except Exception as e:
        print(f"✗ Workflow error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_storage_with_real_workflow():
    """Test 8: Check if workflow saves to database."""
    print("\n" + "="*50)
    print("TEST 8: Database Storage with Workflow")
    print("="*50)
    
    try:
        # Clear any existing test data
        await storage.delete_research("workflow-test-123")
        
        # This is what the API does
        import time
        start_time = time.time()
        
        result = run_research("What is AI?")
        
        duration = time.time() - start_time
        
        # Save to database (simulating what the API does)
        saved_id = await storage.save_research(
            research_id="workflow-test-123",
            query="What is AI?",
            clarified_query=result.get("clarified_question", "What is AI?"),
            final_answer=result.get("final_answer", ""),
            sources=result.get("sources", []),
            cost=0.0,
            duration_seconds=duration,
            status=result.get("status", "completed")
        )
        
        # Try to retrieve
        saved_result = await storage.get_research("workflow-test-123")
        
        if saved_result:
            print(f"✓ Successfully saved and retrieved from database!")
            print(f"  Query: {saved_result['query']}")
            print(f"  Status: {saved_result['status']}")
            
            # Clean up
            await storage.delete_research("workflow-test-123")
            return True
        else:
            print(f"✗ Failed to retrieve saved workflow result")
            return False
            
    except Exception as e:
        print(f"✗ Storage test error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("="*50)
    print("RESEARCH ASSISTANT DEBUG TESTS")
    print("="*50)
    
    results = {}
    
    # Run tests
    results['config'] = test_config()
    results['database'] = await test_database()
    results['wikipedia'] = await test_wikipedia()
    results['web_search'] = await test_web_search()
    results['coordinator'] = await test_coordinator()
    results['search_agent'] = await test_search_agent()
    results['full_workflow'] = await test_full_workflow()
    results['storage_workflow'] = await test_storage_with_real_workflow()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\nTotal: {passed}/{total} tests passed")


if __name__ == "__main__":
    asyncio.run(main())
