import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../hooks/useAuth";

export function CustomerLoginPage() {
  const navigate = useNavigate();
  const { login, loading, authError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    const success = await login("customer", email, password);
    if (success) navigate("/dashboard");
  }

  return (
    <div className="min-h-screen bg-[#f8fbf1] text-slate-900 flex items-center justify-center p-6">
      <form onSubmit={onSubmit} className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 space-y-4 shadow-sm">
        <h1 className="text-2xl font-bold">Customer Login</h1>
        <p className="text-slate-600">Login as customer account.</p>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2" />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2" />
        {authError && <div className="rounded-md bg-rose-500/10 border border-rose-400/40 p-2 text-sm text-rose-700">{authError}</div>}
        <button disabled={loading} className="w-full rounded-lg bg-[#81bf24] px-3 py-2 font-semibold text-white hover:bg-[#73ab1f]">
          {loading ? "Signing in..." : "Sign in"}
        </button>
        <p className="text-sm text-slate-600">
          Staff/Admin? <Link to="/login/user" className="text-[#5f8f1a] underline">Use user login</Link>
        </p>
        <p className="text-sm text-slate-600">
          New customer? <Link to="/register/customer" className="text-[#5f8f1a] underline">Create customer account</Link>
        </p>
      </form>
    </div>
  );
}
