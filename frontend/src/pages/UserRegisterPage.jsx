import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { registerUser } from "../services/authService";
import { getErrorMessage } from "../utils/error";

export function UserRegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "STAFF",
    garage_name: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const update = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  async function onSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await registerUser(form);
      navigate("/login/user");
    } catch (err) {
      setError(getErrorMessage(err, "Registration failed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#f8fbf1] text-slate-900 flex items-center justify-center p-6">
      <form onSubmit={onSubmit} className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-6 space-y-4 shadow-sm">
        <h1 className="text-2xl font-bold">User Register</h1>
        <p className="text-slate-600">Create staff/admin/manager account.</p>
        <input value={form.name} onChange={(e) => update("name", e.target.value)} placeholder="Name" className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2" />
        <input value={form.email} onChange={(e) => update("email", e.target.value)} placeholder="Email" className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2" />
        <input type="password" value={form.password} onChange={(e) => update("password", e.target.value)} placeholder="Password" className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2" />
        <select value={form.role} onChange={(e) => update("role", e.target.value)} className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2">
          <option value="STAFF">STAFF</option>
          <option value="MANAGER">MANAGER</option>
          <option value="ADMIN">ADMIN</option>
        </select>
        <input value={form.garage_name} onChange={(e) => update("garage_name", e.target.value)} placeholder="Garage Name" className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2" />
        {error && <div className="rounded-md bg-rose-500/10 border border-rose-400/40 p-2 text-sm text-rose-700">{error}</div>}
        <button disabled={loading} className="w-full rounded-lg bg-[#81bf24] px-3 py-2 font-semibold text-white hover:bg-[#73ab1f]">
          {loading ? "Creating..." : "Create Account"}
        </button>
        <p className="text-sm text-slate-600">
          Already have account? <Link to="/login/user" className="text-[#5f8f1a] underline">User login</Link>
        </p>
      </form>
    </div>
  );
}
