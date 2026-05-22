import { useEffect, useMemo, useState } from "react";
import type { PropsWithChildren } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AxiosError } from "axios";

import { fetchCurrentUser, login, logout } from "../api/auth";
import { AUTH_TOKEN_STORAGE_KEY } from "../api/client";
import { AuthContext } from "./authContext";
import type { AuthContextValue } from "./authContext";

export function AuthProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient();
  const [token, setToken] = useState(() => window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY));
  const [loginError, setLoginError] = useState<string | null>(null);

  const currentUserQuery = useQuery({
    queryKey: ["auth", "me"],
    queryFn: fetchCurrentUser,
    enabled: Boolean(token),
    retry: false,
  });

  useEffect(() => {
    if (currentUserQuery.error instanceof AxiosError && currentUserQuery.error.response?.status === 401) {
      window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
      setToken(null);
      queryClient.removeQueries({ queryKey: ["auth"] });
    }
  }, [currentUserQuery.error, queryClient]);

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      window.localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, data.token);
      setToken(data.token);
      setLoginError(null);
      queryClient.setQueryData(["auth", "me"], data.user);
    },
    onError: (error) => {
      setLoginError(getAuthErrorMessage(error));
    },
  });

  const logoutMutation = useMutation({
    mutationFn: logout,
    onSettled: () => {
      window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
      setToken(null);
      setLoginError(null);
      queryClient.removeQueries({ queryKey: ["auth"] });
    },
  });

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user: currentUserQuery.data ?? null,
      isAuthenticated: Boolean(token && currentUserQuery.data),
      isLoading: Boolean(token) && currentUserQuery.isLoading,
      loginError,
      login: async (payload) => {
        await loginMutation.mutateAsync(payload);
      },
      logout: async () => {
        await logoutMutation.mutateAsync();
      },
    }),
    [currentUserQuery.data, currentUserQuery.isLoading, loginError, loginMutation, logoutMutation, token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

function getAuthErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail;

    if (Array.isArray(detail)) {
      return detail.join(" ");
    }

    if (typeof detail === "string") {
      return detail;
    }
  }

  return "Не удалось войти. Проверьте логин и пароль.";
}
