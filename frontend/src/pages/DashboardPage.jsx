import { useEffect } from "react";
import { useAuth } from "../hooks/useAuth";
import { useDashboardData } from "../hooks/useDashboardData";
import { useCustomerDashboard } from "../hooks/useCustomerDashboard";
import { CrudCard } from "../components/forms/CrudCard";
import { InputField } from "../components/ui/InputField";
import { StatCard } from "../components/ui/StatCard";

export function DashboardPage() {
  const { logout, authType } = useAuth();
  const isCustomer = authType === "customer";
  const {
    summary,
    loading,
    error: customerError,
    refreshSummary,
    vehicleForm,
    savingVehicle,
    updateVehicleForm,
    submitVehicle: submitCustomerVehicle,
  } = useCustomerDashboard();
  const {
    forms,
    data,
    cacheMeta,
    error,
    taskStatus,
    stats,
    setForms,
    refreshData,
    updateForm,
    submitGarage,
    submitCustomer,
    submitVehicle,
    submitBooking,
    submitInvoiceTask,
  } = useDashboardData();

  useEffect(() => {
    if (isCustomer) {
      refreshSummary().catch(() => null);
      return;
    }
    refreshData().catch(() => null);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  if (isCustomer) {
    const customerStats = [
      { label: "Invoices", value: summary.invoices.length },
      { label: "Garage", value: summary.garage_name ? 1 : 0 },
      { label: "Staff", value: summary.staff_names.length },
    ];

    return (
      <div className="min-h-screen bg-[#f8fbf1] text-slate-900">
        <div className="mx-auto max-w-7xl p-6 space-y-6">
          <header className="rounded-2xl border border-slate-200 bg-white p-6 flex items-center justify-between shadow-sm">
            <div>
              <h1 className="text-3xl font-bold">Customer Dashboard</h1>
              <p className="text-slate-600 mt-2">Vehicle and invoice details only</p>
            </div>
            <button onClick={logout} className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-700 hover:border-slate-400">Logout</button>
          </header>

          {customerError && <div className="rounded-lg border border-rose-400/40 bg-rose-500/10 p-3 text-rose-700">{customerError}</div>}

          <section className="grid gap-4 md:grid-cols-3">
            {customerStats.map((s) => (
              <StatCard key={s.label} label={s.label} value={s.value} />
            ))}
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-xl font-semibold mb-3">Garage & Staff</h2>
            <p className="text-slate-700">Garage: {summary.garage_name || "Not assigned yet"}</p>
            <p className="text-slate-700 mt-1">
              Staff: {summary.staff_names.length ? summary.staff_names.join(", ") : "Not assigned yet"}
            </p>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-xl font-semibold mb-3">Add Vehicle</h2>
            <form
              className="space-y-3"
              onSubmit={(e) => {
                e.preventDefault();
                submitCustomerVehicle();
              }}
            >
              <InputField
                value={vehicleForm.registration_number}
                onChange={(v) => updateVehicleForm("registration_number", v)}
                placeholder="Registration number"
              />
              <InputField value={vehicleForm.make} onChange={(v) => updateVehicleForm("make", v)} placeholder="Make" />
              <InputField value={vehicleForm.model} onChange={(v) => updateVehicleForm("model", v)} placeholder="Model" />
              <InputField value={vehicleForm.year} onChange={(v) => updateVehicleForm("year", v)} placeholder="Year" type="number" />
              <button
                type="submit"
                disabled={savingVehicle}
                className="rounded-lg bg-[#81bf24] px-3 py-2 font-semibold text-white hover:bg-[#73ab1f] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {savingVehicle ? "Adding..." : "Add Vehicle"}
              </button>
            </form>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-xl font-semibold mb-3">My Vehicles</h2>
            {loading ? (
              <p className="text-slate-600">Loading vehicles...</p>
            ) : summary.vehicles.length === 0 ? (
              <p className="text-slate-600">No vehicles found.</p>
            ) : (
              <div className="space-y-2">
                {summary.vehicles.map((vehicle) => (
                  <div key={vehicle.id} className="rounded-lg border border-slate-200 p-3">
                    <p className="font-medium text-slate-800">{vehicle.registration_number}</p>
                    <p className="text-sm text-slate-600">{vehicle.make} {vehicle.model} ({vehicle.year})</p>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-xl font-semibold mb-3">My Invoices</h2>
            {loading ? (
              <p className="text-slate-600">Loading invoices...</p>
            ) : summary.invoices.length === 0 ? (
              <p className="text-slate-600">No invoices found.</p>
            ) : (
              <div className="space-y-2">
                {summary.invoices.map((invoice) => (
                  <div key={invoice.invoice_id} className="rounded-lg border border-slate-200 p-3">
                    <p className="font-medium text-slate-800">
                      Status: <span className="text-[#5f8f1a]">{invoice.payment_status}</span>
                    </p>
                    <p className="text-sm text-slate-600">Vehicle: {invoice.vehicle_registration_number}</p>
                    <p className="text-sm text-slate-600">Amount: {invoice.total_amount}</p>
                    <p className="text-sm text-slate-600">Garage: {invoice.garage_name}</p>
                    <p className="text-sm text-slate-600">Staff: {invoice.staff_name || "Not assigned"}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f8fbf1] text-slate-900">
      <div className="mx-auto max-w-7xl p-6 space-y-6">
        <header className="rounded-2xl border border-slate-200 bg-white p-6 flex items-center justify-between shadow-sm">
          <div>
            <h1 className="text-3xl font-bold">GarageFlow Dashboard</h1>
            <p className="text-slate-600 mt-2">Logged in as: {authType}</p>
          </div>
          <button onClick={logout} className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-700 hover:border-slate-400">Logout</button>
        </header>

        {error && <div className="rounded-lg border border-rose-400/40 bg-rose-500/10 p-3 text-rose-700">{error}</div>}

        <section className="grid gap-4 md:grid-cols-4">
          {stats.map((s) => (
            <StatCard key={s.label} label={s.label} value={s.value} />
          ))}
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <CrudCard title={`Garages (${cacheMeta.garage})`} onSubmit={submitGarage} readOnly={isCustomer}>
            <InputField value={forms.garage.name} onChange={(v) => updateForm("garage", "name", v)} placeholder="Garage name" />
            <InputField value={forms.garage.email} onChange={(v) => updateForm("garage", "email", v)} placeholder="Garage email" />
            <InputField value={forms.garage.address} onChange={(v) => updateForm("garage", "address", v)} placeholder="Address" />
            <InputField value={forms.garage.phone} onChange={(v) => updateForm("garage", "phone", v)} placeholder="Phone" />
          </CrudCard>

          <CrudCard title={`Customers (${cacheMeta.customer})`} onSubmit={submitCustomer} readOnly={isCustomer}>
            <InputField value={forms.customer.name} onChange={(v) => updateForm("customer", "name", v)} placeholder="Customer name" />
            <InputField value={forms.customer.email} onChange={(v) => updateForm("customer", "email", v)} placeholder="Customer email" />
            <InputField value={forms.customer.phone} onChange={(v) => updateForm("customer", "phone", v)} placeholder="Phone" />
            <InputField value={forms.customer.password} onChange={(v) => updateForm("customer", "password", v)} placeholder="Password" type="password" />
          </CrudCard>

          <CrudCard title="Vehicles" onSubmit={submitVehicle} readOnly={isCustomer}>
            <select
              value={forms.vehicle.customer_id}
              onChange={(e) => updateForm("vehicle", "customer_id", e.target.value)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-[#81bf24]"
            >
              <option value="">Select customer</option>
              {data.customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name} ({customer.phone})
                </option>
              ))}
            </select>
            <InputField value={forms.vehicle.registration_number} onChange={(v) => updateForm("vehicle", "registration_number", v)} placeholder="Registration number" />
            <InputField value={forms.vehicle.make} onChange={(v) => updateForm("vehicle", "make", v)} placeholder="Make" />
            <InputField value={forms.vehicle.model} onChange={(v) => updateForm("vehicle", "model", v)} placeholder="Model" />
            <InputField value={forms.vehicle.year} onChange={(v) => updateForm("vehicle", "year", v)} placeholder="Year" type="number" />
          </CrudCard>

          <CrudCard title="Bookings" onSubmit={submitBooking} readOnly={isCustomer}>
            <select
              value={forms.booking.garage_id}
              onChange={(e) => updateForm("booking", "garage_id", e.target.value)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-[#81bf24]"
            >
              <option value="">Select garage</option>
              {data.garages.map((garage) => (
                <option key={garage.id} value={garage.id}>
                  {garage.name} ({garage.phone})
                </option>
              ))}
            </select>
            <select
              value={forms.booking.customer_id}
              onChange={(e) => updateForm("booking", "customer_id", e.target.value)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-[#81bf24]"
            >
              <option value="">Select customer</option>
              {data.customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name} ({customer.phone})
                </option>
              ))}
            </select>
            <select
              value={forms.booking.vehicle_id}
              onChange={(e) => updateForm("booking", "vehicle_id", e.target.value)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-[#81bf24]"
            >
              <option value="">Select vehicle</option>
              {data.vehicles.map((vehicle) => (
                <option key={vehicle.id} value={vehicle.id}>
                  {vehicle.registration_number}
                </option>
              ))}
            </select>
            <InputField value={forms.booking.service_type} onChange={(v) => updateForm("booking", "service_type", v)} placeholder="Service type" />
            <InputField value={forms.booking.booking_date} onChange={(v) => updateForm("booking", "booking_date", v)} type="date" />
            <InputField value={forms.booking.time_slot} onChange={(v) => updateForm("booking", "time_slot", v)} placeholder="Time slot" />
          </CrudCard>
        </section>

        {!isCustomer && (
          <section className="rounded-2xl border border-slate-200 bg-white p-4 space-y-3 shadow-sm">
            <h2 className="text-xl font-semibold">Invoice PDF (Celery)</h2>
            <div className="flex flex-col gap-3 md:flex-row">
              <InputField value={forms.invoiceId} onChange={(v) => setForms((p) => ({ ...p, invoiceId: v }))} placeholder="Invoice ID" />
              <button onClick={submitInvoiceTask} className="rounded-lg bg-[#81bf24] px-3 py-2 font-semibold text-white hover:bg-[#73ab1f]">Queue PDF</button>
            </div>
            {taskStatus && (
              <div className="text-sm text-slate-700">
                <p>Task: {taskStatus.task_id}</p>
                <p>Status: {taskStatus.status}</p>
                {taskStatus.status === "SUCCESS" && (
                  <a className="text-[#5f8f1a] underline" href={taskStatus.download_url} target="_blank" rel="noreferrer">
                    Download PDF
                  </a>
                )}
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  );
}
