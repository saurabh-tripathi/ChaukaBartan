"use client";
import { useEffect, useState } from "react";
import { Goals, Goal, GoalCreate, GoalTimeframe, Priority, GoalStatus } from "@/lib/api";
import { Badge } from "@/components/Badge";

const TIMEFRAMES: GoalTimeframe[] = ["THREE_MONTHS", "SIX_MONTHS", "ONE_YEAR", "FIVE_YEARS"];
const PRIORITIES: Priority[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
const STATUSES: GoalStatus[] = ["ACTIVE", "COMPLETED", "PAUSED", "ABANDONED"];

const blank: GoalCreate = { title: "", timeframe: "THREE_MONTHS", priority: "MEDIUM", status: "ACTIVE" };

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [form, setForm] = useState<GoalCreate>(blank);
  const [editing, setEditing] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () => Goals.list().then(setGoals).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const save = async () => {
    try {
      if (editing) { await Goals.update(editing, form); }
      else { await Goals.create(form); }
      setForm(blank); setEditing(null); setShowForm(false);
      load();
    } catch (e: unknown) { setError(e instanceof Error ? e.message : String(e)); }
  };

  const del = async (id: string) => {
    if (!confirm("Delete this goal?")) return;
    await Goals.delete(id).then(load).catch((e) => setError(e.message));
  };

  const startEdit = (g: Goal) => {
    setForm({ title: g.title, description: g.description ?? undefined, timeframe: g.timeframe, priority: g.priority, status: g.status, target_date: g.target_date ?? undefined, time_requirement_hrs: g.time_requirement_hrs ?? undefined, motivation: g.motivation ?? undefined });
    setEditing(g.id); setShowForm(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Goals</h1>
        <button onClick={() => { setForm(blank); setEditing(null); setShowForm(true); }} className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">
          + New Goal
        </button>
      </div>

      {error && <div className="text-red-500 bg-red-50 rounded p-3 text-sm">{error}</div>}

      {showForm && (
        <div className="bg-white border border-gray-200 rounded-xl p-5 space-y-4">
          <h2 className="font-semibold">{editing ? "Edit Goal" : "New Goal"}</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-xs text-gray-500 mb-1">Title *</label>
              <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Timeframe</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.timeframe} onChange={(e) => setForm({ ...form, timeframe: e.target.value as GoalTimeframe })}>
                {TIMEFRAMES.map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Priority</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value as Priority })}>
                {PRIORITIES.map((p) => <option key={p}>{p}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Status</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as GoalStatus })}>
                {STATUSES.map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Target Date</label>
              <input type="date" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.target_date ?? ""} onChange={(e) => setForm({ ...form, target_date: e.target.value || undefined })} />
            </div>
            <div className="col-span-2">
              <label className="block text-xs text-gray-500 mb-1">Description</label>
              <textarea className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" rows={2} value={form.description ?? ""} onChange={(e) => setForm({ ...form, description: e.target.value || undefined })} />
            </div>
            <div className="col-span-2">
              <label className="block text-xs text-gray-500 mb-1">Motivation</label>
              <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.motivation ?? ""} onChange={(e) => setForm({ ...form, motivation: e.target.value || undefined })} />
            </div>
          </div>
          <div className="flex gap-3">
            <button onClick={save} className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">{editing ? "Save" : "Create"}</button>
            <button onClick={() => { setShowForm(false); setEditing(null); }} className="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {goals.length === 0 && <p className="text-gray-400 text-sm">No goals yet.</p>}
        {goals.map((g) => (
          <div key={g.id} className="bg-white border border-gray-200 rounded-xl p-4 flex items-start justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-medium">{g.title}</span>
                <Badge value={g.priority} />
                <Badge value={g.status} />
                <Badge value={g.timeframe} />
              </div>
              {g.description && <p className="text-sm text-gray-500">{g.description}</p>}
              {g.target_date && <p className="text-xs text-gray-400">Target: {g.target_date}</p>}
            </div>
            <div className="flex gap-2 shrink-0">
              <button onClick={() => startEdit(g)} className="text-xs text-indigo-600 hover:underline">Edit</button>
              <button onClick={() => del(g.id)} className="text-xs text-red-500 hover:underline">Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
