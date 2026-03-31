import { useMemo, useState } from "react";
import {
  createBooking,
  createCustomer,
  createGarage,
  createVehicle,
  getBookings,
  getCustomers,
  getGarages,
  getInvoiceDownloadUrl,
  getInvoiceTask,
  getVehicles,
  queueInvoicePdf,
} from "../services/domainService";
import { getErrorMessage } from "../utils/error";

const seedState = {
  garage: { name: "", email: "", address: "", phone: "" },
  customer: { name: "", email: "", phone: "", password: "" },
  vehicle: { customer_id: "", registration_number: "", make: "", model: "", year: "" },
  booking: {
    garage_id: "",
    customer_id: "",
    vehicle_id: "",
    service_type: "",
    booking_date: "",
    time_slot: "",
    status: "PENDING",
    notes: "",
  },
  invoiceId: "",
};

export function useDashboardData() {
  const [forms, setForms] = useState(seedState);
  const [data, setData] = useState({ garages: [], customers: [], vehicles: [], bookings: [] });
  const [cacheMeta, setCacheMeta] = useState({ garage: "N/A", customer: "N/A" });
  const [error, setError] = useState("");
  const [taskStatus, setTaskStatus] = useState(null);

  const stats = useMemo(
    () => [
      { label: "Garages", value: data.garages.length },
      { label: "Customers", value: data.customers.length },
      { label: "Vehicles", value: data.vehicles.length },
      { label: "Bookings", value: data.bookings.length },
    ],
    [data]
  );

  async function refreshData() {
    const [garageRes, customerRes, vehicles, bookings] = await Promise.all([
      getGarages(),
      getCustomers(),
      getVehicles(),
      getBookings(),
    ]);
    setData({ garages: garageRes.data, customers: customerRes.data, vehicles, bookings });
    setCacheMeta({ garage: garageRes.cache, customer: customerRes.cache });
  }

  function updateForm(section, field, value) {
    setForms((prev) => ({ ...prev, [section]: { ...prev[section], [field]: value } }));
  }

  async function runCreateAction(action, payload, section) {
    setError("");
    try {
      await action(payload);
      await refreshData();
      if (section) {
        setForms((prev) => ({ ...prev, [section]: seedState[section] }));
      }
    } catch (err) {
      setError(getErrorMessage(err, "Request failed"));
    }
  }

  async function submitGarage() {
    return runCreateAction(createGarage, forms.garage, "garage");
  }

  async function submitCustomer() {
    return runCreateAction(createCustomer, forms.customer, "customer");
  }

  async function submitVehicle() {
    return runCreateAction(createVehicle, { ...forms.vehicle, year: Number(forms.vehicle.year) }, "vehicle");
  }

  async function submitBooking() {
    return runCreateAction(createBooking, forms.booking, "booking");
  }

  async function submitInvoiceTask() {
    setError("");
    try {
      const queued = await queueInvoicePdf(forms.invoiceId);
      const status = await getInvoiceTask(queued.task_id);
      setTaskStatus({
        ...status,
        task_id: queued.task_id,
        download_url: getInvoiceDownloadUrl(queued.task_id),
      });
    } catch (err) {
      setError(getErrorMessage(err, "Invoice task failed"));
    }
  }

  return {
    forms,
    data,
    cacheMeta,
    error,
    taskStatus,
    stats,
    setError,
    setForms,
    refreshData,
    updateForm,
    submitGarage,
    submitCustomer,
    submitVehicle,
    submitBooking,
    submitInvoiceTask,
  };
}
