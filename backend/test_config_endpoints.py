#!/usr/bin/env python3
"""
Test script for AI Agent Configuration endpoints
Tests the new configuration management functionality
"""

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

def test_config_schema():
    """Test getting the configuration schema"""
    print("🔍 Testing Configuration Schema...")
    
    try:
        response = requests.get(f"{BASE_URL}/ai/agent/config/schema")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Schema Retrieved!")
            print(f"   Tools Available: {len(data.get('schema', {}))}")
            
            for tool_name, tool_schema in data.get('schema', {}).items():
                print(f"   - {tool_name}: {tool_schema.get('display_name')}")
                if 'available_models' in tool_schema:
                    print(f"     Models: {tool_schema['available_models'][:2]}...")
                elif 'gemini_config' in tool_schema:
                    print(f"     Gemini Models: {tool_schema['gemini_config']['available_models'][:2]}...")
                    print(f"     Perplexity Models: {tool_schema['perplexity_config']['available_models'][:2]}...")
            
            return True, data
        else:
            print(f"❌ Schema Test Failed: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Schema Test Error: {e}")
        return False, None

def test_current_config():
    """Test getting current configuration"""
    print("\n🔍 Testing Current Configuration...")
    
    try:
        response = requests.get(f"{BASE_URL}/ai/agent/config/current")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Current Config Retrieved!")
            
            configs = data.get('current_configs', {})
            for tool_name, tool_config in configs.items():
                if tool_name == 'trusted_sites_search':
                    print(f"   {tool_name}:")
                    print(f"     Gemini: {tool_config['gemini']['model']} (temp: {tool_config['gemini']['temperature']})")
                    print(f"     Perplexity: {tool_config['perplexity']['model']} (temp: {tool_config['perplexity']['temperature']})")
                else:
                    print(f"   {tool_name}: {tool_config['model']} (temp: {tool_config['temperature']}, tokens: {tool_config['max_tokens']})")
            
            return True, data
        else:
            print(f"❌ Current Config Test Failed: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Current Config Test Error: {e}")
        return False, None

def test_update_config():
    """Test updating configuration"""
    print("\n🔍 Testing Configuration Update...")
    
    try:
        # Test updating query reformulation
        update_payload = {
            "tool_configs": {
                "query_reformulation": {
                    "model": "gemini-2.5-pro-exp",
                    "temperature": 0.2,
                    "max_tokens": 600
                }
            }
        }
        
        print(f"Sending update payload: {json.dumps(update_payload, indent=2)}")
        
        response = requests.post(f"{BASE_URL}/ai/agent/config/update", json=update_payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Config Update Successful!")
            print(f"   Success: {data.get('success')}")
            print(f"   Updated Tools: {data.get('updated_tools')}")
            print(f"   Message: {data.get('message')}")
            
            return True, data
        else:
            print(f"❌ Update Test Failed: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Update Test Error: {e}")
        return False, None

def test_available_models():
    """Test getting available models"""
    print("\n🔍 Testing Available Models...")
    
    try:
        response = requests.get(f"{BASE_URL}/ai/agent/models")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Models Retrieved!")
            
            models = data.get('models', {})
            print(f"   Gemini Models ({len(models.get('gemini_models', []))}): {models.get('gemini_models', [])[:3]}...")
            print(f"   Perplexity Models ({len(models.get('perplexity_models', []))}): {models.get('perplexity_models', [])[:3]}...")
            
            return True, data
        else:
            print(f"❌ Models Test Failed: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Models Test Error: {e}")
        return False, None

def verify_config_persistence():
    """Verify that config changes persist"""
    print("\n🔍 Testing Configuration Persistence...")
    
    try:
        # Get current config
        response = requests.get(f"{BASE_URL}/ai/agent/config/current")
        if response.status_code != 200:
            print("❌ Could not get current config for persistence test")
            return False
            
        current_config = response.json().get('current_configs', {})
        query_reform_config = current_config.get('query_reformulation', {})
        
        print(f"Current query_reformulation config: {query_reform_config}")
        
        # Check if our previous update persisted
        if (query_reform_config.get('model') == 'gemini-2.5-pro-exp' and 
            query_reform_config.get('temperature') == 0.2 and 
            query_reform_config.get('max_tokens') == 600):
            print("✅ Configuration changes persisted correctly!")
            return True
        else:
            print("❌ Configuration changes did not persist")
            return False
            
    except Exception as e:
        print(f"❌ Persistence Test Error: {e}")
        return False

def main():
    """Run all configuration tests"""
    print("🚀 AI Agent Configuration Tests")
    print("=" * 50)
    
    tests = [
        ("Schema Retrieval", test_config_schema),
        ("Current Config", test_current_config),
        ("Available Models", test_available_models),
        ("Config Update", test_update_config),
        ("Config Persistence", verify_config_persistence),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            result = test_func()
            if isinstance(result, tuple):
                success, _ = result
            else:
                success = result
                
            if success:
                passed += 1
        except Exception as e:
            print(f"❌ {name} Test Exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 Configuration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All configuration tests passed! Settings should work correctly.")
    elif passed > 0:
        print("⚠️  Some tests passed. Check the failures above.")
    else:
        print("💥 All tests failed. Configuration endpoints are not working.")
    
    print("\n📋 Setup Checklist:")
    print("   □ Start FastAPI server: uvicorn main:app --reload")
    print("   □ Check logs for any configuration errors")
    print("   □ Verify agent_config.json file exists and is writable")

if __name__ == "__main__":
    main() 