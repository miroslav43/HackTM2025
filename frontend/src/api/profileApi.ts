import { apiClient } from './client';

/**
 * API functions for user profile management
 * Handles profile updates, personal information, and activity
 */

export interface ProfileData {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  address?: string;
  cnp?: string;
  avatar?: string;
  role: string;
  created_at: string;
  updated_at: string;
}

export interface ProfileUpdateData {
  first_name?: string;
  last_name?: string;
  phone?: string;
  address?: string;
  cnp?: string;
}

export interface ActivityItem {
  id: string;
  action: string;
  timestamp: string;
  details?: string;
}

export interface PasswordChangeData {
  current_password: string;
  new_password: string;
}

/**
 * Get current user profile
 */
export const getProfile = async (): Promise<ProfileData> => {
  try {
    const response = await apiClient.get('/users/profile');
    return response.data;
  } catch (error) {
    console.error('Error getting profile:', error);
    throw error;
  }
};

/**
 * Update user profile information
 */
export const updateProfile = async (profileData: ProfileUpdateData): Promise<ProfileData> => {
  try {
    const response = await apiClient.put('/users/profile', profileData);
    return response.data;
  } catch (error) {
    console.error('Error updating profile:', error);
    throw error;
  }
};

/**
 * Upload user avatar
 */
export const uploadAvatar = async (file: File): Promise<ProfileData> => {
  try {
    const formData = new FormData();
    formData.append('avatar', file);

    const token = localStorage.getItem('authToken');
    const response = await fetch('/api/users/profile/avatar', {
      method: 'POST',
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      body: formData,
    });

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

    return await response.json();
  } catch (error) {
    console.error('Error uploading avatar:', error);
    throw error;
  }
};

/**
 * Change user password
 */
export const changePassword = async (passwordData: PasswordChangeData): Promise<{ message: string }> => {
  try {
    const response = await apiClient.put('/users/profile/password', passwordData);
    return response.data;
  } catch (error) {
    console.error('Error changing password:', error);
    throw error;
  }
};

/**
 * Get user activity history
 */
export const getUserActivity = async (): Promise<ActivityItem[]> => {
  try {
    // This would be implemented when activity tracking is added to backend
    // For now, return mock data
    return [
      {
        id: '1',
        action: 'Profil actualizat',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        details: 'Informații de contact actualizate'
      },
      {
        id: '2',
        action: 'Document încărcat: Carte identitate',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '3',
        action: 'Cerere procesată: Certificat urbanism',
        timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '4',
        action: 'Cont creat',
        timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      }
    ];
  } catch (error) {
    console.error('Error getting activity:', error);
    throw error;
  }
};

/**
 * Deactivate user account
 */
export const deactivateAccount = async (): Promise<{ message: string }> => {
  try {
    const response = await apiClient.delete('/users/profile');
    return response.data;
  } catch (error) {
    console.error('Error deactivating account:', error);
    throw error;
  }
};

/**
 * Get user sessions
 */
export const getUserSessions = async (): Promise<any[]> => {
  try {
    const response = await apiClient.get('/users/sessions');
    return response.data;
  } catch (error) {
    console.error('Error getting sessions:', error);
    throw error;
  }
};

/**
 * Revoke a specific session
 */
export const revokeSession = async (sessionId: string): Promise<{ message: string }> => {
  try {
    const response = await apiClient.delete(`/users/sessions/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error('Error revoking session:', error);
    throw error;
  }
};

/**
 * Revoke all sessions
 */
export const revokeAllSessions = async (): Promise<{ message: string }> => {
  try {
    const response = await apiClient.delete('/users/sessions');
    return response.data;
  } catch (error) {
    console.error('Error revoking all sessions:', error);
    throw error;
  }
};
