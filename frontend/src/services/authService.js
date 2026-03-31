import { apiClient } from "./apiClient";

export async function loginUser(email, password) {
  const res = await apiClient.post("/auth/login", { email, password });
  return res.data;
}

export async function loginCustomer(email, password) {
  const res = await apiClient.post("/auth/customer/login", { email, password });
  return res.data;
}

export async function registerUser(payload) {
  const res = await apiClient.post("/auth/register", payload);
  return res.data;
}

export async function registerCustomer(payload) {
  const res = await apiClient.post("/auth/customer/register", payload);
  return res.data;
}
