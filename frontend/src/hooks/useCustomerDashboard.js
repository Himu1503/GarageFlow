import { useState } from "react";
import { createVehicle, getCustomerSummary } from "../services/domainService";
import { getErrorMessage } from "../utils/error";

export function useCustomerDashboard() {
  const [summary, setSummary] = useState({
    garage_name: null,
    staff_names: [],
    vehicles: [],
    invoices: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [vehicleForm, setVehicleForm] = useState({
    registration_number: "",
    make: "",
    model: "",
    year: "",
  });
  const [savingVehicle, setSavingVehicle] = useState(false);

  async function refreshSummary() {
    setLoading(true);
    setError("");
    try {
      const res = await getCustomerSummary();
      setSummary(res);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to load customer dashboard"));
    } finally {
      setLoading(false);
    }
  }

  function updateVehicleForm(field, value) {
    setVehicleForm((prev) => ({ ...prev, [field]: value }));
  }

  async function submitVehicle() {
    setSavingVehicle(true);
    setError("");
    try {
      await createVehicle({
        registration_number: vehicleForm.registration_number,
        make: vehicleForm.make,
        model: vehicleForm.model,
        year: Number(vehicleForm.year),
      });
      setVehicleForm({ registration_number: "", make: "", model: "", year: "" });
      await refreshSummary();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to add vehicle"));
    } finally {
      setSavingVehicle(false);
    }
  }

  return {
    summary,
    loading,
    error,
    refreshSummary,
    vehicleForm,
    savingVehicle,
    updateVehicleForm,
    submitVehicle,
  };
}
