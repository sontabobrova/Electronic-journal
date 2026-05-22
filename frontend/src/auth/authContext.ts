import { createContext, useContext } from "react";

import type { CurrentUser, LoginPayload } from "../api/auth";

export type AuthContextValue = {
  token: string | null;
  user: CurrentUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  loginError: string | null;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return context;
}
