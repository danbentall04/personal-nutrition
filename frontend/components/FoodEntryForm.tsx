"use client";

import { useState, type FormEvent } from "react";

import { api, MEAL_TYPES, messageFrom, type MealType } from "@/lib/api";
import { optionalNumber, optionalText } from "@/lib/forms";

interface FormState {
  meal: MealType;
  name: string;
  quantity: string;
  calories: string;
  protein_g: string;
  carbs_g: string;
  fat_g: string;
}

const EMPTY: FormState = {
  meal: "breakfast",
  name: "",
  quantity: "",
  calories: "",
  protein_g: "",
  carbs_g: "",
  fat_g: "",
};

interface Props {
  day: string;
  onSaved: () => void;
}

export default function FoodEntryForm({ day, onSaved }: Props) {
  const [form, setForm] = useState<FormState>(EMPTY);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function update<K extends keyof FormState>(field: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await api.addFoodEntry({
        eaten_on: day,
        meal: form.meal,
        name: form.name.trim(),
        quantity: optionalText(form.quantity),
        calories: Number(form.calories),
        protein_g: optionalNumber(form.protein_g),
        carbs_g: optionalNumber(form.carbs_g),
        fat_g: optionalNumber(form.fat_g),
      });
      // Keep the meal selected so several items can be added in a row.
      setForm({ ...EMPTY, meal: form.meal });
      onSaved();
    } catch (e) {
      setError(messageFrom(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      <div className="row">
        <label>
          Meal
          <select value={form.meal} onChange={(e) => update("meal", e.target.value as MealType)}>
            {MEAL_TYPES.map((meal) => (
              <option key={meal} value={meal}>
                {meal[0].toUpperCase() + meal.slice(1)}
              </option>
            ))}
          </select>
        </label>
        <label className="grow">
          Food
          <input required value={form.name} onChange={(e) => update("name", e.target.value)} />
        </label>
        <label>
          Quantity
          <input
            placeholder="e.g. 150 g"
            value={form.quantity}
            onChange={(e) => update("quantity", e.target.value)}
          />
        </label>
      </div>
      <div className="row">
        <label>
          Calories
          <input
            required
            type="number"
            min={0}
            step={1}
            value={form.calories}
            onChange={(e) => update("calories", e.target.value)}
          />
        </label>
        <label>
          Protein (g)
          <input
            type="number"
            min={0}
            step={0.1}
            value={form.protein_g}
            onChange={(e) => update("protein_g", e.target.value)}
          />
        </label>
        <label>
          Carbs (g)
          <input
            type="number"
            min={0}
            step={0.1}
            value={form.carbs_g}
            onChange={(e) => update("carbs_g", e.target.value)}
          />
        </label>
        <label>
          Fat (g)
          <input
            type="number"
            min={0}
            step={0.1}
            value={form.fat_g}
            onChange={(e) => update("fat_g", e.target.value)}
          />
        </label>
      </div>
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={saving}>
        {saving ? "Adding…" : "Add food"}
      </button>
    </form>
  );
}
