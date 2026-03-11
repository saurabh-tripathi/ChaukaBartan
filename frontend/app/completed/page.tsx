"use client";
import { useEffect, useState, useCallback } from "react";
import { Tasks, Goals, FlatInstance, Goal } from "@/lib/api";

function sub30Days(): string {
  const d = new Date();
  d.setDate(d.getDate() - 30);
  return d.toISOString().slice(0, 10);
}

export default function CompletedPage() {
  const [instances, setInstances] = useState<FlatInstance[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [fromDate, setFromDate] = useState(sub30Days());
  const [toDate, setToDate] = useState(new Date().toISOString().slice(0, 10));
  const [goalId, setGoalId] = useState("");
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { Goals.list().then(setGoals).catch(() => {}); }, []);

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 400);
    return () => clearTimeout(t);
  }, [search]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await Tasks.allInstances({
        status: "COMPLETED",
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
        goal_id: goalId || undefined,
        search: debouncedSearch || undefined,
      });
      setInstances(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, [fromDate, toDate, goalId, debouncedSearch]);

  useEffect(() => { load(); }, [load]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Completed Tasks</h1>

      {/* Filters */}
      <div className="bg-white border border-gray-200 rounded-xl p-4 flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-xs text-gray-500 mb-1">From</label>
          <input type="date" className="border border-gray-300 rounded-lg px-3 py-2 text-sm" value={fromDate} onChange={(e) => setFromDate(e.target.value)} />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">To</label>
          <input type="date" className="border border-gray-300 rounded-lg px-3 py-2 text-sm" value={toDate} onChange={(e) => setToDate(e.target.value)} />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Goal</label>
          <select className="border border-gray-300 rounded-lg px-3 py-2 text-sm" value={goalId} onChange={(e) => setGoalId(e.target.value)}>
            <option value="">— All Goals —</option>
            {goals.map((g) => <option key={g.id} value={g.id}>{g.title}</option>)}
          </select>
        </div>
        <div className="flex-1 min-w-40">
          <label className="block text-xs text-gray-500 mb-1">Task name search</label>
          <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Search..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </div>

      {error && <div className="text-red-500 bg-red-50 rounded p-3 text-sm">{error}</div>}

      {loading && <p className="text-gray-400 text-sm">Loading...</p>}

      {!loading && instances.length === 0 && (
        <p className="text-gray-400 text-sm">No completed tasks found for this filter.</p>
      )}

      {!loading && instances.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-xs text-gray-400 uppercase tracking-wide">
                <th className="text-left px-4 py-3">Task</th>
                <th className="text-left px-4 py-3">Goal</th>
                <th className="text-left px-4 py-3">Date</th>
                <th className="text-right px-4 py-3">Expected</th>
                <th className="text-right px-4 py-3">Actual</th>
                <th className="text-right px-4 py-3">Difficulty</th>
                <th className="text-right px-4 py-3">Satisfaction</th>
                <th className="text-left px-4 py-3">Notes</th>
              </tr>
            </thead>
            <tbody>
              {instances.map((inst) => (
                <tr key={inst.task_instance_id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="font-medium">{inst.task.title}</div>
                    {inst.task.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {inst.task.tags.map((tag) => (
                          <span key={tag} className="text-xs bg-gray-100 text-gray-500 rounded px-1.5 py-0.5">{tag}</span>
                        ))}
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3 text-gray-500">{inst.task.goal_title ?? "—"}</td>
                  <td className="px-4 py-3 text-gray-500 whitespace-nowrap">{inst.scheduled_date}</td>
                  <td className="px-4 py-3 text-right text-gray-500">
                    {inst.task.expected_duration_minutes != null ? `${inst.task.expected_duration_minutes}m` : "—"}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-700">
                    {inst.feedback?.duration_minutes != null ? `${inst.feedback.duration_minutes}m` : "—"}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {inst.feedback?.difficulty_rating != null ? (
                      <span className="text-orange-600">{inst.feedback.difficulty_rating}/5</span>
                    ) : "—"}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {inst.feedback?.satisfaction_rating != null ? (
                      <span className="text-green-600">{inst.feedback.satisfaction_rating}/5</span>
                    ) : "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-500 max-w-xs truncate">{inst.feedback?.notes ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
