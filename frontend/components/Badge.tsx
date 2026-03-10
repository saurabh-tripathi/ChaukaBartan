const colors: Record<string, string> = {
  LOW: "bg-gray-100 text-gray-600",
  MEDIUM: "bg-blue-100 text-blue-700",
  HIGH: "bg-orange-100 text-orange-700",
  CRITICAL: "bg-red-100 text-red-700",
  ACTIVE: "bg-green-100 text-green-700",
  COMPLETED: "bg-indigo-100 text-indigo-700",
  PAUSED: "bg-yellow-100 text-yellow-700",
  ABANDONED: "bg-gray-100 text-gray-500",
  ARCHIVED: "bg-gray-100 text-gray-500",
  PENDING: "bg-yellow-100 text-yellow-700",
  IN_PROGRESS: "bg-blue-100 text-blue-700",
  SKIPPED: "bg-gray-100 text-gray-500",
  DRAFT: "bg-gray-100 text-gray-600",
};

export function Badge({ value }: { value: string }) {
  const cls = colors[value] ?? "bg-gray-100 text-gray-600";
  return (
    <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${cls}`}>
      {value.replace("_", " ")}
    </span>
  );
}
