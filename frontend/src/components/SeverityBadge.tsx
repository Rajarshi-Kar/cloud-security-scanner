const COLORS: Record<string, string> = {
  critical: "bg-red-700 text-white",
  high: "bg-red-500 text-white",
  medium: "bg-amber-400 text-black",
  low: "bg-yellow-200 text-black",
  info: "bg-slate-200 text-black",
  pending: "bg-slate-200 text-black",
  running: "bg-blue-200 text-black",
  completed: "bg-green-200 text-black",
  failed: "bg-red-200 text-black",
};

export default function SeverityBadge({ label }: { label: string }) {
  const className = COLORS[label] ?? "bg-slate-200 text-black";
  return (
    <span className={`rounded px-2 py-0.5 text-xs font-medium uppercase ${className}`}>{label}</span>
  );
}
