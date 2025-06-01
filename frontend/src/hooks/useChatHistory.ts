import {
    createChatSession,
    deleteChatSession,
    getChatSession,
    getChatSessions,
    updateChatSession,
    type ChatSessionListItem,
    type ChatSessionWithMessages
} from '@/api/aiApi';
import { useCallback, useEffect, useState } from 'react';

export interface UseChatHistoryReturn {
  sessions: ChatSessionListItem[];
  currentSession: ChatSessionWithMessages | null;
  loading: boolean;
  error: string;
  loadSessions: () => Promise<void>;
  selectSession: (sessionId: number) => Promise<void>;
  createNewSession: (title?: string) => Promise<number>;
  deleteSession: (sessionId: number) => Promise<void>;
  updateSessionTitle: (sessionId: number, title: string) => Promise<void>;
  clearCurrentSession: () => void;
}

export const useChatHistory = (): UseChatHistoryReturn => {
  const [sessions, setSessions] = useState<ChatSessionListItem[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSessionWithMessages | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadSessions = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const sessionsData = await getChatSessions(false, 50);
      setSessions(sessionsData || []);
    } catch (err: any) {
      console.error('Error loading sessions:', err);
      setError(err.message || 'Nu am putut încărca conversațiile');
    } finally {
      setLoading(false);
    }
  }, []);

  const selectSession = useCallback(async (sessionId: number) => {
    try {
      setLoading(true);
      setError('');
      const sessionData = await getChatSession(sessionId);
      setCurrentSession(sessionData);
    } catch (err: any) {
      console.error('Error loading session:', err);
      setError(err.message || 'Nu am putut încărca conversația');
    } finally {
      setLoading(false);
    }
  }, []);

  const createNewSession = useCallback(async (title?: string): Promise<number> => {
    try {
      setError('');
      const newSession = await createChatSession(title);
      await loadSessions(); // Refresh sessions list
      return newSession.id;
    } catch (err: any) {
      console.error('Error creating session:', err);
      setError(err.message || 'Nu am putut crea conversația');
      throw err;
    }
  }, [loadSessions]);

  const deleteSession = useCallback(async (sessionId: number) => {
    try {
      setError('');
      await deleteChatSession(sessionId);
      await loadSessions(); // Refresh sessions list
      
      // Clear current session if it was deleted
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
      }
    } catch (err: any) {
      console.error('Error deleting session:', err);
      setError(err.message || 'Nu am putut șterge conversația');
      throw err;
    }
  }, [loadSessions, currentSession?.id]);

  const updateSessionTitle = useCallback(async (sessionId: number, title: string) => {
    try {
      setError('');
      await updateChatSession(sessionId, { title });
      await loadSessions(); // Refresh sessions list
      
      // Update current session if it matches
      if (currentSession?.id === sessionId) {
        setCurrentSession(prev => prev ? { ...prev, title } : null);
      }
    } catch (err: any) {
      console.error('Error updating session:', err);
      setError(err.message || 'Nu am putut actualiza titlul conversației');
      throw err;
    }
  }, [loadSessions, currentSession?.id]);

  const clearCurrentSession = useCallback(() => {
    setCurrentSession(null);
  }, []);

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  return {
    sessions,
    currentSession,
    loading,
    error,
    loadSessions,
    selectSession,
    createNewSession,
    deleteSession,
    updateSessionTitle,
    clearCurrentSession,
  };
}; 