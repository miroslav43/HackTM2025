
/**
 * API functions for application settings
 * Handles user preferences, system configuration, and security settings
 */

export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  language: 'ro' | 'en';
  notifications: {
    email: boolean;
    push: boolean;
    documentUpdates: boolean;
    systemAlerts: boolean;
  };
  privacy: {
    profileVisibility: 'public' | 'private';
    shareActivityData: boolean;
  };
}

export interface SecuritySettings {
  twoFactorEnabled: boolean;
  lastPasswordChange: string;
  activeSessions: {
    id: string;
    device: string;
    location: string;
    lastActive: string;
    current: boolean;
  }[];
}

/**
 * Get user settings
 */
export const getUserSettings = async (): Promise<UserSettings> => {
  try {
    const response = await fetch('/api/settings/user', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
    });

    if (!response.ok) throw new Error('Failed to get user settings');
    return await response.json();
  } catch (error) {
    console.error('Error getting user settings:', error);
    // Return default settings for development
    return {
      theme: 'system',
      language: 'ro',
      notifications: {
        email: true,
        push: true,
        documentUpdates: true,
        systemAlerts: false,
      },
      privacy: {
        profileVisibility: 'private',
        shareActivityData: false,
      }
    };
  }
};

/**
 * Update user settings
 */
export const updateUserSettings = async (settings: UserSettings): Promise<UserSettings> => {
  try {
    const response = await fetch('/api/settings/user', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
      body: JSON.stringify(settings),
    });

    if (!response.ok) throw new Error('Failed to update user settings');
    return await response.json();
  } catch (error) {
    console.error('Error updating user settings:', error);
    throw error;
  }
};

/**
 * Get security settings
 */
export const getSecuritySettings = async (): Promise<SecuritySettings> => {
  try {
    const response = await fetch('/api/settings/security', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
    });

    if (!response.ok) throw new Error('Failed to get security settings');
    return await response.json();
  } catch (error) {
    console.error('Error getting security settings:', error);
    throw error;
  }
};

/**
 * Change password
 */
export const changePassword = async (data: {
  currentPassword: string;
  newPassword: string;
}): Promise<void> => {
  try {
    const response = await fetch('/api/settings/password', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) throw new Error('Failed to change password');
  } catch (error) {
    console.error('Error changing password:', error);
    throw error;
  }
};

/**
 * Enable/disable two-factor authentication
 */
export const toggleTwoFactor = async (enable: boolean): Promise<{ qrCode?: string; backupCodes?: string[] }> => {
  try {
    const response = await fetch('/api/settings/two-factor', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
      body: JSON.stringify({ enabled: enable }),
    });

    if (!response.ok) throw new Error('Failed to toggle two-factor authentication');
    return await response.json();
  } catch (error) {
    console.error('Error toggling two-factor authentication:', error);
    throw error;
  }
};

/**
 * Revoke session
 */
export const revokeSession = async (sessionId: string): Promise<void> => {
  try {
    const response = await fetch(`/api/settings/sessions/${sessionId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
    });

    if (!response.ok) throw new Error('Failed to revoke session');
  } catch (error) {
    console.error('Error revoking session:', error);
    throw error;
  }
};
