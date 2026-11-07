// Typed client for the FastAPI backend.
// These types mirror the Pydantic schemas in backend/app/schemas.py; keep them in sync.
// Dates are "YYYY-MM-DD" strings.

export type Goal = "lose" | "maintain" | "gain";
export type Sex = "female" | "male";
export type MealType = "breakfast" | "lunch" | "dinner" | "snack";

export const MEAL_TYPES: MealType[] = ["breakfast", "lunch", "dinner", "snack"];

export interface Profile {
  id: number;
  name: string;
  email: string | null;
  date_of_birth: string | null;
  sex: Sex | null;
  height_cm: number | null;
  goal: Goal;
  target_weight_kg: number | null;
  daily_calorie_target: number | null;
  dietary_notes: string | null;
}
export type ProfileInput = Omit<Profile, "id">;

export interface WeightEntry {
  id: number;
  measured_on: string;
  weight_kg: number;
  note: string | null;
}
export type WeightInput = Pick<WeightEntry, "weight_kg" | "note">;

export interface FoodEntry {
  id: number;
  eaten_on: string;
  meal: MealType;
  name: string;
  quantity: string | null;
  calories: number;
  protein_g: number | null;
  carbs_g: number | null;
  fat_g: number | null;
}
export type FoodEntryInput = Omit<FoodEntry, "id">;

export interface DayTotals {
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  entries_missing_macros: number;
}

export interface Dashboard {
  day: string;
  calorie_target: number | null;
  calories_remaining: number | null;
  totals: DayTotals;
  meals: Record<MealType, FoodEntry[]>;
  weight_on_day: WeightEntry | null;
  recent_weights: WeightEntry[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) {
    throw new Error(await errorMessage(response));
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

// FastAPI errors look like {"detail": "..."}, or for validation errors
// {"detail": [{"loc": ["body", "calories"], "msg": "..."}]}.
async function errorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail
        .map((e: { loc: (string | number)[]; msg: string }) => `${e.loc.at(-1)}: ${e.msg}`)
        .join("; ");
    }
  } catch {
    // Response body wasn't JSON; fall through to the generic message.
  }
  return `Request failed (${response.status})`;
}

export function messageFrom(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

const json = (body: unknown) => JSON.stringify(body);

export const api = {
  getDashboard: (day: string) => request<Dashboard>(`/dashboard?day=${day}`),

  getProfile: () => request<Profile>("/profile"),
  updateProfile: (input: ProfileInput) =>
    request<Profile>("/profile", { method: "PUT", body: json(input) }),

  saveWeight: (day: string, input: WeightInput) =>
    request<WeightEntry>(`/weights/${day}`, { method: "PUT", body: json(input) }),
  deleteWeight: (day: string) => request<void>(`/weights/${day}`, { method: "DELETE" }),

  addFoodEntry: (input: FoodEntryInput) =>
    request<FoodEntry>("/food-entries", { method: "POST", body: json(input) }),
  deleteFoodEntry: (id: number) => request<void>(`/food-entries/${id}`, { method: "DELETE" }),
};
