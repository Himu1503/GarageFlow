export function CrudCard({ title, children, onSubmit, readOnly = false }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-lg font-semibold">{title}</h3>
      <div className="grid gap-2">{children}</div>
      {readOnly ? (
        <p className="mt-3 text-sm text-slate-500">Read-only for customer accounts.</p>
      ) : (
        <button onClick={onSubmit} className="mt-3 rounded-lg bg-[#81bf24] px-3 py-2 font-semibold text-white hover:bg-[#73ab1f]">
          Create
        </button>
      )}
    </div>
  );
}
