
/**
 * API functions for AI agent interactions
 * Handles chat, document analysis, and AI-powered features
 */

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface DocumentAnalysis {
  documentId: string;
  accuracy: number;
  extractedData: Record<string, any>;
  suggestions: string[];
  errors: string[];
}

/**
 * Send message to AI agent
 */
export const sendChatMessage = async (message: string): Promise<ChatMessage> => {
  try {
    const response = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) throw new Error('Failed to send chat message');
    return await response.json();
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

/**
 * Get chat history
 */
export const getChatHistory = async (): Promise<ChatMessage[]> => {
  try {
    const response = await fetch('/api/ai/chat/history', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
    });

    if (!response.ok) throw new Error('Failed to get chat history');
    return await response.json();
  } catch (error) {
    console.error('Error getting chat history:', error);
    throw error;
  }
};

/**
 * Analyze document with AI
 */
export const analyzeDocument = async (documentId: string): Promise<DocumentAnalysis> => {
  try {
    const response = await fetch(`/api/ai/analyze/${documentId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
    });

    if (!response.ok) throw new Error('Failed to analyze document');
    return await response.json();
  } catch (error) {
    console.error('Error analyzing document:', error);
    throw error;
  }
};

/**
 * Generate document automatically
 */
export const generateDocument = async (type: string, data: Record<string, any>): Promise<{ documentUrl: string }> => {
  try {
    const response = await fetch('/api/ai/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
      body: JSON.stringify({ type, data }),
    });

    if (!response.ok) throw new Error('Failed to generate document');
    return await response.json();
  } catch (error) {
    console.error('Error generating document:', error);
    throw error;
  }
};
