import { useState, useEffect } from 'react';
import {
  getCurrentLocation,
  findNearbyParkingZones,
  getUserVehicles,
  startParkingSession,
  getActiveParkingSessions,
  stopParkingSession,
  ParkingZone,
  UserVehicle,
  ParkingSession,
  UserLocation
} from '@/api/parkingApi';

export const useParking = () => {
  const [location, setLocation] = useState<UserLocation | null>(null);
  const [parkingZones, setParkingZones] = useState<ParkingZone[]>([]);
  const [vehicles, setVehicles] = useState<UserVehicle[]>([]);
  const [activeSessions, setActiveSessions] = useState<ParkingSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Get current location and find nearby parking zones
   */
  const findParking = async (): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      console.log('Getting current location...');
      const userLocation = await getCurrentLocation();
      setLocation(userLocation);

      console.log('Finding nearby parking zones...');
      const zones = await findNearbyParkingZones(userLocation);
      setParkingZones(zones);

      console.log('Getting user vehicles...');
      const userVehicles = await getUserVehicles();
      setVehicles(userVehicles);

      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Eroare necunoscută';
      setError(errorMessage);
      console.error('Error in findParking:', errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Start a new parking session
   */
  const payParking = async (zoneId: string, duration: number): Promise<boolean> => {
    if (!vehicles.length) {
      setError('Nu aveți vehicule înregistrate');
      return false;
    }

    const defaultVehicle = vehicles.find(v => v.isDefault) || vehicles[0];
    setLoading(true);
    setError(null);

    try {
      console.log('Starting parking session...');
      await startParkingSession(zoneId, defaultVehicle.licensePlate, duration);
      
      // Refresh active sessions
      await loadActiveSessions();
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Eroare la plata parcării';
      setError(errorMessage);
      console.error('Error paying parking:', errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Load active parking sessions
   */
  const loadActiveSessions = async () => {
    try {
      const sessions = await getActiveParkingSessions();
      setActiveSessions(sessions);
    } catch (err) {
      console.error('Error loading active sessions:', err);
    }
  };

  /**
   * Stop an active parking session
   */
  const stopParking = async (sessionId: string): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      await stopParkingSession(sessionId);
      await loadActiveSessions();
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Eroare la oprirea parcării';
      setError(errorMessage);
      console.error('Error stopping parking:', errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Load active sessions on component mount
  useEffect(() => {
    loadActiveSessions();
  }, []);

  return {
    location,
    parkingZones,
    vehicles,
    activeSessions,
    loading,
    error,
    findParking,
    payParking,
    stopParking,
    refreshSessions: loadActiveSessions
  };
};
