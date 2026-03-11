"use client";
import { useEffect, useState } from "react";
import { Plans, Tasks, Habits, Plan, PlanSummary, PlanItem, Task, Habit } from "@/lib/api";
import { Badge } from "@/components/Badge";

export default function PlansPage() {
  const [plans, setPlans] = useState<PlanSummary[]>([]);
  const [selected, setSelected] = useState<Plan | null>(null);
  const [genDate, setGenDate] = useState(new Date().toISOString().slice(0, 10));
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Backlog state
  const [showBacklog, setShowBacklog] = useState(false);
  const [backlogTasks, setBacklogTasks] = useState<Task[]>([]);
  const [backlogHabits, setBacklogHabits] = useState<Habit[]>([]);
  const [backlogTab, setBacklogTab] = useState<"tasks" | "habits">("tasks");
  const [addingId, setAddingId] = useState<string | null>(null);

  const loadList = () => Plans.list().then(setPlans).catch((e) => setError(e.message));
  useEffect(() => { loadList(); }, []);

  const openPlan = async (id: string) => {
    const p = await Plans.get(id).catch((e) => { setError(e.message); return null; });
    if (p) setSelected(p);
  };

  const refreshSelected = async () => {
    if (!selected) return;
    const p = await Plans.get(selected.id);
    setSelected(p);
  };

  const generate = async () => {
    setLoading(true);
    try {
      const p = await Plans.generate({ plan_date: genDate });
      setSelected(p);
      loadList();
    } catch (e: unknown) { setError(e instanceof Error ? e.message : String(e)); }
    finally { setLoading(false); }
  };

  const del = async (id: string) => {
    if (!confirm("Delete this plan?")) return;
    await Plans.delete(id).catch((e) => setError(e.message));
    if (selected?.id === id) setSelected(null);
    loadList();
  };

  const removeItem = async (item: PlanItem) => {
    if (!selected) return;
    await Plans.deleteItem(selected.id, item.id).catch((e) => setError(e.message));
    refreshSelected();
  };

  const openBacklog = async () => {
    setShowBacklog(true);
    const [tasks, habits] = await Promise.all([
      Tasks.list({ active_only: true }),
      Habits.list({ active_only: true }),
    ]);
    setBacklogTasks(tasks);
    setBacklogHabits(habits);
  };

  const addTaskToPlan = async (task: Task) => {
    if (!selected) return;
    setAddingId(task.id);
    try {
      // Create a task instance for the plan date then add it
      const instance = await Tasks.createInstance(task.id, { scheduled_date: selected.plan_date });
      await Plans.addItem(selected.id, { task_instance_id: instance.id });
      refreshSelected();
    } catch (e: unknown) { setError(e instanceof Error ? e.message : String(e)); }
    finally { setAddingId(null); }
  };

  const addHabitToPlan = async (habit: Habit) => {
    if (!selected) return;
    setAddingId(habit.id);
    try {
      await Plans.addItem(selected.id, { habit_id: habit.id });
      refreshSelected();
    } catch (e: unknown) { setError(e instanceof Error ? e.message : String(e)); }
    finally { setAddingId(null); }
  };

  // IDs already in the plan
  const planTaskInstanceIds = new Set(selected?.items.map((i) => i.task_instance?.task_id).filter(Boolean));
  const planHabitIds = new Set(selected?.items.map((i) => i.habit_id).filter(Boolean));

  const itemLabel = (item: PlanItem) => item.task_instance?.task.title ?? item.habit?.title ?? "Unknown";
  const itemType = (item: PlanItem) => item.task_instance ? "TASK" : "HABIT";

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Plans</h1>

      {error && (
        <div className="text-red-500 bg-red-50 rounded p-3 text-sm flex justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="ml-4 font-bold">✕</button>
        </div>
      )}

      {/* Generate bar */}
      <div className="bg-white border border-gray-200 rounded-xl p-4 flex items-end gap-4">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Plan Date</label>
          <input type="date" className="border border-gray-300 rounded-lg px-3 py-2 text-sm" value={genDate} onChange={(e) => setGenDate(e.target.value)} />
        </div>
        <button onClick={generate} disabled={loading} className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50">
          {loading ? "Generating…" : "Generate Plan"}
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Plan list */}
        <div className="space-y-2">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">All Plans</h2>
          {plans.length === 0 && <p className="text-gray-400 text-sm">No plans yet.</p>}
          {plans.map((p) => (
            <div key={p.id} onClick={() => openPlan(p.id)} className={`cursor-pointer border rounded-lg p-3 transition-colors ${selected?.id === p.id ? "border-indigo-500 bg-indigo-50" : "border-gray-200 bg-white hover:border-gray-300"}`}>
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium text-sm">{p.plan_date}</p>
                  <Badge value={p.status} />
                </div>
                <button onClick={(e) => { e.stopPropagation(); del(p.id); }} className="text-xs text-red-400 hover:text-red-600">✕</button>
              </div>
            </div>
          ))}
        </div>

        {/* Plan detail */}
        <div className="sm:col-span-2 space-y-4">
          {!selected && <p className="text-gray-400 text-sm">Select a plan to view details.</p>}

          {selected && (
            <>
              <div className="bg-white border border-gray-200 rounded-xl p-4 space-y-4">
                <div className="flex justify-between items-center flex-wrap gap-2">
                  <div>
                    <h2 className="font-semibold text-lg">{selected.plan_date}</h2>
                    <Badge value={selected.status} />
                  </div>
                  <div className="flex gap-2 flex-wrap">
                    <button onClick={() => Plans.update(selected.id, { status: "ACTIVE" }).then(refreshSelected)} className="text-xs text-indigo-600 border border-indigo-200 rounded px-2 py-1 hover:bg-indigo-50">Activate</button>
                    <button onClick={() => Plans.update(selected.id, { status: "COMPLETED" }).then(refreshSelected)} className="text-xs text-green-600 border border-green-200 rounded px-2 py-1 hover:bg-green-50">Complete</button>
                    <button onClick={openBacklog} className="text-xs bg-indigo-600 text-white rounded px-2 py-1 hover:bg-indigo-700">+ Add from Backlog</button>
                  </div>
                </div>

                {selected.notes && <p className="text-sm text-gray-500">{selected.notes}</p>}

                <div className="space-y-2">
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{selected.items.length} items</p>
                  {selected.items.length === 0 && <p className="text-sm text-gray-400">No items — add from backlog.</p>}
                  {selected.items.map((item) => (
                    <div key={item.id} className="flex items-center justify-between gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-xs text-gray-400 shrink-0">{itemType(item)}</span>
                        <span className="text-sm font-medium truncate">{itemLabel(item)}</span>
                        {item.task_instance && <Badge value={item.task_instance.task.priority} />}
                        {item.habit && <Badge value={item.habit.priority} />}
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <Badge value={item.status} />
                        <button onClick={() => removeItem(item)} className="text-xs text-red-400 hover:text-red-600 font-bold" title="Remove from plan">✕</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Backlog panel */}
              {showBacklog && (
                <div className="bg-white border border-gray-200 rounded-xl p-4 space-y-3">
                  <div className="flex justify-between items-center">
                    <h3 className="font-semibold">Backlog</h3>
                    <button onClick={() => setShowBacklog(false)} className="text-gray-400 hover:text-gray-600 font-bold">✕</button>
                  </div>

                  {/* Tabs */}
                  <div className="flex gap-1 border-b border-gray-200">
                    {(["tasks", "habits"] as const).map((tab) => (
                      <button key={tab} onClick={() => setBacklogTab(tab)} className={`px-3 py-1.5 text-sm font-medium capitalize border-b-2 -mb-px transition-colors ${backlogTab === tab ? "border-indigo-500 text-indigo-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}>
                        {tab}
                      </button>
                    ))}
                  </div>

                  {backlogTab === "tasks" && (
                    <div className="space-y-2 max-h-72 overflow-y-auto">
                      {backlogTasks.length === 0 && <p className="text-sm text-gray-400">No active tasks.</p>}
                      {backlogTasks.map((t) => {
                        const alreadyIn = planTaskInstanceIds.has(t.id);
                        return (
                          <div key={t.id} className="flex items-center justify-between gap-3 p-2 rounded-lg hover:bg-gray-50">
                            <div className="flex items-center gap-2 min-w-0">
                              <span className="text-sm truncate">{t.title}</span>
                              <Badge value={t.priority} />
                              <Badge value={t.frequency} />
                            </div>
                            <button
                              onClick={() => addTaskToPlan(t)}
                              disabled={alreadyIn || addingId === t.id}
                              className="text-xs shrink-0 px-2 py-1 rounded border disabled:opacity-40 disabled:cursor-not-allowed border-indigo-200 text-indigo-600 hover:bg-indigo-50"
                            >
                              {addingId === t.id ? "Adding…" : alreadyIn ? "In plan" : "+ Add"}
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {backlogTab === "habits" && (
                    <div className="space-y-2 max-h-72 overflow-y-auto">
                      {backlogHabits.length === 0 && <p className="text-sm text-gray-400">No active habits.</p>}
                      {backlogHabits.map((h) => {
                        const alreadyIn = planHabitIds.has(h.id);
                        return (
                          <div key={h.id} className="flex items-center justify-between gap-3 p-2 rounded-lg hover:bg-gray-50">
                            <div className="flex items-center gap-2 min-w-0">
                              <span className="text-sm truncate">{h.title}</span>
                              <Badge value={h.priority} />
                              <Badge value={h.frequency} />
                              <span className="text-xs text-gray-400">🔥 {h.streak_count}</span>
                            </div>
                            <button
                              onClick={() => addHabitToPlan(h)}
                              disabled={alreadyIn || addingId === h.id}
                              className="text-xs shrink-0 px-2 py-1 rounded border disabled:opacity-40 disabled:cursor-not-allowed border-indigo-200 text-indigo-600 hover:bg-indigo-50"
                            >
                              {addingId === h.id ? "Adding…" : alreadyIn ? "In plan" : "+ Add"}
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
