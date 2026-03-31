import { Link } from "react-router-dom";

export function LandingPage() {
  return (
    <div className="min-h-screen bg-[#f8fbf1] text-slate-900 selection:bg-[#81bf24]/30">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <header className="flex items-center justify-between">
          <h1 className="text-xl font-semibold tracking-wide">GarageFlow</h1>
          <Link
            to="/login/user"
            className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 transition hover:border-slate-400"
          >
            Login
          </Link>
        </header>

        <section className="mt-20 grid items-center gap-10 lg:grid-cols-2">
          <div className="space-y-5">
            <p className="inline-block rounded-full border border-[#81bf24]/40 bg-[#81bf24]/10 px-3 py-1 text-xs text-[#4f7c12]">
              Smart Garage Operations
            </p>
            <h2 className="text-5xl font-bold leading-tight">
              One clean workspace for garage, staff, and customer workflows
            </h2>
            <p className="text-slate-600">
              Manage bookings, vehicles, customer records, and invoice PDF generation with role-based access and fast APIs.
            </p>
            <div className="pt-3 flex flex-wrap items-center gap-3">
              <Link
                to="/register/user"
                className="rounded-md bg-[#81bf24] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#73ab1f]"
              >
                Create Account
              </Link>
              <Link
                to="/register/customer"
                className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 transition hover:border-slate-400"
              >
                Customer Signup
              </Link>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="grid gap-4 sm:grid-cols-2">
              <Feature title="JWT Security" description="Access + refresh token auth for users and customers." />
              <Feature title="Role Based Access" description="Admin, Manager, Staff and Customer permissions." />
              <Feature title="Invoice PDF" description="Background PDF generation with Celery + Redis." />
              <Feature title="Fast APIs" description="Cached list endpoints with cache-hit visibility." />
            </div>
          </div>
        </section>

        <section className="mt-16 grid gap-4 md:grid-cols-3">
          <Metric label="Bookings Managed" value="10k+" />
          <Metric label="Average Response" value="< 120ms" />
          <Metric label="Operational Visibility" value="Realtime" />
        </section>
      </div>
    </div>
  );
}

function Feature({ title, description }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-[#fcfef7] p-4">
      <h3 className="font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-slate-600">{description}</p>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-3xl font-bold text-[#5f8f1a]">{value}</p>
      <p className="mt-1 text-sm text-slate-600">{label}</p>
    </div>
  );
}
