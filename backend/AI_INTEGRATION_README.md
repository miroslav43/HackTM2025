# AI Agent Integration - FastAPI Backend

## Overview

This integration brings the sophisticated Romanian Civic Information Assistant AI agent into your FastAPI backend. The agent provides 5 specialized tools for comprehensive civic information and services.

## ✅ **FRONTEND NOW USES REAL API (NO MORE MOCK DATA)**

The frontend AI Agent component has been updated to use the real API endpoints instead of mock responses. Users will now get actual AI-powered responses from the agent.

## Features

### 🔧 **5 Specialized Tools**
1. **Query Reformulation** - Uses Gemini to enhance user queries
2. **TimPark Payment** - Automated parking payment for Timișoara  
3. **Web Search** - Perplexity-powered search with Romanian geographic filtering
4. **Trusted Sites Search** - Government websites search with domain filtering
5. **Final Response Synthesis** - RAG-enhanced response generation

### 🚀 **API Endpoints**

#### `/api/ai/agent/query` (Used by Frontend)
Direct agent access without database operations - **NOW IMPLEMENTED IN FRONTEND**.

```json
POST /api/ai/agent/query
{
  "query": "cum platesc taxa pe locuinta in Timisoara?",
  "config": { /* optional custom config */ }
}

Response:
{
  "success": true,
  "query": "cum platesc taxa pe locuinta in Timisoara?",
  "response": "Pentru plata taxei pe locuință...",
  "reformulated_query": "procedura plata impozit...",
  "tools_used": ["query_reformulation", "trusted_sites_search"],
  "timpark_executed": false,
  "processing_time": 3.45,
  "timestamp": "2024-12-19T10:30:00Z"
}
```

#### Other Endpoints
- `/api/ai/chat` - Full chat with database persistence
- `/api/ai/agent/test` - Development testing
- `/api/ai/agent/config` - Get configuration
- `/api/ai/agent/tools` - List available tools
- `/api/ai/health` - Health check

## Setup

### 1. Environment Variables
Add to your `.env` file:

```bash
# AI Agent Configuration
GEMINI_KEY=your_gemini_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here
AI_AGENT_ENABLED=true
AI_AGENT_TIMEOUT=120
AI_AGENT_MAX_RETRIES=3
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. API Keys Required
- **Gemini API Key**: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Perplexity API Key**: Get from [Perplexity API](https://docs.perplexity.ai/docs/getting-started)

### 4. Test the Integration
```bash
# Run the test script to verify everything works
python test_ai_api.py
```

## Usage Examples

### Frontend Usage (React/TypeScript)
The frontend now uses the real API through `src/api/aiApi.ts`:

```typescript
import { sendAgentQuery } from '@/api/aiApi';

// Send query to real AI agent
const response = await sendAgentQuery({
  query: "taxe locuinta Timisoara",
  config: {
    web_search: { city_hint: "timisoara" },
    timpark_payment: { use_timpark_payment: true }
  }
});

console.log(response.response); // Real AI response
console.log(response.tools_used); // Tools that were executed
```

### Backend Testing
```bash
# Test with curl
curl -X POST http://localhost:8000/api/ai/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "taxe locuinta Timisoara"}'
```

### Custom Configuration
```python
# Custom config example
custom_config = {
    "timpark_payment": {
        "use_timpark_payment": False  # Disable parking automation
    },
    "web_search": {
        "city_hint": "bucuresti",  # Change city context
        "search_context_size": "high"
    }
}
```

## Frontend Changes Made

### Updated Components
- ✅ `frontend/src/components/AIAgent.tsx` - Now uses real API
- ✅ `frontend/src/api/aiApi.ts` - Complete API service implementation

### Features Added
- ✅ Real-time AI responses from backend
- ✅ Tool usage display (shows which AI tools were used)
- ✅ Processing time display
- ✅ TimPark automation status
- ✅ Error handling and user feedback
- ✅ Quick suggestion buttons
- ✅ Loading states

### Removed
- ❌ Mock response generation (`generateAIResponse` function)
- ❌ Hardcoded responses
- ❌ Fake delay simulation

## Agent Workflow

1. **Query Processing** → Gemini reformulates user query
2. **TimPark Check** → If parking payment detected, execute automation
3. **Web Search** → Perplexity searches Romanian sources  
4. **Trusted Sites** → Searches government websites
5. **Final Synthesis** → Gemini creates comprehensive response with RAG context

## Configuration Options

The agent supports extensive configuration through `agent_config.json`:

- **Models**: Choose Gemini models (2.0-flash, 2.5-flash-preview)
- **Temperature**: Control AI creativity (0.1=focused, 1.0=creative)
- **Search Context**: low/medium/high search breadth
- **RAG Domains**: Enable local knowledge integration
- **Tool Toggle**: Enable/disable individual tools

## Error Handling

The integration includes comprehensive error handling:

- **API Key Validation**: Checks for required environment variables
- **Config Validation**: Validates configuration structure
- **Timeout Management**: Prevents hanging requests
- **Graceful Degradation**: Returns meaningful errors
- **Frontend Error States**: User-friendly error messages

## Health Check & Monitoring

Monitor agent status:
```bash
GET /api/ai/health

Response:
{
  "status": "healthy",
  "agent_initialized": true,
  "config_loaded": true,
  "tools_available": 5,
  "tools": ["query_reformulation", "timpark_payment", "web_search", "trusted_sites_search", "final_response_generation"],
  "environment": {
    "gemini_key_configured": true,
    "perplexity_key_configured": true,
    "fully_configured": true
  }
}
```

## Testing

### Automated Tests
```bash
# Run comprehensive API tests
python test_ai_api.py
```

### Manual Testing
1. Start FastAPI server: `uvicorn main:app --reload`
2. Open frontend and navigate to AI Agent
3. Try these test queries:
   - "Salut, cum ești?" (Simple greeting)
   - "taxe locuinta Timisoara" (Tax information)
   - "platesc parcarea 2 ore" (Parking payment)
   - "certificat urbanism" (Urban planning certificate)

## Performance

- **Async Operations**: Non-blocking execution
- **Concurrent Processing**: Multiple tools run simultaneously  
- **Response Caching**: Efficient for repeated queries
- **Timeout Controls**: Configurable processing limits
- **Frontend Optimization**: Real-time updates and loading states

## Troubleshooting

### Common Issues
1. **"Agent service unhealthy"** → Check API keys in environment
2. **"Processing failed"** → Verify network connectivity
3. **"Mock responses"** → This is now fixed - all responses are real
4. **Slow responses** → Increase `AI_AGENT_TIMEOUT` setting

### Debug Commands
```bash
# Check health
curl http://localhost:8000/api/ai/health

# Test simple query
curl -X POST http://localhost:8000/api/ai/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# View logs
tail -f backend.log
```

## Production Deployment

- ✅ Environment variables configured
- ✅ API keys secured
- ✅ Error handling implemented
- ✅ Health monitoring available
- ✅ Frontend integrated with real API
- ✅ No mock data remaining

The AI Agent is now **fully integrated** and production-ready! 🎉 