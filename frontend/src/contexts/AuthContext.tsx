import React, { createContext, useContext, useEffect, useState } from "react";
import {
  getCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
  type LoginRequest,
  type RegisterRequest,
} from "../api/authApi";

export type UserRole = "citizen" | "official";

export interface User {
  id: string;
  first_name: string;
  last_name: string;
  name: string; // computed field from backend
  email: string;
  role: UserRole;
  phone?: string;
  address?: string;
  cnp?: string;
  avatar?: string;
  documents?: {
    id: boolean;
    landRegistry: boolean;
  };
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string, role: UserRole) => Promise<void>;
  register: (userData: {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    role: UserRole;
    phone?: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (updates: Partial<User>) => void;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

/**
 * Transform backend user to frontend user format
 */
const transformUser = (backendUser: any): User => ({
  id: backendUser.id,
  first_name: backendUser.first_name,
  last_name: backendUser.last_name,
  name:
    backendUser.name ||
    `${backendUser.first_name} ${backendUser.last_name}`.trim(),
  email: backendUser.email,
  role: backendUser.role,
  phone: backendUser.phone,
  address: backendUser.address,
  cnp: backendUser.cnp,
  avatar: backendUser.avatar,
  documents: {
    id: false, // These would need to be determined from actual user documents
    landRegistry: false,
  },
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on app start
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("authToken");

      if (token) {
        try {
          const userData = await getCurrentUser();
          const transformedUser = transformUser(userData);
          setUser(transformedUser);
          localStorage.setItem("user", JSON.stringify(transformedUser));
        } catch (error) {
          console.error("Failed to get current user:", error);
          // Clear stale data if API call fails
          localStorage.removeItem("authToken");
          localStorage.removeItem("refreshToken");
          localStorage.removeItem("user");
          setUser(null);
        }
      }
    } catch (error) {
      console.error("Auth initialization error:", error);
      // Clear stale data
      localStorage.removeItem("authToken");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("user");
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string, role: UserRole) => {
    try {
      setLoading(true);

      const credentials: LoginRequest = { email, password };
      const response = await loginUser(credentials);
      const transformedUser = transformUser(response.user);
      setUser(transformedUser);
      localStorage.setItem("user", JSON.stringify(transformedUser));
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData: {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    role: UserRole;
    phone?: string;
  }) => {
    try {
      setLoading(true);

      const registerData: RegisterRequest = {
        first_name: userData.firstName,
        last_name: userData.lastName,
        email: userData.email,
        password: userData.password,
        role: userData.role,
        phone: userData.phone,
      };
      const response = await registerUser(registerData);
      const transformedUser = transformUser(response.user);
      setUser(transformedUser);
      localStorage.setItem("user", JSON.stringify(transformedUser));
    } catch (error) {
      console.error("Registration error:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await logoutUser();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setUser(null);
      localStorage.removeItem("user");
      localStorage.removeItem("authToken");
      localStorage.removeItem("refreshToken");
    }
  };

  const updateUser = (updates: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...updates };
      setUser(updatedUser);
      localStorage.setItem("user", JSON.stringify(updatedUser));
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        register,
        logout,
        updateUser,
        isAuthenticated: !!user,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
