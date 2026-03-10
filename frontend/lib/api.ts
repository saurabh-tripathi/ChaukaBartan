const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Goals ──────────────────────────────────────────────────────────────────
export const Goals = {
  list: () => request<Goal[]>("/api/v1/goals"),
  get: (id: string) => request<Goal>(`/api/v1/goals/${id}`),
  create: (body: GoalCreate) => request<Goal>("/api/v1/goals", { method: "POST", body: JSON.stringify(body) }),
  update: (id: string, body: Partial<GoalCreate>) => request<Goal>(`/api/v1/goals/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  delete: (id: string) => request<void>(`/api/v1/goals/${id}`, { method: "DELETE" }),
  progress: (id: string) => request<GoalProgress>(`/api/v1/dashboard/goals/${id}`),
};

// ── Tasks ──────────────────────────────────────────────────────────────────
export const Tasks = {
  list: (params?: { active_only?: boolean; goal_id?: string }) => {
    const q = new URLSearchParams();
    if (params?.active_only !== undefined) q.set("active_only", String(params.active_only));
    if (params?.goal_id) q.set("goal_id", params.goal_id);
    return request<Task[]>(`/api/v1/tasks${q.toString() ? "?" + q : ""}`);
  },
  get: (id: string) => request<Task>(`/api/v1/tasks/${id}`),
  create: (body: TaskCreate) => request<Task>("/api/v1/tasks", { method: "POST", body: JSON.stringify(body) }),
  update: (id: string, body: Partial<TaskCreate>) => request<Task>(`/api/v1/tasks/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  delete: (id: string) => request<void>(`/api/v1/tasks/${id}`, { method: "DELETE" }),
  instances: (id: string) => request<TaskInstance[]>(`/api/v1/tasks/${id}/instances`),
  createInstance: (taskId: string, body: { scheduled_date: string; status?: string }) =>
    request<TaskInstance>(`/api/v1/tasks/${taskId}/instances`, { method: "POST", body: JSON.stringify(body) }),
  updateInstance: (taskId: string, instanceId: string, body: { status: string }) =>
    request<TaskInstance>(`/api/v1/tasks/${taskId}/instances/${instanceId}`, { method: "PATCH", body: JSON.stringify(body) }),
  getFeedback: (taskId: string, instanceId: string) =>
    request<TaskFeedback>(`/api/v1/tasks/${taskId}/instances/${instanceId}/feedback`),
  createFeedback: (taskId: string, instanceId: string, body: FeedbackCreate) =>
    request<TaskFeedback>(`/api/v1/tasks/${taskId}/instances/${instanceId}/feedback`, { method: "POST", body: JSON.stringify(body) }),
};

// ── Habits ─────────────────────────────────────────────────────────────────
export const Habits = {
  list: (params?: { active_only?: boolean; goal_id?: string }) => {
    const q = new URLSearchParams();
    if (params?.active_only !== undefined) q.set("active_only", String(params.active_only));
    if (params?.goal_id) q.set("goal_id", params.goal_id);
    return request<Habit[]>(`/api/v1/habits${q.toString() ? "?" + q : ""}`);
  },
  get: (id: string) => request<Habit>(`/api/v1/habits/${id}`),
  create: (body: HabitCreate) => request<Habit>("/api/v1/habits", { method: "POST", body: JSON.stringify(body) }),
  update: (id: string, body: Partial<HabitCreate>) => request<Habit>(`/api/v1/habits/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  delete: (id: string) => request<void>(`/api/v1/habits/${id}`, { method: "DELETE" }),
  log: (id: string, body: { logged_date: string; notes?: string }) =>
    request<HabitLog>(`/api/v1/habits/${id}/logs`, { method: "POST", body: JSON.stringify(body) }),
  logs: (id: string) => request<HabitLog[]>(`/api/v1/habits/${id}/logs`),
};

// ── Plans ──────────────────────────────────────────────────────────────────
export const Plans = {
  list: () => request<PlanSummary[]>("/api/v1/plans"),
  get: (id: string) => request<Plan>(`/api/v1/plans/${id}`),
  byDate: (date: string) => request<Plan>(`/api/v1/plans/by-date/${date}`),
  generate: (body: { plan_date?: string; notes?: string }) =>
    request<Plan>("/api/v1/plans/generate", { method: "POST", body: JSON.stringify(body) }),
  update: (id: string, body: { status?: string; notes?: string }) =>
    request<Plan>(`/api/v1/plans/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  delete: (id: string) => request<void>(`/api/v1/plans/${id}`, { method: "DELETE" }),
  updateItem: (planId: string, itemId: string, body: { status?: string; display_order?: number }) =>
    request<PlanItem>(`/api/v1/plans/${planId}/items/${itemId}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteItem: (planId: string, itemId: string) =>
    request<void>(`/api/v1/plans/${planId}/items/${itemId}`, { method: "DELETE" }),
  addItem: (planId: string, body: { task_instance_id?: string; habit_id?: string }) =>
    request<PlanItem>(`/api/v1/plans/${planId}/items`, { method: "POST", body: JSON.stringify(body) }),
};

// ── Dashboard ──────────────────────────────────────────────────────────────
export const Dashboard = {
  daily: (date?: string) => {
    const q = date ? `?date=${date}` : "";
    return request<DailyDashboard>(`/api/v1/dashboard/daily${q}`);
  },
};

// ── Types ──────────────────────────────────────────────────────────────────
export type Priority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type GoalStatus = "ACTIVE" | "COMPLETED" | "PAUSED" | "ABANDONED";
export type GoalTimeframe = "THREE_MONTHS" | "SIX_MONTHS" | "ONE_YEAR" | "FIVE_YEARS";
export type TaskType = "CHORE" | "IMPROVEMENT";
export type Frequency = "DAILY" | "WEEKLY" | "MONTHLY" | "QUARTERLY" | "HALF_YEARLY" | "YEARLY" | "ONE_TIME" | "AD_HOC";
export type InstanceStatus = "PENDING" | "IN_PROGRESS" | "COMPLETED" | "SKIPPED";
export type HabitFrequency = "DAILY" | "WEEKLY";
export type HabitStatus = "ACTIVE" | "SET" | "LAPSED" | "ABANDONED";
export type PlanStatus = "DRAFT" | "ACTIVE" | "COMPLETED" | "ARCHIVED";
export type ItemStatus = "PENDING" | "COMPLETED" | "SKIPPED";

export interface Goal {
  id: string; title: string; description: string | null;
  timeframe: GoalTimeframe; priority: Priority; status: GoalStatus;
  target_date: string | null; time_requirement_hrs: number | null;
  motivation: string | null; parent_goal_id: string | null;
  created_at: string; updated_at: string;
}
export interface GoalCreate {
  title: string; description?: string; timeframe: GoalTimeframe;
  priority?: Priority; status?: GoalStatus; target_date?: string;
  time_requirement_hrs?: number; motivation?: string;
}
export interface GoalProgress {
  goal: Goal;
  tasks: { total_tasks: number; active_tasks: number; completed_instances_last_30d: number };
  habits: { total_habits: number; active_habits: number; avg_streak: number; logs_last_30d: number };
}

export interface Task {
  id: string; title: string; description: string | null;
  task_type: TaskType; frequency: Frequency; priority: Priority;
  is_active: boolean; goal_id: string | null;
  end_date: string | null; importance_note: string | null;
  created_at: string; updated_at: string;
}
export interface TaskCreate {
  title: string; description?: string; task_type: TaskType;
  frequency: Frequency; priority?: Priority; goal_id?: string;
  is_active?: boolean; end_date?: string;
}
export interface TaskInstance {
  id: string; task_id: string; scheduled_date: string;
  status: InstanceStatus; created_at: string; updated_at: string;
}
export interface TaskFeedback {
  id: string; task_instance_id: string;
  completed_at: string | null; duration_minutes: number | null;
  difficulty_rating: number | null; satisfaction_rating: number | null;
  notes: string | null; created_at: string; updated_at: string;
}
export interface FeedbackCreate {
  duration_minutes?: number; difficulty_rating?: number;
  satisfaction_rating?: number; notes?: string;
}

export interface Habit {
  id: string; title: string; description: string | null;
  frequency: HabitFrequency; priority: Priority; status: HabitStatus;
  streak_count: number; goal_id: string | null;
  importance_note: string | null; created_at: string; updated_at: string;
}
export interface HabitCreate {
  title: string; description?: string; frequency: HabitFrequency;
  priority?: Priority; goal_id?: string; status?: HabitStatus;
}
export interface HabitLog {
  id: string; habit_id: string; logged_date: string;
  logged_at: string; notes: string | null; created_at: string; updated_at: string;
}

export interface PlanSummary {
  id: string; plan_date: string; status: PlanStatus;
  notes: string | null; created_at: string; updated_at: string;
}
export interface PlanItem {
  id: string; plan_id: string; task_instance_id: string | null;
  habit_id: string | null; scheduled_time: string | null;
  display_order: number; status: ItemStatus;
  task_instance: { id: string; task_id: string; scheduled_date: string; status: string; task: { id: string; title: string; priority: Priority; task_type: TaskType } } | null;
  habit: { id: string; title: string; priority: Priority; frequency: HabitFrequency; streak_count: number } | null;
  created_at: string; updated_at: string;
}
export interface Plan extends PlanSummary { items: PlanItem[] }

export interface DailyDashboard {
  date: string;
  plan: { total_items: number; completed: number; skipped: number; pending: number; completion_rate: number } | null;
  tasks: { total_instances: number; completed: number; skipped: number; pending: number; in_progress: number; completion_rate: number; avg_difficulty: number | null; avg_satisfaction: number | null; total_duration_minutes: number };
  habits: { logged: number };
}
