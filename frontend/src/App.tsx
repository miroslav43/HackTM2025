import AddToArchive from "@/components/AddToArchive";
import AIAgent from "@/components/AIAgent";
import AutoArchiveScan from "@/components/AutoArchiveScan";
import AutoArchiveUpload from "@/components/AutoArchiveUpload";
import AutoDocuments from "@/components/AutoDocuments";
import Dashboard from "@/components/Dashboard";
import DBArchive from "@/components/DBArchive";
import Layout from "@/components/Layout";
import Login from "@/components/Login";
import Profile from "@/components/Profile";
import Register from "@/components/Register";
import Settings from "@/components/Settings";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  return !isAuthenticated ? (
    <>{children}</>
  ) : (
    <Navigate to="/dashboard" replace />
  );
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="ai-agent" element={<AIAgent />} />
        <Route path="db-archive" element={<DBArchive />} />
        <Route path="profile" element={<Profile />} />
        <Route path="auto-documents" element={<AutoDocuments />} />
        <Route path="add-to-archive" element={<AddToArchive />} />
        <Route path="auto-archive/upload" element={<AutoArchiveUpload />} />
        <Route path="auto-archive/scan" element={<AutoArchiveScan />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
