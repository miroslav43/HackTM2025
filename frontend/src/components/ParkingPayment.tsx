
import React, { useState } from 'react';
import { MapPin, Car, Clock, CreditCard, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useParking } from '@/hooks/useParking';
import { toast } from 'sonner';

interface ParkingPaymentProps {
  isOpen: boolean;
  onClose: () => void;
}

const ParkingPayment: React.FC<ParkingPaymentProps> = ({ isOpen, onClose }) => {
  const {
    location,
    parkingZones,
    vehicles,
    activeSessions,
    loading,
    error,
    findParking,
    payParking,
    stopParking
  } = useParking();

  const [selectedZone, setSelectedZone] = useState<string>('');
  const [duration, setDuration] = useState<string>('60');
  const [step, setStep] = useState<'location' | 'zones' | 'payment'>('location');

  const handleFindParking = async () => {
    const success = await findParking();
    if (success) {
      setStep('zones');
    }
  };

  const handlePayParking = async () => {
    if (!selectedZone || !duration) {
      toast.error('Selectați zona și durata');
      return;
    }

    const success = await payParking(selectedZone, parseInt(duration));
    if (success) {
      toast.success('Parcarea a fost plătită cu succes!');
      onClose();
    }
  };

  const handleStopParking = async (sessionId: string) => {
    const success = await stopParking(sessionId);
    if (success) {
      toast.success('Sesiunea de parcare a fost oprită');
    }
  };

  const selectedZoneData = parkingZones.find(zone => zone.id === selectedZone);
  const calculateCost = () => {
    if (!selectedZoneData || !duration) return 0;
    return (selectedZoneData.pricePerHour * parseInt(duration)) / 60;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Car className="h-5 w-5" />
              <span>Plată Parcare</span>
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          <CardDescription>
            Plătiți parcarea automat cu locația dvs. curentă
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Active Sessions */}
          {activeSessions.length > 0 && (
            <div>
              <h3 className="font-medium mb-3">Sesiuni Active</h3>
              <div className="space-y-2">
                {activeSessions.map((session) => (
                  <div key={session.id} className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-md">
                    <div>
                      <p className="font-medium">{session.zoneName}</p>
                      <p className="text-sm text-gray-600">{session.licensePlate}</p>
                      <p className="text-sm text-green-600">
                        {session.duration} min - {session.totalCost} RON
                      </p>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleStopParking(session.id)}
                      disabled={loading}
                    >
                      Oprește
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {step === 'location' && (
            <div className="text-center space-y-4">
              <MapPin className="h-12 w-12 mx-auto text-blue-500" />
              <div>
                <h3 className="font-medium">Detectare Locație</h3>
                <p className="text-sm text-gray-600">
                  Găsim parcările disponibile în zona dvs.
                </p>
              </div>
              <Button 
                onClick={handleFindParking} 
                disabled={loading}
                className="w-full"
              >
                {loading ? 'Se caută...' : 'Găsește Parcări'}
              </Button>
            </div>
          )}

          {step === 'zones' && (
            <div className="space-y-4">
              <div>
                <h3 className="font-medium mb-3">Parcări Disponibile</h3>
                <Select value={selectedZone} onValueChange={setSelectedZone}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selectați zona de parcare" />
                  </SelectTrigger>
                  <SelectContent>
                    {parkingZones.map((zone) => (
                      <SelectItem key={zone.id} value={zone.id}>
                        <div className="flex justify-between w-full">
                          <span>{zone.name}</span>
                          <span className="text-green-600">{zone.pricePerHour} RON/oră</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <h4 className="font-medium mb-2">Durată Parcare</h4>
                <Select value={duration} onValueChange={setDuration}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="30">30 minute</SelectItem>
                    <SelectItem value="60">1 oră</SelectItem>
                    <SelectItem value="120">2 ore</SelectItem>
                    <SelectItem value="180">3 ore</SelectItem>
                    <SelectItem value="240">4 ore</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {vehicles.length > 0 && (
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                  <p className="text-sm font-medium">Vehicul:</p>
                  <p className="text-sm text-blue-600">
                    {vehicles.find(v => v.isDefault)?.licensePlate || vehicles[0]?.licensePlate}
                  </p>
                </div>
              )}

              {selectedZoneData && (
                <div className="p-3 bg-gray-50 border rounded-md">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Cost Total:</span>
                    <span className="text-lg font-bold text-green-600">
                      {calculateCost().toFixed(2)} RON
                    </span>
                  </div>
                </div>
              )}

              <div className="flex space-x-2">
                <Button variant="outline" onClick={() => setStep('location')} className="flex-1">
                  Înapoi
                </Button>
                <Button 
                  onClick={handlePayParking} 
                  disabled={!selectedZone || loading}
                  className="flex-1"
                >
                  <CreditCard className="h-4 w-4 mr-2" />
                  {loading ? 'Se procesează...' : 'Plătește'}
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ParkingPayment;
