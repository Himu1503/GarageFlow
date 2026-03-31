import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

const ACCESS_TOKEN_KEY = "gf_access_token";
const REFRESH_TOKEN_KEY = "gf_refresh_token";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

let refreshInFlight = null;

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setTokens({ accessToken, refreshToken }) {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

async function refreshTokens() {
  if (refreshInFlight) return refreshInFlight;

  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refreshToken) throw new Error("No refresh token");

  refreshInFlight = apiClient
    .post("/auth/refresh", { refresh_token: refreshToken })
    .then((res) => {
      setTokens({
        accessToken: res.data.access_token,
        refreshToken: res.data.refresh_token,
      });
      return res.data.access_token;
    })
    .finally(() => {
      refreshInFlight = null;
    });

  return refreshInFlight;
}

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error?.response?.status;
    if (!originalRequest || originalRequest._retry || status !== 401) {
      return Promise.reject(error);
    }

    if (
      originalRequest.url?.includes("/auth/login") ||
      originalRequest.url?.includes("/auth/customer/login") ||
      originalRequest.url?.includes("/auth/refresh")
    ) {
      return Promise.reject(error);
    }

    try {
      const newAccessToken = await refreshTokens();
      originalRequest._retry = true;
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      clearTokens();
      return Promise.reject(refreshError);
    }
  }
);

export function getApiBaseUrl() {
  return API_BASE_URL;
}
