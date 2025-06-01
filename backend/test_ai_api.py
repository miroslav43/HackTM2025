#!/usr/bin/env python3
"""
Test script for AI Agent API integration
Verifies that the AI agent endpoints work correctly
"""

import asyncio
import requests
import json
import time
from typing import Dict, Any

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

def test_agent_health():
    """Test the health endpoint"""
    print("🔍 Testing AI Agent Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/ai/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check Passed!")
            print(f"   Agent Status: {data.get('status')}")
            print(f"   Agent Initialized: {data.get('agent_initialized')}")
            print(f"   Tools Available: {data.get('tools_available')}")
            print(f"   Environment Configured: {data.get('environment', {}).get('fully_configured')}")
            
            if data.get('warnings'):
                print("⚠️  Warnings:", data.get('warnings'))
                
            return True
        else:
            print(f"❌ Health Check Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False

def test_agent_config():
    """Test the configuration endpoint"""
    print("\n🔍 Testing AI Agent Configuration...")
    
    try:
        response = requests.get(f"{BASE_URL}/ai/agent/config")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Config Retrieved!")
            print(f"   Description: {data.get('description')}")
            print(f"   Tools Count: {len(data.get('tools', []))}")
            
            tools = data.get('tools', [])
            print("   Available Tools:")
            for tool in tools:
                print(f"     - {tool.get('name')}: {tool.get('description')}")
                
            return True
        else:
            print(f"❌ Config Test Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Config Test Error: {e}")
        return False

def test_agent_query(query: str):
    """Test the direct agent query endpoint"""
    print(f"\n🔍 Testing AI Agent Query: '{query}'...")
    
    try:
        payload = {
            "query": query,
            "config": {
                "web_search": {
                    "city_hint": "timisoara",
                    "search_context_size": "high"
                },
                "timpark_payment": {
                    "use_timpark_payment": True
                }
            }
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/ai/agent/query", json=payload)
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {end_time - start_time:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ Agent Query Successful!")
                print(f"   Query: {data.get('query')}")
                print(f"   Response Length: {len(data.get('response', ''))}")
                print(f"   Tools Used: {', '.join(data.get('tools_used', []))}")
                print(f"   TimPark Executed: {data.get('timpark_executed')}")
                print(f"   Processing Time: {data.get('processing_time', 0):.2f}s")
                
                # Show first 300 chars of clean response
                response_text = data.get('response', '')
                preview = response_text[:300] + "..." if len(response_text) > 300 else response_text
                print(f"   Clean Response Preview:")
                print(f"   {preview}")
                
                # Show if this looks like a proper user-friendly response
                if "final_synthesized_response" not in response_text and len(response_text) > 100:
                    print("   ✅ Response appears to be clean and user-friendly")
                else:
                    print("   ⚠️  Response might still contain technical data")
                
                return True
            else:
                print(f"❌ Agent Query Failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Query Test Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query Test Error: {e}")
        return False

def test_agent_tools():
    """Test the tools endpoint"""
    print("\n🔍 Testing AI Agent Tools...")
    
    try:
        response = requests.get(f"{BASE_URL}/ai/agent/tools")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Tools Retrieved!")
            print(f"   Total Tools: {data.get('total_tools')}")
            print(f"   Description: {data.get('description')}")
            
            return True
        else:
            print(f"❌ Tools Test Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Tools Test Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Agent API Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_agent_health),
        ("Configuration", test_agent_config),
        ("Tools List", test_agent_tools),
        ("Simple Query", lambda: test_agent_query("Salut, cum ești?")),
        ("Tax Query", lambda: test_agent_query("taxe locuinta Timisoara")),
        ("Parking Query", lambda: test_agent_query("platesc parcarea 2 ore")),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {name} Test Exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI Agent integration is working correctly.")
    elif passed > 0:
        print("⚠️  Some tests passed. Check the failures above.")
    else:
        print("💥 All tests failed. Check your configuration and API keys.")
    
    print("\n📋 Setup Checklist:")
    print("   □ Set GEMINI_KEY in environment variables")
    print("   □ Set PERPLEXITY_API_KEY in environment variables")
    print("   □ Start FastAPI server: uvicorn main:app --reload")
    print("   □ Ensure all dependencies are installed")

if __name__ == "__main__":
    main() 