"use client";
import { useEffect, useState } from "react";
import { Tasks, Goals, Task, TaskCreate, TaskType, Frequency, Priority, Goal, TaskInstance } from "@/lib/api";
import { Badge } from "@/components/Badge";

const TYPES: TaskType[] = ["CHORE", "IMPROVEMENT"];
const FREQS: Frequency[] = ["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "HALF_YEARLY", "YEARLY", "ONE_TIME", "AD_HOC"];
const PRIORITIES: Priority[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

const blank: TaskCreate = { title: "", task_type: "CHORE", frequency: "DAILY", priority: "MEDIUM", is_active: true };

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [form, setForm] = useState<TaskCreate>(blank);
  const [editing, setEditing] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [instances, setInstances] = useState<Record<string, TaskInstance[]>>({});
  const [error, setError] = useState<string | null>(null);

  const load = () => Tasks.list().then(setTasks).catch((e) => setError(e.message));
  useEffect(() => { load(); Goals.list().then(setGoals); }, []);

  const save = async () => {
    try {
      if (editing) { await Tasks.update(editing, form); }
      else { await Tasks.create(form); }
      setForm(blank); setEditing(null); setShowForm(false); load();
    } catch (e: unknown) { setError(e instanceof Error ? e.message : String(e)); }
  };

  const del = async (id: string) => {
    if (!confirm("Delete this task?")) return;
    await Tasks.delete(id).then(load).catch((e) => setError(e.message));
  };

  const startEdit = (t: Task) => {
    setForm({ title: t.title, description: t.description ?? undefined, task_type: t.task_type, frequency: t.frequency, priority: t.priority, is_active: t.is_active, goal_id: t.goal_id ?? undefined });
    setEditing(t.id); setShowForm(true);
  };

  const toggleExpand = async (id: string) => {
    if (expanded === id) { setExpanded(null); return; }
    setExpanded(id);
    if (!instances[id]) {
      const list = await Tasks.instances(id).catch(() => []);
      setInstances((prev) => ({ ...prev, [id]: list }));
    }
  };

  const addInstance = async (taskId: string) => {
    const date = prompt("Scheduled date (YYYY-MM-DD):", new Date().toISOString().slice(0, 10));
    if (!date) return;
    await Tasks.createInstance(taskId, { scheduled_date: date });
    const list = await Tasks.instances(taskId);
    setInstances((prev) => ({ ...prev, [taskId]: list }));
  };

  const updateInstanceStatus = async (taskId: string, instanceId: string, status: string) => {
    await Tasks.updateInstance(taskId, instanceId, { status });
    const list = await Tasks.instances(taskId);
    setInstances((prev) => ({ ...prev, [taskId]: list }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Tasks</h1>
        <button onClick={() => { setForm(blank); setEditing(null); setShowForm(true); }} className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">
          + New Task
        </button>
      </div>

      {error && <div className="text-red-500 bg-red-50 rounded p-3 text-sm">{error}</div>}

      {showForm && (
        <div className="bg-white border border-gray-200 rounded-xl p-5 space-y-4">
          <h2 className="font-semibold">{editing ? "Edit Task" : "New Task"}</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-xs text-gray-500 mb-1">Title *</label>
              <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Type</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.task_type} onChange={(e) => setForm({ ...form, task_type: e.target.value as TaskType })}>
                {TYPES.map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Frequency</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value as Frequency })}>
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
        {tasks.length === 0 && <p className="text-gray-400 text-sm">No tasks yet.</p>}
        {tasks.map((t) => (
          <div key={t.id} className="bg-white border border-gray-200 rounded-xl">
            <div className="p-4 flex items-start justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-medium">{t.title}</span>
                  <Badge value={t.priority} />
                  <Badge value={t.task_type} />
                  <Badge value={t.frequency} />
                  {!t.is_active && <Badge value="INACTIVE" />}
                </div>
                {t.description && <p className="text-sm text-gray-500">{t.description}</p>}
              </div>
              <div className="flex gap-2 shrink-0">
                <button onClick={() => toggleExpand(t.id)} className="text-xs text-gray-500 hover:underline">{expanded === t.id ? "Hide" : "Instances"}</button>
                <button onClick={() => startEdit(t)} className="text-xs text-indigo-600 hover:underline">Edit</button>
                <button onClick={() => del(t.id)} className="text-xs text-red-500 hover:underline">Delete</button>
              </div>
            </div>

            {expanded === t.id && (
              <div className="border-t border-gray-100 px-4 py-3 space-y-2">
                <div className="flex justify-between items-center">
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Instances</p>
                  <button onClick={() => addInstance(t.id)} className="text-xs text-indigo-600 hover:underline">+ Add Instance</button>
                </div>
                {(instances[t.id] ?? []).length === 0 && <p className="text-xs text-gray-400">No instances.</p>}
                {(instances[t.id] ?? []).map((inst) => (
                  <div key={inst.id} className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">{inst.scheduled_date}</span>
                    <div className="flex items-center gap-2">
                      <Badge value={inst.status} />
                      <select className="text-xs border border-gray-200 rounded px-1 py-0.5" value={inst.status} onChange={(e) => updateInstanceStatus(t.id, inst.id, e.target.value)}>
                        {["PENDING", "IN_PROGRESS", "COMPLETED", "SKIPPED"].map((s) => <option key={s}>{s}</option>)}
                      </select>
                    </div>
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
