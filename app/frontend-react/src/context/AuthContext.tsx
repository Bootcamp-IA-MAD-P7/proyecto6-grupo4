import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { apiFetch, clearToken, getToken, setToken } from "../lib/api";
import type { AuthResponse, User } from "../lib/types";

interface RegisterPayload {
  first_name: string;
  last_name: string;
  birth_date: string;
  phone: string;
  email: string;
  password: string;
  accepts_terms: boolean;
}

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const USER_KEY = "laliga_predictor_user";

function loadStoredUser(): User | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => (getToken() ? loadStoredUser() : null));

  const applySession = useCallback((payload: AuthResponse) => {
    setToken(payload.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(payload.user));
    setUser(payload.user);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const payload = await apiFetch<AuthResponse>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      applySession(payload);
    },
    [applySession],
  );

  const register = useCallback(
    async (data: RegisterPayload) => {
      const payload = await apiFetch<AuthResponse>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
      });
      applySession(payload);
    },
    [applySession],
  );

  const logout = useCallback(() => {
    clearToken();
    localStorage.removeItem(USER_KEY);
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, isAuthenticated: user !== null, login, register, logout }),
    [user, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}
