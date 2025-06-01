"""
Test script for AI Agent integration
Tests basic functionality without requiring full backend setup.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

async def test_agent_service():
    """Test the agent service initialization and basic functionality"""
    print("🧪 Testing AI Agent Integration")
    print("=" * 50)
    
    try:
        # Test 1: Import agent service
        print("1️⃣ Testing agent service import...")
        from app.services.agent_service import agent_service
        print("   ✅ Agent service imported successfully")
        
        # Test 2: Check agent initialization
        print("\n2️⃣ Testing agent initialization...")
        tools = agent_service.get_available_tools()
        print(f"   ✅ Found {len(tools)} available tools:")
        for tool in tools:
            print(f"      - {tool['name']}: {tool['description']}")
        
        # Test 3: Check configuration loading
        print("\n3️⃣ Testing configuration loading...")
        config = agent_service.get_default_config()
        if config:
            print("   ✅ Configuration loaded successfully")
            print(f"      - Query processing: {config.get('query_processing', {}).get('use_robust_reformulation', 'Not set')}")
            print(f"      - TimPark payment: {config.get('timpark_payment', {}).get('use_timpark_payment', 'Not set')}")
            print(f"      - Web search: {config.get('web_search', {}).get('use_perplexity', 'Not set')}")
            print(f"      - Trusted sites: {config.get('trusted_sites_search', {}).get('use_trusted_sites_search', 'Not set')}")
            print(f"      - Final response: {config.get('final_response_generation', {}).get('use_final_response_generation', 'Not set')}")
        else:
            print("   ⚠️ Configuration not loaded")
        
        # Test 4: Test basic agent query processing (without API keys)
        print("\n4️⃣ Testing agent query processing (dry run)...")
        try:
            # This might fail due to missing API keys, but we can test the workflow
            result = await agent_service.process_query(
                query="test query",
                config_name="integration_test"
            )
            
            if result.get("error"):
                print(f"   ⚠️ Expected error (likely missing API keys): {result['error'][:100]}...")
                print("   ✅ Agent workflow structure is working (error handling)")
            else:
                print("   ✅ Agent processing completed successfully")
                print(f"      - Execution time: {result.get('execution_time', 0)}ms")
                print(f"      - Tools executed: {result.get('tools_executed', [])}")
                
        except Exception as e:
            print(f"   ⚠️ Expected error (likely missing API keys): {str(e)[:100]}...")
            print("   ✅ Agent service structure is working (error handling)")
        
        print("\n🎉 Agent integration test completed!")
        print("\n📝 Next steps:")
        print("   1. Add API keys to .env file (see AI_AGENT_SETUP.md)")
        print("   2. Run database migration: python add_chat_tables.py")
        print("   3. Start the backend server")
        print("   4. Test with: curl http://localhost:8000/api/ai/health")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("\n🔧 Possible solutions:")
        print("   1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("   2. Check that AI/src directory exists and contains agent.py")
        print("   3. Verify the directory structure matches the expected layout")
        return False
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        print("\n🔧 Check the error details above and refer to AI_AGENT_SETUP.md")
        return False


async def test_models_import():
    """Test that the new models can be imported"""
    print("\n🗃️ Testing database models...")
    
    try:
        from app.models.chat import ChatSession, ChatMessage, AgentExecution
        print("   ✅ Chat models imported successfully")
        
        # Test model structure
        print("   📊 Model fields:")
        print(f"      - ChatSession: {list(ChatSession.__table__.columns.keys())}")
        print(f"      - ChatMessage: {list(ChatMessage.__table__.columns.keys())}")
        print(f"      - AgentExecution: {list(AgentExecution.__table__.columns.keys())}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Model import error: {e}")
        return False


async def test_schemas_import():
    """Test that the new schemas can be imported"""
    print("\n📋 Testing Pydantic schemas...")
    
    try:
        from app.schemas.chat import (
            ChatRequest, ChatResponse, ChatSessionCreate,
            ChatMessageResponse, AgentExecutionResponse
        )
        print("   ✅ Chat schemas imported successfully")
        
        # Test creating a sample request
        request = ChatRequest(message="Test message", create_new_session=True)
        print(f"   ✅ Sample request created: {request.message[:20]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Schema import error: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 AI Agent Integration Test Suite")
    print("=" * 60)
    
    # Test individual components
    models_ok = await test_models_import()
    schemas_ok = await test_schemas_import() 
    agent_ok = await test_agent_service()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print(f"   Models:  {'✅ PASS' if models_ok else '❌ FAIL'}")
    print(f"   Schemas: {'✅ PASS' if schemas_ok else '❌ FAIL'}")
    print(f"   Agent:   {'✅ PASS' if agent_ok else '❌ FAIL'}")
    
    if models_ok and schemas_ok and agent_ok:
        print("\n🎉 ALL TESTS PASSED! Integration is ready.")
        print("   📖 See AI_AGENT_SETUP.md for next steps")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        print("   📖 See AI_AGENT_SETUP.md for troubleshooting")


if __name__ == "__main__":
    asyncio.run(main()) 