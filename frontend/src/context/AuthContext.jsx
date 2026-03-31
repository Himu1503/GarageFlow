import { createContext, useEffect, useMemo, useState } from "react";
import { clearTokens, getAccessToken, setTokens } from "../services/apiClient";
import { loginCustomer, loginUser } from "../services/authService";
import { getErrorMessage } from "../utils/error";

const AUTH_TYPE_KEY = "gf_auth_type";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(getAccessToken()));
  const [authType, setAuthType] = useState(localStorage.getItem(AUTH_TYPE_KEY) || "user");
  const [loading, setLoading] = useState(false);
  const [authError, setAuthError] = useState("");

  useEffect(() => {
    setIsAuthenticated(Boolean(getAccessToken()));
  }, []);

  async function login(kind, email, password) {
    setLoading(true);
    setAuthError("");
    try {
      const payload = kind === "customer" ? await loginCustomer(email, password) : await loginUser(email, password);
      setTokens({
        accessToken: payload.access_token,
        refreshToken: payload.refresh_token,
      });
      localStorage.setItem(AUTH_TYPE_KEY, kind);
      setAuthType(kind);
      setIsAuthenticated(true);
      return true;
    } catch (err) {
      setAuthError(getErrorMessage(err, "Login failed"));
      setIsAuthenticated(false);
      return false;
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    clearTokens();
    setIsAuthenticated(false);
  }

  const value = useMemo(
    () => ({ isAuthenticated, authType, login, logout, loading, authError }),
    [isAuthenticated, authType, loading, authError]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
