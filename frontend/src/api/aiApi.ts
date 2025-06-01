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
    [key: string]: unknown;
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
  [key: string]: unknown;
}

export interface ToolConfigSchema {
  display_name: string;
  description: string;
  model_type: 'gemini' | 'perplexity' | 'mixed';
  available_models?: string[];
  default_model?: string;
  temperature_range?: [number, number];
  default_temperature?: number;
  max_tokens_range?: [number, number];
  default_max_tokens?: number;
  gemini_config?: {
    available_models: string[];
    default_model: string;
    temperature_range: [number, number];
    default_temperature: number;
    max_tokens_range: [number, number];
    default_max_tokens: number;
  };
  perplexity_config?: {
    available_models: string[];
    default_model: string;
    temperature_range: [number, number];
    default_temperature: number;
    max_tokens_range: [number, number];
    default_max_tokens: number;
  };
}

export interface ToolConfig {
  model: string;
  temperature: number;
  max_tokens: number;
}

export interface TrustedSitesToolConfig {
  gemini: ToolConfig;
  perplexity: ToolConfig;
}

export interface CurrentToolConfigs {
  query_reformulation: ToolConfig;
  timpark_payment: ToolConfig;
  web_search: ToolConfig;
  trusted_sites_search: TrustedSitesToolConfig;
  final_response_generation: ToolConfig;
}

export interface ToolConfigUpdateRequest {
  tool_configs: {
    [toolName: string]: ToolConfig | { gemini?: ToolConfig; perplexity?: ToolConfig };
  };
}

export interface ToolConfigUpdateResponse {
  success: boolean;
  updated_tools?: string[];
  message: string;
  error?: string;
}

export interface AvailableModels {
  gemini_models: string[];
  perplexity_models: string[];
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
  } catch (error: unknown) {
    console.error('Error sending agent query:', error);
    
    // Handle different error types
    const apiError = error as { response?: { data?: { detail?: string } }; message?: string };
    
    // Return a structured error response
    return {
      success: false,
      query: request.query,
      response: 'Ne pare rău, a apărut o eroare în procesarea întrebării. Vă rugăm să încercați din nou.',
      tools_used: [],
      timpark_executed: false,
      processing_time: 0,
      timestamp: new Date().toISOString(),
      error: apiError.response?.data?.detail || apiError.message || 'Unknown error'
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
): Promise<unknown> => {
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
 * Get all chat sessions for the current user
 */
export const getChatSessions = async (includeArchived: boolean = false, limit: number = 50) => {
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
 * Get a specific chat session with messages
 */
export const getChatSession = async (sessionId: number, limit: number = 100) => {
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
 * Create a new chat session
 */
export const createChatSession = async (title?: string) => {
  try {
    const response = await apiClient.post('/ai/chat/sessions', {
      title: title || null
    });
    return response.data;
  } catch (error) {
    console.error('Error creating chat session:', error);
    throw error;
  }
};

/**
 * Update chat session (e.g., change title)
 */
export const updateChatSession = async (sessionId: number, updates: { title?: string }) => {
  try {
    const response = await apiClient.put(`/ai/chat/sessions/${sessionId}`, updates);
    return response.data;
  } catch (error) {
    console.error('Error updating chat session:', error);
    throw error;
  }
};

/**
 * Delete (archive) a chat session
 */
export const deleteChatSession = async (sessionId: number) => {
  try {
    const response = await apiClient.delete(`/ai/chat/sessions/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting chat session:', error);
    throw error;
  }
};

/**
 * Get chat statistics
 */
export const getChatStats = async () => {
  try {
    const response = await apiClient.get('/ai/chat/stats');
    return response.data;
  } catch (error) {
    console.error('Error getting chat stats:', error);
    throw error;
  }
};

/**
 * Get agent configuration
 */
export const getAgentConfig = async (): Promise<{ config: AgentConfig; tools: unknown[]; description: string }> => {
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
export const getAgentTools = async (): Promise<{ tools: unknown[]; total_tools: number; description: string }> => {
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
export const testAgent = async (query: string, config?: unknown): Promise<unknown> => {
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
 * Get configuration schema for all tools
 */
export const getAgentConfigSchema = async (): Promise<{
  success: boolean;
  schema: Record<string, ToolConfigSchema>;
  description: string;
}> => {
  try {
    const response = await apiClient.get('/ai/agent/config/schema');
    return response.data;
  } catch (error) {
    console.error('Error getting agent config schema:', error);
    throw error;
  }
};

/**
 * Get current configuration for all tools
 */
export const getCurrentAgentConfig = async (): Promise<{
  success: boolean;
  current_configs: CurrentToolConfigs;
  available_models: AvailableModels;
  description: string;
}> => {
  try {
    const response = await apiClient.get('/ai/agent/config/current');
    return response.data;
  } catch (error) {
    console.error('Error getting current agent config:', error);
    throw error;
  }
};

/**
 * Update tool configurations
 */
export const updateAgentConfig = async (
  toolConfigs: ToolConfigUpdateRequest['tool_configs']
): Promise<ToolConfigUpdateResponse> => {
  try {
    const response = await apiClient.post('/ai/agent/config/update', {
      tool_configs: toolConfigs
    });
    return response.data;
  } catch (error) {
    console.error('Error updating agent config:', error);
    throw error;
  }
};

/**
 * Get available models for each tool type
 */
export const getAvailableAgentModels = async (): Promise<{
  success: boolean;
  models: AvailableModels;
  description: string;
}> => {
  try {
    const response = await apiClient.get('/ai/agent/models');
    return response.data;
  } catch (error) {
    console.error('Error getting available models:', error);
    throw error;
  }
};

// Add interfaces for conversation history
export interface ChatSessionListItem {
  id: number;
  title?: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_at?: string;
}

export interface ChatSessionWithMessages {
  id: number;
  title?: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_at?: string;
  messages: ChatMessage[];
}

export interface ChatStats {
  total_sessions: number;
  total_messages: number;
  total_agent_executions: number;
  most_used_tools: string[];
}
