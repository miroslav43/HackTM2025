import React, { useState } from 'react';
import { 
  MessageSquare, 
  Archive, 
  FileText, 
  User, 
  TrendingUp, 
  Clock, 
  CheckCircle,
  AlertTriangle,
  BarChart3,
  Users,
  Calendar,
  Car
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useNavigate } from 'react-router-dom';
import ParkingPayment from './ParkingPayment';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [showParkingPayment, setShowParkingPayment] = useState(false);

  const quickActions = [
    {
      icon: MessageSquare,
      title: 'AI Agent',
      description: 'Obține răspunsuri rapide',
      path: '/ai-agent',
      color: 'bg-blue-500'
    },
    {
      icon: Archive,
      title: 'Arhiva Documente',
      description: 'Caută în baza de date',
      path: '/db-archive',
      color: 'bg-green-500'
    },
    {
      icon: FileText,
      title: 'Documente Auto',
      description: 'Completează automat',
      path: '/auto-documents',
      color: 'bg-purple-500'
    },
    {
      icon: Car,
      title: 'Plată Parcare',
      description: 'Plătește automat parcarea',
      action: () => setShowParkingPayment(true),
      color: 'bg-red-500'
    },
    {
      icon: User,
      title: 'Profil',
      description: 'Gestionează contul',
      path: '/profile',
      color: 'bg-orange-500'
    }
  ];

  const citizenStats = [
    { label: 'Cereri în proces', value: '3', icon: Clock, color: 'text-yellow-600' },
    { label: 'Documente verificate', value: '12', icon: CheckCircle, color: 'text-green-600' },
    { label: 'Notificări noi', value: '2', icon: AlertTriangle, color: 'text-red-600' },
  ];

  const officialStats = [
    { label: 'Cereri de procesat', value: '28', icon: Clock, color: 'text-yellow-600' },
    { label: 'Procesate azi', value: '15', icon: CheckCircle, color: 'text-green-600' },
    { label: 'Utilizatori activi', value: '1,245', icon: Users, color: 'text-blue-600' },
    { label: 'Performanță', value: '94%', icon: TrendingUp, color: 'text-green-600' },
  ];

  const recentActivity = [
    { action: 'Cerere certificat urbanism', status: 'approved', time: '2 ore în urmă' },
    { action: 'Document identitate verificat', status: 'completed', time: '1 zi în urmă' },
    { action: 'Formular taxe locale', status: 'pending', time: '2 zile în urmă' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'text-green-600 bg-green-100';
      case 'completed': return 'text-blue-600 bg-blue-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'approved': return 'Aprobat';
      case 'completed': return 'Finalizat';
      case 'pending': return 'În așteptare';
      default: return 'Necunoscut';
    }
  };

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const handleActionClick = (action: any) => {
    if (action.action) {
      action.action();
    } else if (action.path) {
      handleNavigation(action.path);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">
          Bun venit, {user?.name}!
        </h1>
        <p className="opacity-90">
          {user?.role === 'citizen' 
            ? 'Gestionează documentele și cererile tale cu ușurință' 
            : 'Monitorizează și procesează cererile cetățenilor'
          }
        </p>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Acțiuni rapide</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {quickActions.map((action, index) => (
            <Card 
              key={action.title} 
              className="hover-lift cursor-pointer animate-scale-in"
              style={{ animationDelay: `${index * 0.1}s` }}
              onClick={() => handleActionClick(action)}
            >
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className={`p-3 rounded-lg ${action.color} text-white`}>
                    <action.icon className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{action.title}</h3>
                    <p className="text-sm text-gray-600">{action.description}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Statistics */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Statistici</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {(user?.role === 'citizen' ? citizenStats : officialStats).map((stat, index) => (
            <Card key={stat.label} className="animate-scale-in" style={{ animationDelay: `${index * 0.1}s` }}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">{stat.label}</p>
                    <p className="text-2xl font-bold">{stat.value}</p>
                  </div>
                  <stat.icon className={`h-8 w-8 ${stat.color}`} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5" />
              <span>Activitate recentă</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">{activity.action}</p>
                    <p className="text-sm text-gray-600">{activity.time}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(activity.status)}`}>
                    {getStatusText(activity.status)}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Profile Completion */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <User className="h-5 w-5" />
              <span>Progres profil</span>
            </CardTitle>
            <CardDescription>
              Completează-ți profilul pentru o experiență optimă
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Completare profil</span>
                  <span>75%</span>
                </div>
                <Progress value={75} className="h-2" />
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Informații de bază</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Email verificat</span>
                </div>
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  <span>Documente de identitate</span>
                </div>
              </div>
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => navigate('/profile')}
              >
                Completează profilul
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Parking Payment Modal */}
      <ParkingPayment 
        isOpen={showParkingPayment}
        onClose={() => setShowParkingPayment(false)}
      />
    </div>
  );
};

export default Dashboard;
