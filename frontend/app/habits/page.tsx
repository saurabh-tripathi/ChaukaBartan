"use client";
import { useEffect, useState } from "react";
import { Habits, Goals, Habit, HabitCreate, HabitFrequency, Priority, HabitStatus, Goal, HabitLog } from "@/lib/api";
import { Badge } from "@/components/Badge";

const FREQS: HabitFrequency[] = ["DAILY", "WEEKLY"];
const PRIORITIES: Priority[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
const STATUSES: HabitStatus[] = ["ACTIVE", "SET", "LAPSED", "ABANDONED"];

const blank: HabitCreate = { title: "", frequency: "DAILY", priority: "MEDIUM", status: "ACTIVE" as HabitStatus };

export default function HabitsPage() {
  const [habits, setHabits] = useState<Habit[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [form, setForm] = useState<HabitCreate>(blank);
  const [editing, setEditing] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [logs, setLogs] = useState<Record<string, HabitLog[]>>({});
  const [error, setError] = useState<string | null>(null);

  const load = () => Habits.list().then(setHabits).catch((e) => setError(e.message));
  useEffect(() => { load(); Goals.list().then(setGoals); }, []);

  const save = async () => {
    try {
      if (editing) { await Habits.update(editing, form); }
      else { await Habits.create(form); }
      setForm(blank); setEditing(null); setShowForm(false); load();
    } catch (e: unknown) { setError(e instanceof Error ? e.message : String(e)); }
  };

  const del = async (id: string) => {
    if (!confirm("Delete this habit?")) return;
    await Habits.delete(id).then(load).catch((e) => setError(e.message));
  };

  const startEdit = (h: Habit) => {
    setForm({ title: h.title, description: h.description ?? undefined, frequency: h.frequency, priority: h.priority, status: h.status, goal_id: h.goal_id ?? undefined });
    setEditing(h.id); setShowForm(true);
  };

  const toggleExpand = async (id: string) => {
    if (expanded === id) { setExpanded(null); return; }
    setExpanded(id);
    if (!logs[id]) {
      const list = await Habits.logs(id).catch(() => []);
      setLogs((prev) => ({ ...prev, [id]: list }));
    }
  };

  const logHabit = async (id: string) => {
    const date = new Date().toISOString().slice(0, 10);
    const notes = prompt("Notes (optional):", "") ?? undefined;
    await Habits.log(id, { logged_date: date, notes: notes || undefined });
    const list = await Habits.logs(id);
    setLogs((prev) => ({ ...prev, [id]: list }));
    load(); // refresh streak
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Habits</h1>
        <button onClick={() => { setForm(blank); setEditing(null); setShowForm(true); }} className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">
          + New Habit
        </button>
      </div>

      {error && <div className="text-red-500 bg-red-50 rounded p-3 text-sm">{error}</div>}

      {showForm && (
        <div className="bg-white border border-gray-200 rounded-xl p-5 space-y-4">
          <h2 className="font-semibold">{editing ? "Edit Habit" : "New Habit"}</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-xs text-gray-500 mb-1">Title *</label>
              <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Frequency</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value as HabitFrequency })}>
                {FREQS.map((f) => <option key={f}>{f}</option>)}
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
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as HabitStatus })}>
                {STATUSES.map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Goal (optional)</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.goal_id ?? ""} onChange={(e) => setForm({ ...form, goal_id: e.target.value || undefined })}>
                <option value="">— None —</option>
                {goals.map((g) => <option key={g.id} value={g.id}>{g.title}</option>)}
              </select>
            </div>
            <div className="col-span-2">
              <label className="block text-xs text-gray-500 mb-1">Description</label>
              <textarea className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" rows={2} value={form.description ?? ""} onChange={(e) => setForm({ ...form, description: e.target.value || undefined })} />
            </div>
          </div>
          <div className="flex gap-3">
            <button onClick={save} className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">{editing ? "Save" : "Create"}</button>
            <button onClick={() => { setShowForm(false); setEditing(null); }} className="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {habits.length === 0 && <p className="text-gray-400 text-sm">No habits yet.</p>}
        {habits.map((h) => (
          <div key={h.id} className="bg-white border border-gray-200 rounded-xl">
            <div className="p-4 flex items-start justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-medium">{h.title}</span>
                  <Badge value={h.priority} />
                  <Badge value={h.status} />
                  <Badge value={h.frequency} />
                  <span className="text-xs text-gray-500">🔥 {h.streak_count} streak</span>
                </div>
                {h.description && <p className="text-sm text-gray-500">{h.description}</p>}
              </div>
              <div className="flex gap-2 shrink-0">
                <button onClick={() => logHabit(h.id)} className="text-xs bg-green-50 text-green-700 border border-green-200 rounded px-2 py-1 hover:bg-green-100">Log Today</button>
                <button onClick={() => toggleExpand(h.id)} className="text-xs text-gray-500 hover:underline">{expanded === h.id ? "Hide" : "Logs"}</button>
                <button onClick={() => startEdit(h)} className="text-xs text-indigo-600 hover:underline">Edit</button>
                <button onClick={() => del(h.id)} className="text-xs text-red-500 hover:underline">Delete</button>
              </div>
            </div>

            {expanded === h.id && (
              <div className="border-t border-gray-100 px-4 py-3 space-y-2">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Recent Logs</p>
                {(logs[h.id] ?? []).length === 0 && <p className="text-xs text-gray-400">No logs yet.</p>}
                {(logs[h.id] ?? []).slice(0, 10).map((l) => (
                  <div key={l.id} className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">{l.logged_date}</span>
                    {l.notes && <span className="text-gray-400 text-xs">{l.notes}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
