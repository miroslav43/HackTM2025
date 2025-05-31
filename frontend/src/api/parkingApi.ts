import { apiClient } from './client';

/**
 * API functions for parking management
 * Handles location detection, parking zones, and automatic payments
 */

export interface ParkingZone {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  pricePerHour: number;
  maxDuration: number; // în ore
  available: boolean;
}

export interface UserVehicle {
  id: string;
  licensePlate: string;
  brand: string;
  model: string;
  isDefault: boolean;
}

export interface ParkingSession {
  id: string;
  zoneId: string;
  zoneName: string;
  licensePlate: string;
  startTime: string;
  endTime?: string;
  duration: number; // în minute
  totalCost: number;
  status: 'active' | 'completed' | 'expired';
}

export interface UserLocation {
  latitude: number;
  longitude: number;
  accuracy: number;
}

/**
 * Get user's current location
 */
export const getCurrentLocation = (): Promise<UserLocation> => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation nu este suportată de acest browser'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        });
      },
      (error) => {
        reject(new Error(`Eroare la obținerea locației: ${error.message}`));
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5 minute
      }
    );
  });
};

/**
 * Find parking zones near user location
 */
export const findNearbyParkingZones = async (location: UserLocation): Promise<ParkingZone[]> => {
  try {
    const response = await apiClient.post('/parking/nearby', {
      latitude: location.latitude,
      longitude: location.longitude,
      radius: 500 // 500 metri
    });

    return response.data;
  } catch (error) {
    console.error('Error finding parking zones:', error);
    // Return mock data for development
    return [
      {
        id: '1',
        name: 'Parcarea Centrul Vechi',
        latitude: location.latitude + 0.001,
        longitude: location.longitude + 0.001,
        pricePerHour: 5,
        maxDuration: 4,
        available: true
      },
      {
        id: '2',
        name: 'Parcarea Piața Victoriei',
        latitude: location.latitude - 0.001,
        longitude: location.longitude - 0.001,
        pricePerHour: 7,
        maxDuration: 2,
        available: true
      }
    ];
  }
};

/**
 * Get user vehicles
 */
export const getUserVehicles = async (): Promise<UserVehicle[]> => {
  try {
    const response = await apiClient.get('/parking/vehicles');
    return response.data;
  } catch (error) {
    console.error('Error getting vehicles:', error);
    // Return mock data for development
    return [
      {
        id: '1',
        licensePlate: 'B123ABC',
        brand: 'Dacia',
        model: 'Logan',
        isDefault: true
      }
    ];
  }
};

/**
 * Start parking session
 */
export const startParkingSession = async (
  zoneId: string,
  licensePlate: string,
  duration: number
): Promise<ParkingSession> => {
  try {
    const response = await apiClient.post('/parking/start', {
      zoneId,
      licensePlate,
      duration
    });

    return response.data;
  } catch (error) {
    console.error('Error starting parking session:', error);
    throw error;
  }
};

/**
 * Get active parking sessions
 */
export const getActiveParkingSessions = async (): Promise<ParkingSession[]> => {
  try {
    const response = await apiClient.get('/parking/active');
    return response.data;
  } catch (error) {
    console.error('Error getting active sessions:', error);
    return [];
  }
};

/**
 * Stop parking session
 */
export const stopParkingSession = async (sessionId: string): Promise<void> => {
  try {
    await apiClient.post(`/parking/stop/${sessionId}`);
  } catch (error) {
    console.error('Error stopping parking session:', error);
    throw error;
  }
};
