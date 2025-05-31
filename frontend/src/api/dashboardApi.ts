
/**
 * API functions for dashboard data and statistics
 * Handles metrics, recent activity, and system status
 */

export interface DashboardStats {
  totalDocuments: number;
  pendingVerifications: number;
  completedRequests: number;
  systemStatus: 'online' | 'maintenance' | 'offline';
}

export interface RecentActivity {
  id: string;
  type: 'document_upload' | 'verification_complete' | 'request_submitted';
  title: string;
  timestamp: string;
  status: 'success' | 'pending' | 'error';
}

export interface SystemNotification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

/**
 * Get dashboard statistics
 */
export const getDashboardStats = async (): Promise<DashboardStats> => {
  try {
    const response = await fetch('/api/dashboard/stats', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
    });

    if (!response.ok) throw new Error('Failed to get dashboard stats');
    return await response.json();
  } catch (error) {
    console.error('Error getting dashboard stats:', error);
    // Return mock data for development
    return {
      totalDocuments: 156,
      pendingVerifications: 23,
      completedRequests: 89,
      systemStatus: 'online'
    };
  }
};

/**
 * Get recent activity
 */
export const getRecentActivity = async (limit: number = 10): Promise<RecentActivity[]> => {
  try {
    const response = await fetch(`/api/dashboard/activity?limit=${limit}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
    });

    if (!response.ok) throw new Error('Failed to get recent activity');
    return await response.json();
  } catch (error) {
    console.error('Error getting recent activity:', error);
    // Return mock data for development
    return [
      {
        id: '1',
        type: 'document_upload',
        title: 'Document încărcat: Carte identitate',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        status: 'success'
      },
      {
        id: '2',
        type: 'verification_complete',
        title: 'Verificare completă: Extras carte funciară',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        status: 'success'
      },
      {
        id: '3',
        type: 'request_submitted',
        title: 'Cerere trimisă: Certificat urbanism',
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        status: 'pending'
      }
    ];
  }
};

/**
 * Get system notifications
 */
export const getNotifications = async (): Promise<SystemNotification[]> => {
  try {
    const response = await fetch('/api/dashboard/notifications', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
    });

    if (!response.ok) throw new Error('Failed to get notifications');
    return await response.json();
  } catch (error) {
    console.error('Error getting notifications:', error);
    throw error;
  }
};

/**
 * Mark notification as read
 */
export const markNotificationAsRead = async (notificationId: string): Promise<void> => {
  try {
    const response = await fetch(`/api/dashboard/notifications/${notificationId}/read`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
    });

    if (!response.ok) throw new Error('Failed to mark notification as read');
  } catch (error) {
    console.error('Error marking notification as read:', error);
    throw error;
  }
};
