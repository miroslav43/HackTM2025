# AI Agent Integration Setup Guide

## Overview

This guide will help you integrate the Romanian Civic Information Assistant AI Agent into your backend and set up chat functionality.

## Environment Variables

Add these environment variables to your `.env` file:

```bash
# AI Agent Configuration
# Get these from Google AI Studio: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your-gemini-api-key-here

# Get this from Perplexity: https://www.perplexity.ai/settings/api
PERPLEXITY_API_KEY=your-perplexity-api-key-here

# TimPark automation configuration (optional)
TIMPARK_EMAIL=your-email@example.com
TIMPARK_PHONE=your-phone-number

# Optional: Chrome WebDriver configuration for TimPark automation
CHROME_DRIVER_PATH=/path/to/chromedriver
HEADLESS_BROWSER=true
```

## Installation Steps

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Database Migration

Run the migration script to add chat tables:

```bash
python add_chat_tables.py
```

### 3. Verify Agent Integration

Test the agent health check:

```bash
curl http://localhost:8000/api/ai/health
```

### 4. API Endpoints

The following endpoints are now available:

#### Chat Endpoints
- `POST /api/ai/chat` - Send message to AI agent
- `GET /api/ai/chat/sessions` - Get user's chat sessions
- `POST /api/ai/chat/sessions` - Create new chat session
- `GET /api/ai/chat/sessions/{id}` - Get specific session with messages
- `PUT /api/ai/chat/sessions/{id}` - Update session
- `DELETE /api/ai/chat/sessions/{id}` - Archive session
- `GET /api/ai/chat/stats` - Get chat statistics

#### Agent Configuration
- `GET /api/ai/agent/config` - Get agent configuration
- `GET /api/ai/agent/tools` - Get available tools info
- `POST /api/ai/agent/test` - Test agent with query
- `GET /api/ai/agent/execution/{id}` - Get execution details
- `GET /api/ai/health` - Agent health check

## Agent Features

### 5 Integrated Tools:

1. **Query Reformulation** - Uses Gemini to enhance user queries
2. **TimPark Payment Tool** - Automates parking payments for Timișoara
3. **Web Search** - Uses Perplexity for Romanian sources
4. **Trusted Sites Search** - Searches only government websites
5. **Final Response Generation** - Synthesizes all results with RAG context

### Conditional Workflow:
- If TimPark payment is executed, steps 3-5 are skipped for efficiency
- Full workflow continues for information queries

## API Usage Examples

### Send a Chat Message

```bash
curl -X POST "http://localhost:8000/api/ai/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Cum îmi reinnoiesc buletinul în Timișoara?",
    "create_new_session": true
  }'
```

### Get Chat Sessions

```bash
curl -X GET "http://localhost:8000/api/ai/chat/sessions" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Agent (Development)

```bash
curl -X POST "http://localhost:8000/api/ai/agent/test?query=taxe%20locuinta%20Timisoara" \
  -H "Content-Type: application/json"
```

## Configuration Options

You can customize agent behavior by passing configuration in the chat request:

```json
{
  "message": "Your question here",
  "agent_config": {
    "query_processing": {
      "use_robust_reformulation": true,
      "gemini_temperature": 0.1
    },
    "timpark_payment": {
      "use_timpark_payment": true
    },
    "web_search": {
      "use_perplexity": true,
      "city_hint": "timisoara"
    },
    "trusted_sites_search": {
      "use_trusted_sites_search": true
    },
    "final_response_generation": {
      "use_final_response_generation": true,
      "rag_context": {
        "use_rag_context": true,
        "rag_domains": ["dfmt.ro", "timpark.ro"]
      }
    }
  }
}
```

## Database Schema

### New Tables Added:

1. **chat_sessions** - Manages chat conversations
   - id, user_id, title, created_at, updated_at, is_archived

2. **chat_messages** - Stores individual messages
   - id, session_id, role, content, timestamp, processing_time, tools_used, agent_metadata

3. **agent_executions** - Tracks AI agent processing details
   - id, message_id, original_question, reformulated_query, config_used, execution_time, tools_executed, workflow_stopped_early, tool results

## Troubleshooting

### Common Issues:

1. **Agent import errors**: Ensure the `AI/src` directory is accessible
2. **Missing API keys**: Check environment variables are set
3. **ChromeDriver issues**: Install ChromeDriver for TimPark automation
4. **Database connection**: Run the migration script

### Logs:
Check application logs for detailed error information:
```bash
tail -f backend_logs.log
```

## Frontend Integration

Use these API endpoints to build a chat interface in your frontend:

1. Create a chat session
2. Send messages via POST /api/ai/chat
3. Display responses and track conversation history
4. Show agent execution details (tools used, processing time)

## Security Considerations

- All endpoints require authentication
- Chat sessions are user-isolated
- Sensitive agent configurations are server-side only
- API keys are never exposed to frontend

## Performance Notes

- Average agent processing time: 5-15 seconds
- TimPark automation: 10-30 seconds
- Database queries are optimized with indexes
- Consider implementing rate limiting for production

## Support

For issues or questions about the AI agent integration, check:
1. Agent health endpoint: `/api/ai/health`
2. Available tools: `/api/ai/agent/tools`
3. Application logs for detailed error information 