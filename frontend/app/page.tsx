"use client";
import { useEffect, useState } from "react";
import { Plans, Plan, ItemStatus } from "@/lib/api";
import { Badge } from "@/components/Badge";

// ── Donut Chart ────────────────────────────────────────────────────────────────

function DonutChart({ done, total, label, color }: { done: number; total: number; label: string; color: string }) {
  const r = 34;
  const circ = 2 * Math.PI * r;
  const ratio = total > 0 ? Math.min(done / total, 1) : 0;
  const dash = ratio * circ;

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width="110" height="110" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke="#e5e7eb" strokeWidth="11" />
        {total > 0 && (
          <circle
            cx="50" cy="50" r={r}
            fill="none" stroke={color} strokeWidth="11"
            strokeDasharray={`${dash} ${circ - dash}`}
            strokeLinecap="round"
            transform="rotate(-90 50 50)"
          />
        )}
        <text x="50" y="46" textAnchor="middle" fontSize="19" fontWeight="700" fill="#111827">
          {total > 0 ? Math.round(ratio * 100) : "—"}
          {total > 0 ? "%" : ""}
        </text>
        <text x="50" y="61" textAnchor="middle" fontSize="10" fill="#9ca3af">
          {done} / {total}
        </text>
      </svg>
      <p className="text-sm font-semibold text-gray-600">{label}</p>
    </div>
  );
}

// ── Status Pills ───────────────────────────────────────────────────────────────

const PILL_OPTIONS: { value: ItemStatus; label: string; active: string; inactive: string }[] = [
  { value: "PENDING",   label: "●", active: "bg-gray-200 text-gray-700",    inactive: "text-gray-300 hover:text-gray-500" },
  { value: "COMPLETED", label: "✓", active: "bg-green-100 text-green-700",  inactive: "text-gray-300 hover:text-green-500" },
  { value: "SKIPPED",   label: "—", active: "bg-yellow-100 text-yellow-700", inactive: "text-gray-300 hover:text-yellow-500" },
];

