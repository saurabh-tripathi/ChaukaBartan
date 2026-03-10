"use client";
import { useEffect, useState } from "react";
import { Dashboard, DailyDashboard } from "@/lib/api";

function StatCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  );
}

function pct(n: number) { return `${Math.round(n * 100)}%`; }

export default function DashboardPage() {
  const [data, setData] = useState<DailyDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);
  const today = new Date().toISOString().slice(0, 10);

  useEffect(() => {
    Dashboard.daily(today).then(setData).catch((e) => setError(e.message));
  }, [today]);

  if (error) return <div className="text-red-500 bg-red-50 rounded p-4">{error}</div>;
  if (!data) return <p className="text-gray-400">Loading…</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">
        Dashboard <span className="text-gray-400 text-base font-normal">{data.date}</span>
      </h1>

      {data.plan && (
        <section>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Today&apos;s Plan</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <StatCard label="Completion" value={pct(data.plan.completion_rate)} />
            <StatCard label="Pending" value={data.plan.pending} />
            <StatCard label="Completed" value={data.plan.completed} />
            <StatCard label="Skipped" value={data.plan.skipped} />
          </div>
        </section>
      )}

      <section>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Tasks</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard label="Completion" value={pct(data.tasks.completion_rate)} />
          <StatCard label="Completed" value={data.tasks.completed} />
          <StatCard label="Pending" value={data.tasks.pending} />
          <StatCard label="In Progress" value={data.tasks.in_progress} />
          {data.tasks.avg_difficulty != null && (
            <StatCard label="Avg Difficulty" value={`${data.tasks.avg_difficulty.toFixed(1)}/5`} />
          )}
          {data.tasks.avg_satisfaction != null && (
            <StatCard label="Avg Satisfaction" value={`${data.tasks.avg_satisfaction.toFixed(1)}/5`} />
          )}
          {data.tasks.total_duration_minutes > 0 && (
            <StatCard label="Time Logged" value={`${data.tasks.total_duration_minutes}m`} />
          )}
        </div>
      </section>

      <section>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Habits</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard label="Logged Today" value={data.habits.logged} />
        </div>
      </section>

      {!data.plan && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-700">
          No plan for today. <a href="/plans" className="underline font-medium">Generate one →</a>
        </div>
      )}
    </div>
  );
}
