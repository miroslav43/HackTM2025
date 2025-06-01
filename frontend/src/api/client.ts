// API Configuration
const API_BASE_URL = '/api';

/**
 * Get auth token from localStorage
 */
const getAuthToken = (): string | null => {
  return localStorage.getItem('authToken');
};

/**
 * Refresh authentication token
 */
const refreshAuthToken = async (): Promise<string | null> => {
  try {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
      return null;
    }

    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      // Clear tokens if refresh failed
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
      return null;
    }

    const data = await response.json();
    localStorage.setItem('authToken', data.access_token);
    return data.access_token;
  } catch (error) {
    console.error('Error refreshing token:', error);
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    return null;
  }
};

/**
 * Create headers with authentication
 */
const createHeaders = (additionalHeaders: Record<string, string> = {}): Record<string, string> => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...additionalHeaders,
  };
};

/**
 * Handle fetch response with automatic token refresh
 */
const handleResponse = async (response: Response, originalRequest: () => Promise<Response>): Promise<Response> => {
  if (response.status === 401) {
    // Try to refresh token
    const newToken = await refreshAuthToken();
    
    if (newToken) {
      // Retry the original request with new token
      return await originalRequest();
    } else {
      // Refresh failed, emit logout event
      window.dispatchEvent(new CustomEvent('auth:logout'));
      throw new Error('Authentication failed');
    }
  }
  
  if (!response.ok) {
    let errorMessage = `HTTP error! status: ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // If can't parse JSON, use default message
    }
    throw new Error(errorMessage);
  }
  
  return response;
};

/**
 * API Client with automatic authentication and error handling
 */
export const apiClient = {
  async get(endpoint: string, options: { responseType?: 'blob' } & RequestInit = {}) {
    const makeRequest = () => fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: createHeaders(options.headers as Record<string, string>),
      ...options,
    });

    const response = await makeRequest();
    const handledResponse = await handleResponse(response, makeRequest);
    
    // Handle blob responses (like file downloads)
    if (options.responseType === 'blob') {
      return {
        data: await handledResponse.blob(),
        status: handledResponse.status,
        statusText: handledResponse.statusText,
      };
    }
    
    return {
      data: await handledResponse.json(),
      status: handledResponse.status,
      statusText: handledResponse.statusText,
    };
  },

  async post(endpoint: string, data?: any, options: RequestInit = {}) {
    const makeRequest = () => fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: createHeaders(options.headers as Record<string, string>),
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });

    const response = await makeRequest();
    const handledResponse = await handleResponse(response, makeRequest);
    
    return {
      data: await handledResponse.json(),
      status: handledResponse.status,
      statusText: handledResponse.statusText,
    };
  },

  async put(endpoint: string, data?: any, options: RequestInit = {}) {
    const makeRequest = () => fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: createHeaders(options.headers as Record<string, string>),
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });

    const response = await makeRequest();
    const handledResponse = await handleResponse(response, makeRequest);
    
    return {
      data: await handledResponse.json(),
      status: handledResponse.status,
      statusText: handledResponse.statusText,
    };
  },

  async delete(endpoint: string, options: RequestInit = {}) {
    const makeRequest = () => fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: createHeaders(options.headers as Record<string, string>),
      ...options,
    });

    const response = await makeRequest();
    const handledResponse = await handleResponse(response, makeRequest);
    
    return {
      data: await handledResponse.json(),
      status: handledResponse.status,
      statusText: handledResponse.statusText,
    };
  },
};
