/**
 * API functions for authentication and user management
 * Handles login, logout, registration, and user operations
 */

const API_BASE = '/api';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  role: 'citizen' | 'official';
  phone?: string;
}

export interface User {
  id: string;
  first_name: string;
  last_name: string;
  name: string; // computed field from backend
  email: string;
  role: 'citizen' | 'official';
  phone?: string;
  address?: string;
  cnp?: string;
  avatar?: string;
  created_at: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

/**
 * Get auth token from localStorage
 */
const getAuthToken = (): string | null => {
  return localStorage.getItem('authToken');
};

/**
 * Create headers with auth token
 */
const createAuthHeaders = (): HeadersInit => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

/**
 * Login user with credentials
 */
export const loginUser = async (credentials: LoginRequest): Promise<AuthResponse> => {
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to login');
    }
    
    const data = await response.json();
    
    // Store tokens
    localStorage.setItem('authToken', data.access_token);
    localStorage.setItem('refreshToken', data.refresh_token);
    
    return data;
  } catch (error) {
    console.error('Error logging in:', error);
    throw error;
  }
};

/**
 * Register new user
 */
export const registerUser = async (userData: RegisterRequest): Promise<AuthResponse> => {
  try {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to register');
    }
    
    const data = await response.json();
    
    // Store tokens
    localStorage.setItem('authToken', data.access_token);
    localStorage.setItem('refreshToken', data.refresh_token);
    
    return data;
  } catch (error) {
    console.error('Error registering:', error);
    throw error;
  }
};

/**
 * Logout current user
 */
export const logoutUser = async (): Promise<void> => {
  try {
    const token = getAuthToken();
    if (token) {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: createAuthHeaders(),
      });
    }
  } catch (error) {
    console.error('Error logging out:', error);
  } finally {
    // Always clear tokens
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
  }
};

/**
 * Get current user profile
 */
export const getCurrentUser = async (): Promise<User> => {
  try {
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: createAuthHeaders(),
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Try to refresh token
        const refreshed = await refreshToken();
        if (refreshed) {
          // Retry with new token
          const retryResponse = await fetch(`${API_BASE}/auth/me`, {
            headers: createAuthHeaders(),
          });
          if (retryResponse.ok) {
            return await retryResponse.json();
          }
        }
        // Clear tokens if refresh failed
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        throw new Error('Authentication failed');
      }
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error getting current user:', error);
    throw error;
  }
};

/**
 * Refresh authentication token
 */
export const refreshToken = async (): Promise<{ token: string } | null> => {
  try {
    const refresh_token = localStorage.getItem('refreshToken');
    if (!refresh_token) {
      throw new Error('No refresh token available');
    }

    const response = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token }),
    });

    if (!response.ok) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
      throw new Error('Failed to refresh token');
    }
    
    const data = await response.json();
    localStorage.setItem('authToken', data.access_token);
    
    return { token: data.access_token };
  } catch (error) {
    console.error('Error refreshing token:', error);
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    return null;
  }
};
