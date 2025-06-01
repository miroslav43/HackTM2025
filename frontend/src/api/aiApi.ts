/**
 * AI Agent API - Romanian Civic Information Assistant
 * Handles direct agent queries, chat sessions, and AI-powered features
 */

import { apiClient } from './client';

// Types
export interface AgentQueryRequest {
  query: string;
  config?: {
    web_search?: {
      city_hint?: string;
      search_context_size?: 'low' | 'medium' | 'high';
    };
    timpark_payment?: {
      use_timpark_payment?: boolean;
    };
    [key: string]: any;
  };
}

export interface AgentQueryResponse {
  success: boolean;
  query: string;
  response: string;
  reformulated_query?: string;
  tools_used: string[];
  timpark_executed: boolean;
  processing_time: number;
  timestamp: string;
  error?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatSession {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
  message_count?: number;
  last_message_at?: string;
}

export interface AgentConfig {
  query_processing: {
    use_robust_reformulation: boolean;
    gemini_temperature: number;
    gemini_max_tokens: number;
  };
  timpark_payment: {
    use_timpark_payment: boolean;
  };
  web_search: {
    city_hint: string;
    use_perplexity: boolean;
    search_context_size: 'low' | 'medium' | 'high';
  };
  [key: string]: any;
}

export interface AgentHealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  agent_initialized: boolean;
  config_loaded: boolean;
  tools_available: number;
  tools: string[];
  environment: {
    gemini_key_configured: boolean;
    perplexity_key_configured: boolean;
    agent_enabled: boolean;
    fully_configured: boolean;
  };
  warnings: string[];
  timestamp: string;
}

/**
 * Direct query to AI agent (recommended for quick responses)
 */
export const sendAgentQuery = async (request: AgentQueryRequest): Promise<AgentQueryResponse> => {
  try {
    const response = await apiClient.post('/ai/agent/query', request);
    return response.data;
  } catch (error: any) {
    console.error('Error sending agent query:', error);
    
    // Return a structured error response
    return {
      success: false,
      query: request.query,
      response: 'Ne pare rău, a apărut o eroare în procesarea întrebării. Vă rugăm să încercați din nou.',
      tools_used: [],
      timpark_executed: false,
      processing_time: 0,
      timestamp: new Date().toISOString(),
      error: error.response?.data?.detail || error.message || 'Unknown error'
    };
  }
};

/**
 * Send message to AI chat (with database persistence)
 */
export const sendChatMessage = async (
  message: string,
  sessionId?: number,
  createNewSession: boolean = false,
  agentConfig?: Partial<AgentConfig>
): Promise<any> => {
  try {
    const response = await apiClient.post('/ai/chat', {
      message,
      session_id: sessionId,
      create_new_session: createNewSession,
      agent_config: agentConfig
    });
    return response.data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

/**
 * Get chat sessions
 */
export const getChatSessions = async (includeArchived: boolean = false, limit: number = 50): Promise<ChatSession[]> => {
  try {
    const queryParams = new URLSearchParams({
      include_archived: includeArchived.toString(),
      limit: limit.toString()
    });
    const response = await apiClient.get(`/ai/chat/sessions?${queryParams.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error getting chat sessions:', error);
    throw error;
  }
};

/**
 * Get specific chat session with messages
 */
export const getChatSession = async (sessionId: number, limit: number = 100): Promise<any> => {
  try {
    const queryParams = new URLSearchParams({
      limit: limit.toString()
    });
    const response = await apiClient.get(`/ai/chat/sessions/${sessionId}?${queryParams.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error getting chat session:', error);
    throw error;
  }
};

/**
 * Create new chat session
 */
export const createChatSession = async (title: string): Promise<ChatSession> => {
  try {
    const response = await apiClient.post('/ai/chat/sessions', { title });
    return response.data;
  } catch (error) {
    console.error('Error creating chat session:', error);
    throw error;
  }
};

/**
 * Get agent configuration
 */
export const getAgentConfig = async (): Promise<{ config: AgentConfig; tools: any[]; description: string }> => {
  try {
    const response = await apiClient.get('/ai/agent/config');
    return response.data;
  } catch (error) {
    console.error('Error getting agent config:', error);
    throw error;
  }
};

/**
 * Get available agent tools
 */
export const getAgentTools = async (): Promise<{ tools: any[]; total_tools: number; description: string }> => {
  try {
    const response = await apiClient.get('/ai/agent/tools');
    return response.data;
  } catch (error) {
    console.error('Error getting agent tools:', error);
    throw error;
  }
};

/**
 * Test agent with custom query (development/debugging)
 */
export const testAgent = async (query: string, config?: any): Promise<any> => {
  try {
    const queryParams = new URLSearchParams({
      query,
      ...(config && { config: JSON.stringify(config) })
    });
    const response = await apiClient.post(`/ai/agent/test?${queryParams.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error testing agent:', error);
    throw error;
  }
};

/**
 * Check agent health status
 */
export const getAgentHealth = async (): Promise<AgentHealthStatus> => {
  try {
    const response = await apiClient.get('/ai/health');
    return response.data;
  } catch (error) {
    console.error('Error getting agent health:', error);
    throw error;
  }
};

/**
 * Get chat statistics
 */
export const getChatStats = async (): Promise<any> => {
  try {
    const response = await apiClient.get('/ai/chat/stats');
    return response.data;
  } catch (error) {
    console.error('Error getting chat stats:', error);
    throw error;
  }
};
