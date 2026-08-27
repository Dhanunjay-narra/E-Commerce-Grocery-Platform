"use client";
import React, { createContext, useContext, useState, useEffect } from "react";

export interface UserSession {
  id: string;
  email: string;
  fullName: string;
  role: string;
  token: string;
}

interface AuthContextType {
  user: UserSession | null;
  login: (email: string, token: string, fullName: string, role: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserSession | null>(() => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("fc_token");
      const email = localStorage.getItem("fc_email");
      const fullName = localStorage.getItem("fc_name");
      const role = localStorage.getItem("fc_role");
      if (token && email) {
        return { id: "user-1", email, fullName: fullName || "Valued Customer", role: role || "CUSTOMER", token };
      }
    }
    return null;
  });

  const login = (email: string, token: string, fullName: string, role: string) => {
    const session = { id: "user-1", email, fullName, role, token };
    setUser(session);
    if (typeof window !== "undefined") {
      localStorage.setItem("fc_token", token);
      localStorage.setItem("fc_email", email);
      localStorage.setItem("fc_name", fullName);
      localStorage.setItem("fc_role", role);
    }
  };

  const logout = () => {
    setUser(null);
    if (typeof window !== "undefined") {
      localStorage.removeItem("fc_token");
      localStorage.removeItem("fc_email");
      localStorage.removeItem("fc_name");
      localStorage.removeItem("fc_role");
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
