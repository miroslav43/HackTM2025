import {
  ActivityItem,
  changePassword,
  getProfile,
  getUserActivity,
  getUserSessions,
  PasswordChangeData,
  ProfileData,
  ProfileUpdateData,
  revokeSession,
  updateProfile,
  uploadAvatar,
} from "@/api/profileApi";
import DocumentUploadSection from "@/components/documents/DocumentUploadSection";
import PersonalInfoSection from "@/components/PersonalInfoSection";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/contexts/AuthContext";
import {
  Activity,
  AlertCircle,
  Check,
  Edit,
  Shield,
  Upload,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { toast } from "sonner";

const Profile = () => {
  const { user: authUser, logout } = useAuth();
  const [user, setUser] = useState<ProfileData | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);
  const [showPasswordChange, setShowPasswordChange] = useState(false);

  const [formData, setFormData] = useState<ProfileUpdateData>({
    first_name: "",
    last_name: "",
    phone: "",
    address: "",
    cnp: "",
  });

  const [passwordData, setPasswordData] = useState<PasswordChangeData>({
    current_password: "",
    new_password: "",
  });

  // Load profile data on component mount
  useEffect(() => {
    loadProfileData();
    loadActivityData();
  }, []);

  const loadProfileData = async () => {
    try {
      setLoading(true);
      const profileData = await getProfile();
      setUser(profileData);
      setFormData({
        first_name: profileData.first_name,
        last_name: profileData.last_name,
        phone: profileData.phone || "",
        address: profileData.address || "",
        cnp: profileData.cnp || "",
      });
    } catch (error) {
      console.error("Error loading profile:", error);
      toast.error("Eroare la încărcarea profilului");
    } finally {
      setLoading(false);
    }
  };

  const loadActivityData = async () => {
    try {
      const [activityData, sessionsData] = await Promise.all([
        getUserActivity(),
        getUserSessions(),
      ]);
      setActivities(activityData);
      setSessions(sessionsData);
    } catch (error) {
      console.error("Error loading activity data:", error);
    }
  };

  const calculateProfileCompletion = () => {
    if (!user) return 0;

    let completed = 0;
    const total = 5;

    if (user.first_name && user.last_name) completed++;
    if (user.email) completed++;
    if (user.phone) completed++;
    if (user.address) completed++;
    if (user.cnp) completed++;

    return Math.round((completed / total) * 100);
  };

  const handleInputChange = (field: keyof ProfileUpdateData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      const updatedUser = await updateProfile(formData);
      setUser(updatedUser);
      setIsEditing(false);
      toast.success("Profil actualizat cu succes!");
    } catch (error) {
      console.error("Error updating profile:", error);
      toast.error("Eroare la actualizarea profilului");
    } finally {
      setSaving(false);
    }
  };

  const handleAvatarUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file
    if (!file.type.startsWith("image/")) {
      toast.error("Vă rugăm să selectați o imagine valida");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      // 5MB
      toast.error("Imaginea este prea mare. Dimensiunea maximă este 5MB");
      return;
    }

    try {
      setUploadingAvatar(true);
      const updatedUser = await uploadAvatar(file);
      setUser(updatedUser);
      toast.success("Avatar actualizat cu succes!");
    } catch (error) {
      console.error("Error uploading avatar:", error);
      toast.error("Eroare la încărcarea avatar-ului");
    } finally {
      setUploadingAvatar(false);
    }
  };

  const handlePasswordChange = async () => {
    if (!passwordData.current_password || !passwordData.new_password) {
      toast.error("Vă rugăm să completați toate câmpurile");
      return;
    }

    if (passwordData.new_password.length < 8) {
      toast.error("Parola nouă trebuie să aibă cel puțin 8 caractere");
      return;
    }

    try {
      await changePassword(passwordData);
      setPasswordData({ current_password: "", new_password: "" });
      setShowPasswordChange(false);
      toast.success("Parola a fost schimbată cu succes!");
    } catch (error) {
      console.error("Error changing password:", error);
      toast.error("Eroare la schimbarea parolei");
    }
  };

  const handleRevokeSession = async (sessionId: string) => {
    try {
      await revokeSession(sessionId);
      await loadActivityData(); // Reload sessions
      toast.success("Sesiune revocată cu succes");
    } catch (error) {
      console.error("Error revoking session:", error);
      toast.error("Eroare la revocarea sesiunii");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Se încarcă profilul...</span>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="h-16 w-16 text-red-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Eroare la încărcarea profilului
        </h3>
        <Button onClick={loadProfileData} variant="outline">
          Încearcă din nou
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header cu progres */}
      <Card className="bg-gradient-to-r from-primary-600 to-primary-700 text-white">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Avatar className="h-16 w-16 border-4 border-white">
                <AvatarImage src={user?.avatar} />
                <AvatarFallback className="bg-white text-primary-700 text-xl font-bold">
                  {user?.first_name
                    ?.split(" ")
                    .map((n) => n[0])
                    .join("")}
                </AvatarFallback>
              </Avatar>
              <div>
                <h1 className="text-2xl font-bold">
                  {user?.first_name} {user?.last_name}
                </h1>
                <p className="opacity-90">
                  {user?.role === "citizen" ? "Cetățean" : "Funcționar Public"}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm opacity-90 mb-2">Completare profil</p>
              <div className="flex items-center space-x-3">
                <Progress
                  value={calculateProfileCompletion()}
                  className="w-32 h-2 bg-white/20"
                />
                <span className="text-xl font-bold">
                  {calculateProfileCompletion()}%
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="personal" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="personal">Informații Personale</TabsTrigger>
          <TabsTrigger value="security">Securitate</TabsTrigger>
          <TabsTrigger value="documents">Documente Personale</TabsTrigger>
          <TabsTrigger value="activity">Activitate</TabsTrigger>
        </TabsList>

        <TabsContent value="personal">
          <div className="space-y-6">
            {/* Avatar Upload Section */}
            <Card>
              <CardHeader>
                <CardTitle>Avatar profil</CardTitle>
                <CardDescription>
                  Încărcă o fotografie pentru profilul tău
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-4">
                  <Avatar className="h-20 w-20">
                    <AvatarImage src={user?.avatar} />
                    <AvatarFallback className="text-2xl">
                      {user?.first_name?.[0]}
                      {user?.last_name?.[0]}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarUpload}
                      className="hidden"
                      id="avatar-upload"
                      disabled={uploadingAvatar}
                    />
                    <label htmlFor="avatar-upload">
                      <Button
                        asChild
                        variant="outline"
                        disabled={uploadingAvatar}
                      >
                        <span>
                          {uploadingAvatar ? (
                            <>Se încarcă...</>
                          ) : (
                            <>
                              <Upload className="h-4 w-4 mr-2" />
                              Schimbă avatar
                            </>
                          )}
                        </span>
                      </Button>
                    </label>
                    <p className="text-sm text-gray-500 mt-2">
                      JPG, PNG sau GIF. Dimensiunea maximă: 5MB
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Personal Information */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Informații personale</CardTitle>
                    <CardDescription>
                      Gestionează datele tale de contact și profil
                    </CardDescription>
                  </div>
                  <Button
                    variant={isEditing ? "default" : "outline"}
                    onClick={() =>
                      isEditing ? handleSaveProfile() : setIsEditing(true)
                    }
                    disabled={saving}
                  >
                    {saving ? (
                      <>Se salvează...</>
                    ) : isEditing ? (
                      <>
                        <Check className="h-4 w-4 mr-2" />
                        Salvează
                      </>
                    ) : (
                      <>
                        <Edit className="h-4 w-4 mr-2" />
                        Editează
                      </>
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="first_name">Prenume</Label>
                    <Input
                      id="first_name"
                      value={formData.first_name}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          first_name: e.target.value,
                        }))
                      }
                      disabled={!isEditing}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="last_name">Nume</Label>
                    <Input
                      id="last_name"
                      value={formData.last_name}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          last_name: e.target.value,
                        }))
                      }
                      disabled={!isEditing}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="phone">Telefon</Label>
                    <Input
                      id="phone"
                      value={formData.phone}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          phone: e.target.value,
                        }))
                      }
                      disabled={!isEditing}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cnp">CNP</Label>
                    <Input
                      id="cnp"
                      value={formData.cnp}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          cnp: e.target.value,
                        }))
                      }
                      disabled={!isEditing}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="address">Adresa</Label>
                  <Input
                    id="address"
                    value={formData.address}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        address: e.target.value,
                      }))
                    }
                    disabled={!isEditing}
                  />
                </div>
              </CardContent>
            </Card>

            {/* AI Extracted Personal Information Section */}
            <PersonalInfoSection />
          </div>
        </TabsContent>

        <TabsContent value="security">
          <div className="space-y-6">
            {/* Password Change */}
            <Card>
              <CardHeader>
                <CardTitle>Schimbă parola</CardTitle>
                <CardDescription>
                  Actualizează parola contului tău
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {!showPasswordChange ? (
                  <Button
                    onClick={() => setShowPasswordChange(true)}
                    variant="outline"
                  >
                    <Shield className="h-4 w-4 mr-2" />
                    Schimbă parola
                  </Button>
                ) : (
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="current_password">Parola curentă</Label>
                      <Input
                        id="current_password"
                        type="password"
                        value={passwordData.current_password}
                        onChange={(e) =>
                          setPasswordData((prev) => ({
                            ...prev,
                            current_password: e.target.value,
                          }))
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="new_password">Parola nouă</Label>
                      <Input
                        id="new_password"
                        type="password"
                        value={passwordData.new_password}
                        onChange={(e) =>
                          setPasswordData((prev) => ({
                            ...prev,
                            new_password: e.target.value,
                          }))
                        }
                      />
                    </div>
                    <div className="flex space-x-2">
                      <Button onClick={handlePasswordChange}>
                        Salvează parola
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => {
                          setShowPasswordChange(false);
                          setPasswordData({
                            current_password: "",
                            new_password: "",
                          });
                        }}
                      >
                        Anulează
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Active Sessions */}
            <Card>
              <CardHeader>
                <CardTitle>Sesiuni active</CardTitle>
                <CardDescription>
                  Gestionează sesiunile active ale contului
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {sessions.length > 0 ? (
                    sessions.map((session, index) => (
                      <div
                        key={session.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div>
                          <p className="font-medium">
                            {session.is_current
                              ? "Sesiunea curentă"
                              : "Sesiune activă"}
                          </p>
                          <p className="text-sm text-gray-600">
                            Creat:{" "}
                            {new Date(session.created_at).toLocaleDateString(
                              "ro-RO"
                            )}
                          </p>
                        </div>
                        {!session.is_current && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleRevokeSession(session.id)}
                          >
                            Revocă
                          </Button>
                        )}
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500">Nu există sesiuni active</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="documents">
          <DocumentUploadSection />
        </TabsContent>

        <TabsContent value="activity">
          <Card>
            <CardHeader>
              <CardTitle>Activitate recentă</CardTitle>
              <CardDescription>
                Istoricul acțiunilor efectuate în cont
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {activities.length > 0 ? (
                  activities.map((activity, index) => (
                    <div
                      key={activity.id}
                      className={`flex items-center space-x-3 p-3 bg-gray-50 rounded-lg animate-scale-in`}
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <Activity className="h-5 w-5 text-gray-500" />
                      <div className="flex-1">
                        <p className="font-medium">{activity.action}</p>
                        <p className="text-sm text-gray-600">
                          {new Date(activity.timestamp).toLocaleDateString(
                            "ro-RO",
                            {
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            }
                          )}
                        </p>
                        {activity.details && (
                          <p className="text-xs text-gray-500 mt-1">
                            {activity.details}
                          </p>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500">Nu există activitate recentă</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Profile;