function StatusPills({ current, onChange }: { current: ItemStatus; onChange: (s: ItemStatus) => void }) {
  return (
    <div className="flex items-center gap-0.5 bg-gray-100 rounded-lg p-0.5">
      {PILL_OPTIONS.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          title={opt.value}
          className={`w-7 h-7 rounded-md text-sm font-bold transition-colors ${current === opt.value ? opt.active : opt.inactive}`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function formatDate(iso: string) {
  return new Date(iso + "T12:00:00").toLocaleDateString("en-US", {
    weekday: "long", month: "short", day: "numeric",
  });
}

function carryOverDays(scheduledDate: string, planDate: string): number {
  const a = new Date(scheduledDate + "T12:00:00");
  const b = new Date(planDate + "T12:00:00");
  return Math.floor((b.getTime() - a.getTime()) / (1000 * 60 * 60 * 24));
}

const DOT: Record<string, string> = {
  COMPLETED: "bg-green-500",
  PENDING: "bg-gray-300",
  SKIPPED: "bg-yellow-400",
};

// ── Page ───────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const today = new Date().toISOString().slice(0, 10);
  const [date, setDate] = useState(today);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Plans.byDate(date)
      .then(setPlan)
      .catch((e: Error) => {
        if (e.message.startsWith("404")) setPlan(null);
        else setError(e.message);
      })
      .finally(() => setLoading(false));
  }, [date]);

  const shiftDay = (n: number) => {
    const d = new Date(date + "T12:00:00");
    d.setDate(d.getDate() + n);
    setDate(d.toISOString().slice(0, 10));
  };

  const taskItems = plan?.items.filter((i) => i.task_instance != null) ?? [];
  const habitItems = plan?.items.filter((i) => i.habit != null) ?? [];
  const allItems = plan?.items ?? [];
  const done = (items: typeof allItems) => items.filter((i) => i.status === "COMPLETED").length;

  const updateItem = async (itemId: string, status: ItemStatus) => {
    if (!plan) return;
    // Optimistic update
    setPlan((p) => p ? { ...p, items: p.items.map((i) => i.id === itemId ? { ...i, status } : i) } : p);
    await Plans.updateItem(plan.id, itemId, { status }).catch(() => {
      // revert on error by re-fetching
      Plans.byDate(date).then(setPlan).catch(() => {});
    });
  };

  return (
    <div className="space-y-6">

      {/* ── Header + Day Nav ── */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="flex items-center gap-2">
          <button
            onClick={() => shiftDay(-1)}
            className="p-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-500 transition-colors"
          >
            ←
          </button>
          <span className="text-sm font-medium text-gray-700 w-44 text-center">{formatDate(date)}</span>
          <button
            onClick={() => shiftDay(1)}
            disabled={date >= today}
            className="p-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-500 disabled:opacity-30 transition-colors"
          >
            →
          </button>
          {date !== today && (
            <button
              onClick={() => setDate(today)}
              className="ml-1 text-xs text-indigo-600 hover:underline"
            >
              Today
            </button>
          )}
        </div>
      </div>

      {/* ── KPI Donuts ── */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 grid grid-cols-3 divide-x divide-gray-100">
        <div className="flex justify-center pr-4">
          <DonutChart done={done(allItems)} total={allItems.length} label="Total" color="#6366f1" />
        </div>
        <div className="flex justify-center px-4">
          <DonutChart done={done(taskItems)} total={taskItems.length} label="Tasks" color="#0ea5e9" />
        </div>
        <div className="flex justify-center pl-4">
          <DonutChart done={done(habitItems)} total={habitItems.length} label="Habits" color="#10b981" />
        </div>
      </div>

      {/* ── Plan Items ── */}
      <div>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
          {date === today ? "Today's Plan" : `Plan — ${formatDate(date)}`}
        </h2>

        {loading && <p className="text-gray-400 text-sm">Loading…</p>}
        {error && <div className="text-red-500 bg-red-50 rounded p-3 text-sm">{error}</div>}

        {!loading && !plan && !error && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-700">
            No plan for {date === today ? "today" : formatDate(date)}.
            {date === today && (
              <> <a href="/plans" className="underline font-medium">Generate one →</a></>
            )}
          </div>
        )}

        {plan && allItems.length === 0 && (
          <p className="text-gray-400 text-sm">This plan has no items.</p>
        )}

        {plan && allItems.length > 0 && (
          <div className="space-y-4">

            {taskItems.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Tasks</p>
                {taskItems.map((item) => {
                  const carried = item.task_instance
                    ? carryOverDays(item.task_instance.scheduled_date, date)
                    : 0;
                  return (
                    <div
                      key={item.id}
                      className={`bg-white border rounded-xl px-4 py-3 flex items-center justify-between gap-4 ${carried > 0 ? "border-orange-200" : "border-gray-200"}`}
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${DOT[item.status] ?? "bg-gray-300"}`} />
                        <span className={`text-sm font-medium truncate ${item.status === "COMPLETED" ? "line-through text-gray-400" : "text-gray-800"}`}>
                          {item.task_instance?.task.title}
                        </span>
                        {carried > 0 && (
                          <span className="shrink-0 text-xs font-semibold px-1.5 py-0.5 rounded bg-orange-100 text-orange-600">
                            +{carried}d
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <Badge value={item.task_instance!.task.priority} />
                        <StatusPills current={item.status} onChange={(s) => updateItem(item.id, s)} />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {habitItems.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Habits</p>
                {habitItems.map((item) => (
                  <div
                    key={item.id}
                    className="bg-white border border-gray-200 rounded-xl px-4 py-3 flex items-center justify-between gap-4"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${DOT[item.status] ?? "bg-gray-300"}`} />
                      <span className={`text-sm font-medium truncate ${item.status === "COMPLETED" ? "line-through text-gray-400" : "text-gray-800"}`}>
                        {item.habit?.title}
                      </span>
                      {(item.habit?.streak_count ?? 0) > 0 && (
                        <span className="shrink-0 text-xs font-semibold px-1.5 py-0.5 rounded bg-orange-100 text-orange-600">
                          🔥 {item.habit!.streak_count}d
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <Badge value={item.habit!.priority} />
                      <StatusPills current={item.status} onChange={(s) => updateItem(item.id, s)} />
                    </div>
                  </div>
                ))}
              </div>
            )}

          </div>
        )}
      </div>

    </div>
  );
}
