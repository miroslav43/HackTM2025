import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import {
  Archive,
  ChevronDown,
  FileText,
  Home,
  LogOut,
  Menu,
  MessageSquare,
  Plus,
  Scan,
  Settings,
  Upload,
  User,
  X,
} from "lucide-react";
import { useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [autoArchiveSubmenuOpen, setAutoArchiveSubmenuOpen] = useState(false);

  const menuItems = [
    { icon: Home, label: "Dashboard", path: "/dashboard" },
    { icon: MessageSquare, label: "AI Agent", path: "/ai-agent" },
    { icon: Archive, label: "Arhiva Documente", path: "/db-archive" },
    { icon: FileText, label: "Documente Auto", path: "/auto-documents" },
    { icon: User, label: "Profil", path: "/profile" },
  ];

  // Add admin-only menu item for adding documents to archive
  if (user?.role === "official") {
    menuItems.splice(-1, 0, {
      icon: Plus,
      label: "Adaugă în Arhivă",
      path: "/add-to-archive",
    });
  }

  const autoArchiveSubItems = [
    { icon: Upload, label: "Upload PDF", path: "/auto-archive/upload" },
    { icon: Scan, label: "Scan din imprimantă", path: "/auto-archive/scan" },
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    setSidebarOpen(false);
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const toggleAutoArchiveSubmenu = () => {
    setAutoArchiveSubmenuOpen(!autoArchiveSubmenuOpen);
  };

  const isAutoArchiveActive = location.pathname.startsWith("/auto-archive");

  return (
    <div className="min-h-screen bg-secondary-50 flex">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`
        fixed lg:static inset-y-0 left-0 z-50
        w-64 bg-white shadow-xl border-r border-secondary-200
        transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
      `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-secondary-200">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-bold text-primary-700">
                e-Guvernare
              </h1>
              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden"
                onClick={() => setSidebarOpen(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
          </div>

          {/* User info */}
          <div className="p-6 border-b border-secondary-200">
            <div className="flex items-center space-x-3">
              <Avatar>
                <AvatarImage src={user?.avatar} />
                <AvatarFallback>
                  {user?.name
                    ?.split(" ")
                    .map((n) => n[0])
                    .join("")}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.name}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {user?.role === "citizen" ? "Cetățean" : "Funcționar Public"}
                </p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {menuItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => handleNavigation(item.path)}
                  className={`
                    w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left
                    transition-all duration-200 hover:bg-primary-50
                    ${
                      isActive
                        ? "bg-primary-100 text-primary-700 border-r-2 border-primary-700"
                        : "text-gray-600 hover:text-primary-700"
                    }
                  `}
                >
                  <item.icon className="h-5 w-5" />
                  <span className="font-medium">{item.label}</span>
                </button>
              );
            })}

            {/* Auto Archive with submenu - only for officials */}
            {user?.role === "official" && (
              <div className="space-y-1">
                <button
                  onClick={toggleAutoArchiveSubmenu}
                  className={`
                    w-full flex items-center justify-between px-3 py-2 rounded-lg text-left
                    transition-all duration-200 hover:bg-primary-50
                    ${
                      isAutoArchiveActive
                        ? "bg-primary-100 text-primary-700 border-r-2 border-primary-700"
                        : "text-gray-600 hover:text-primary-700"
                    }
                  `}
                >
                  <div className="flex items-center space-x-3">
                    <Archive className="h-5 w-5" />
                    <span className="font-medium">
                      Adaugă în arhivă - automat
                    </span>
                  </div>
                  <ChevronDown
                    className={`h-4 w-4 transition-transform duration-200 ${
                      autoArchiveSubmenuOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>

                {/* Submenu */}
                <div
                  className={`ml-6 space-y-1 overflow-hidden transition-all duration-200 ${
                    autoArchiveSubmenuOpen
                      ? "max-h-32 opacity-100"
                      : "max-h-0 opacity-0"
                  }`}
                >
                  {autoArchiveSubItems.map((subItem) => {
                    const isSubActive = location.pathname === subItem.path;
                    return (
                      <button
                        key={subItem.path}
                        onClick={() => handleNavigation(subItem.path)}
                        className={`
                          w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left text-sm
                          transition-all duration-200 hover:bg-primary-50
                          ${
                            isSubActive
                              ? "bg-primary-50 text-primary-700 font-medium"
                              : "text-gray-600 hover:text-primary-700"
                          }
                        `}
                      >
                        <subItem.icon className="h-4 w-4" />
                        <span>{subItem.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-secondary-200 space-y-2">
            <Button
              variant="ghost"
              className="w-full justify-start"
              onClick={() => handleNavigation("/settings")}
            >
              <Settings className="h-5 w-5 mr-3" />
              Setări
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
              onClick={handleLogout}
            >
              <LogOut className="h-5 w-5 mr-3" />
              Deconectare
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Top bar */}
        <header className="bg-white shadow-sm border-b border-secondary-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              size="sm"
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </Button>

            <div className="hidden lg:block">
              <h2 className="text-lg font-semibold text-gray-900">
                {autoArchiveSubItems.find(
                  (item) => item.path === location.pathname
                )?.label ||
                  menuItems.find((item) => item.path === location.pathname)
                    ?.label ||
                  "Dashboard"}
              </h2>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">
                Bun venit, {user?.name}
              </span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
