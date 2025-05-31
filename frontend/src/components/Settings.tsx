
import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/contexts/AuthContext';
import { 
  User, 
  Bell, 
  Shield, 
  Palette, 
  HelpCircle, 
  Mail, 
  Phone, 
  Lock,
  Globe,
  Save,
  Camera
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const Settings = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [settings, setSettings] = useState({
    emailNotifications: true,
    smsNotifications: false,
    documentAlerts: true,
    twoFactorAuth: false,
    darkMode: false,
    language: 'ro',
    autoSave: true
  });

  const handleSettingChange = (key: string, value: boolean) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    toast({
      title: "Setări salvate",
      description: "Preferințele dumneavoastră au fost actualizate cu succes.",
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Setări</h1>
        <p className="text-gray-600">Gestionați preferințele și configurațiile contului dumneavoastră</p>
      </div>

      {/* Profil utilizator */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <User className="h-5 w-5" />
            <span>Informații Profil</span>
          </CardTitle>
          <CardDescription>
            Actualizați informațiile personale și fotografiile de profil
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center space-x-4">
            <Avatar className="h-20 w-20">
              <AvatarImage src={user?.avatar} />
              <AvatarFallback className="text-lg">
                {user?.name?.split(' ').map(n => n[0]).join('')}
              </AvatarFallback>
            </Avatar>
            <div className="space-y-2">
              <Button variant="outline" size="sm">
                <Camera className="h-4 w-4 mr-2" />
                Schimbă fotografia
              </Button>
              <p className="text-sm text-gray-500">
                Imaginea trebuie să fie în format JPG, PNG sau GIF și să nu depășească 5MB
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nume complet</Label>
              <Input id="name" defaultValue={user?.name} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" defaultValue={user?.email} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Telefon</Label>
              <Input id="phone" type="tel" placeholder="+40 XXX XXX XXX" />
            </div>
            <div className="space-y-2">
              <Label>Rol utilizator</Label>
              <Badge variant="secondary" className="w-fit">
                {user?.role === 'citizen' ? 'Cetățean' : 'Funcționar Public'}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notificări */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bell className="h-5 w-5" />
            <span>Notificări</span>
          </CardTitle>
          <CardDescription>
            Configurați modul în care doriți să primiți notificări
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Notificări email</Label>
              <p className="text-sm text-gray-500">
                Primiți actualizări despre documentele dumneavoastră prin email
              </p>
            </div>
            <Switch
              checked={settings.emailNotifications}
              onCheckedChange={(checked) => handleSettingChange('emailNotifications', checked)}
            />
          </div>
          
          <Separator />
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Notificări SMS</Label>
              <p className="text-sm text-gray-500">
                Primiți alerte importante prin mesaje text
              </p>
            </div>
            <Switch
              checked={settings.smsNotifications}
              onCheckedChange={(checked) => handleSettingChange('smsNotifications', checked)}
            />
          </div>
          
          <Separator />
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Alerte documente</Label>
              <p className="text-sm text-gray-500">
                Notificări când documentele sunt procesate sau expiră
              </p>
            </div>
            <Switch
              checked={settings.documentAlerts}
              onCheckedChange={(checked) => handleSettingChange('documentAlerts', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Securitate */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5" />
            <span>Securitate</span>
          </CardTitle>
          <CardDescription>
            Opțiuni pentru a vă proteja contul
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Autentificare cu doi factori</Label>
              <p className="text-sm text-gray-500">
                Adăugați un nivel suplimentar de securitate contului
              </p>
            </div>
            <Switch
              checked={settings.twoFactorAuth}
              onCheckedChange={(checked) => handleSettingChange('twoFactorAuth', checked)}
            />
          </div>
          
          <Separator />
          
          <div className="space-y-3">
            <Label className="text-base">Schimbă parola</Label>
            <div className="grid grid-cols-1 gap-3 max-w-md">
              <Input type="password" placeholder="Parola actuală" />
              <Input type="password" placeholder="Parola nouă" />
              <Input type="password" placeholder="Confirmă parola nouă" />
              <Button variant="outline" size="sm" className="w-fit">
                <Lock className="h-4 w-4 mr-2" />
                Actualizează parola
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Preferințe aplicație */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Palette className="h-5 w-5" />
            <span>Preferințe Aplicație</span>
          </CardTitle>
          <CardDescription>
            Personalizați experiența de utilizare
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Mod întunecat</Label>
              <p className="text-sm text-gray-500">
                Comutați între tema clară și întunecată
              </p>
            </div>
            <Switch
              checked={settings.darkMode}
              onCheckedChange={(checked) => handleSettingChange('darkMode', checked)}
            />
          </div>
          
          <Separator />
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Salvare automată</Label>
              <p className="text-sm text-gray-500">
                Salvează automat modificările făcute în formulare
              </p>
            </div>
            <Switch
              checked={settings.autoSave}
              onCheckedChange={(checked) => handleSettingChange('autoSave', checked)}
            />
          </div>
          
          <Separator />
          
          <div className="space-y-2">
            <Label className="text-base">Limba aplicației</Label>
            <select className="w-full max-w-xs px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option value="ro">Română</option>
              <option value="en">English</option>
              <option value="hu">Magyar</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Suport și ajutor */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <HelpCircle className="h-5 w-5" />
            <span>Suport și Ajutor</span>
          </CardTitle>
          <CardDescription>
            Resurse și informații de contact
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button variant="outline" className="justify-start">
              <Mail className="h-4 w-4 mr-2" />
              Contactează suportul
            </Button>
            <Button variant="outline" className="justify-start">
              <Phone className="h-4 w-4 mr-2" />
              Apel telefonic
            </Button>
            <Button variant="outline" className="justify-start">
              <Globe className="h-4 w-4 mr-2" />
              Ghid utilizare
            </Button>
            <Button variant="outline" className="justify-start">
              <HelpCircle className="h-4 w-4 mr-2" />
              Întrebări frecvente
            </Button>
          </div>
          
          <Separator />
          
          <div className="text-sm text-gray-500">
            <p><strong>Versiunea aplicației:</strong> 1.0.0</p>
            <p><strong>Ultima actualizare:</strong> 31 Mai 2025</p>
          </div>
        </CardContent>
      </Card>

      {/* Buton de salvare */}
      <div className="flex justify-end">
        <Button onClick={handleSave} className="flex items-center space-x-2">
          <Save className="h-4 w-4" />
          <span>Salvează setările</span>
        </Button>
      </div>
    </div>
  );
};

export default Settings;
