import { Alert, AlertDescription } from "@/components/ui/alert";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth, UserRole } from "@/contexts/AuthContext";
import { AlertCircle, CreditCard, Eye, EyeOff, User } from "lucide-react";
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [loginType, setLoginType] = useState<"classic" | "eid">("classic");
  const [userRole, setUserRole] = useState<UserRole>("citizen");

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (loginType === "classic") {
        if (!email || !password) {
          throw new Error("Te rog completează toate câmpurile");
        }
        await login(email, password, userRole);
      } else {
        // Simulate eID login
        await login("eid@user.ro", "eid-password", userRole);
      }
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Eroare la autentificare");
    } finally {
      setLoading(false);
    }
  };

  const handleEidLogin = () => {
    setLoginType("eid");
    setLoading(true);
    // Simulate eID process
    setTimeout(() => {
      login("eid@user.ro", "eid-password", userRole);
      navigate("/dashboard");
    }, 2000);
  };

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary-700 mb-2">
            e-Guvernare
          </h1>
          <p className="text-gray-600">
            Platformă digitală pentru administrația publică
          </p>
        </div>

        <Card className="glass-effect">
          <CardHeader className="text-center">
            <CardTitle className="text-xl">Autentificare</CardTitle>
            <CardDescription>
              Alege modul de autentificare preferat
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs
              value={loginType}
              onValueChange={(value) =>
                setLoginType(value as "classic" | "eid")
              }
            >
              <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger
                  value="classic"
                  className="flex items-center gap-2"
                >
                  <User className="h-4 w-4" />
                  Cont clasic
                </TabsTrigger>
                <TabsTrigger value="eid" className="flex items-center gap-2">
                  <CreditCard className="h-4 w-4" />
                  eID
                </TabsTrigger>
              </TabsList>

              <TabsContent value="classic">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="role">Tip cont</Label>
                    <select
                      value={userRole}
                      onChange={(e) => setUserRole(e.target.value as UserRole)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="citizen">Cetățean</option>
                      <option value="official">Funcționar Public</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="nume@exemplu.ro"
                      disabled={loading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Parolă</Label>
                    <div className="relative">
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Introdu parola"
                        disabled={loading}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-2 top-1/2 transform -translate-y-1/2"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>

                  {error && (
                    <Alert variant="destructive">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}

                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? "Se autentifică..." : "Autentificare"}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="eid">
                <div className="text-center space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="role-eid">Tip cont</Label>
                    <select
                      value={userRole}
                      onChange={(e) => setUserRole(e.target.value as UserRole)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="citizen">Cetățean</option>
                      <option value="official">Funcționar Public</option>
                    </select>
                  </div>

                  <div className="p-6 border-2 border-dashed border-gray-300 rounded-lg">
                    <CreditCard className="h-12 w-12 mx-auto text-gray-400 mb-3" />
                    <p className="text-sm text-gray-600 mb-4">
                      Inserează cardul eID și urmează instrucțiunile
                    </p>
                    <Button
                      onClick={handleEidLogin}
                      disabled={loading}
                      className="w-full"
                    >
                      {loading ? "Se conectează..." : "Autentificare cu eID"}
                    </Button>
                  </div>
                </div>
              </TabsContent>
            </Tabs>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Nu ai cont?{" "}
                <Link
                  to="/register"
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  Înregistrează-te
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;
