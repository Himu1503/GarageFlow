import { apiClient, getApiBaseUrl } from "./apiClient";

export async function getGarages() {
  const res = await apiClient.get("/garage");
  return { data: res.data, cache: res.headers["x-cache"] || "N/A" };
}

export async function getCustomers() {
  const res = await apiClient.get("/customer");
  return { data: res.data, cache: res.headers["x-cache"] || "N/A" };
}

export async function getVehicles() {
  const res = await apiClient.get("/vehicle");
  return res.data;
}

export async function getBookings() {
  const res = await apiClient.get("/booking");
  return res.data;
}

export async function getCustomerSummary() {
  const res = await apiClient.get("/customer/me/summary");
  return res.data;
}

export async function createGarage(payload) {
  const res = await apiClient.post("/garage", payload);
  return res.data;
}

export async function createCustomer(payload) {
  const res = await apiClient.post("/customer", payload);
  return res.data;
}

export async function createVehicle(payload) {
  const res = await apiClient.post("/vehicle", payload);
  return res.data;
}

export async function createBooking(payload) {
  const res = await apiClient.post("/booking", payload);
  return res.data;
}

export async function queueInvoicePdf(invoiceId) {
  const res = await apiClient.post(`/invoice/${invoiceId}/pdf`);
  return res.data;
}

export async function getInvoiceTask(taskId) {
  const res = await apiClient.get(`/invoice/pdf/tasks/${taskId}`);
  return res.data;
}

export function getInvoiceDownloadUrl(taskId) {
  return `${getApiBaseUrl()}/invoice/pdf/tasks/${taskId}/download`;
}
