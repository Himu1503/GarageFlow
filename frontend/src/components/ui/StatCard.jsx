export function StatCard({ label, value }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-slate-600">{label}</p>
      <p className="text-2xl font-bold text-[#5f8f1a]">{value}</p>
    </div>
  );
}
