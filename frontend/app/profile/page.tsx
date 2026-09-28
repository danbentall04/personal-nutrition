"use client";

import { useEffect, useState, type FormEvent } from "react";

import { api, messageFrom, type Goal, type Profile, type ProfileInput, type Sex } from "@/lib/api";
import { optionalNumber, optionalText, toInputValue } from "@/lib/forms";

// Inputs hold strings; these convert between the form and the API shape.
interface FormState {
  name: string;
  email: string;
  date_of_birth: string;
  sex: Sex | "";
  height_cm: string;
  goal: Goal;
  target_weight_kg: string;
  daily_calorie_target: string;
  dietary_notes: string;
}

function toForm(p: Profile): FormState {
  return {
    name: p.name,
    email: p.email ?? "",
    date_of_birth: p.date_of_birth ?? "",
    sex: p.sex ?? "",
    height_cm: toInputValue(p.height_cm),
    goal: p.goal,
    target_weight_kg: toInputValue(p.target_weight_kg),
    daily_calorie_target: toInputValue(p.daily_calorie_target),
    dietary_notes: p.dietary_notes ?? "",
  };
}

function fromForm(f: FormState): ProfileInput {
  return {
    name: f.name.trim(),
    email: optionalText(f.email),
    date_of_birth: f.date_of_birth || null,
    sex: f.sex || null,
    height_cm: optionalNumber(f.height_cm),
    goal: f.goal,
    target_weight_kg: optionalNumber(f.target_weight_kg),
    daily_calorie_target: optionalNumber(f.daily_calorie_target),
    dietary_notes: optionalText(f.dietary_notes),
  };
}

export default function ProfilePage() {
  const [form, setForm] = useState<FormState | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getProfile()
      .then((profile) => setForm(toForm(profile)))
      .catch((e) => setError(messageFrom(e)));
  }, []);

  if (!form) {
    return error ? <p className="error">{error}</p> : <p className="muted">Loading…</p>;
  }

  function update<K extends keyof FormState>(field: K, value: FormState[K]) {
    setForm((prev) => (prev ? { ...prev, [field]: value } : prev));
    setMessage(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!form) return;
    setSaving(true);
    setError(null);
    try {
      const saved = await api.updateProfile(fromForm(form));
      setForm(toForm(saved));
      setMessage("Profile saved.");
    } catch (e) {
      setError(messageFrom(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="card narrow">
      <h1>Profile</h1>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Name
          <input required value={form.name} onChange={(e) => update("name", e.target.value)} />
        </label>
        <label>
          Email
          <input type="email" value={form.email} onChange={(e) => update("email", e.target.value)} />
        </label>
        <div className="row">
          <label>
            Date of birth
            <input
              type="date"
              value={form.date_of_birth}
              onChange={(e) => update("date_of_birth", e.target.value)}
            />
          </label>
          <label>
            Sex (for BMR estimates)
            <select value={form.sex} onChange={(e) => update("sex", e.target.value as Sex | "")}>
              <option value="">Not set</option>
              <option value="female">Female</option>
              <option value="male">Male</option>
            </select>
          </label>
          <label>
            Height (cm)
            <input
              type="number"
              min={1}
              step={0.1}
              value={form.height_cm}
              onChange={(e) => update("height_cm", e.target.value)}
            />
          </label>
        </div>
        <div className="row">
          <label>
            Goal
            <select value={form.goal} onChange={(e) => update("goal", e.target.value as Goal)}>
              <option value="lose">Lose weight</option>
              <option value="maintain">Maintain</option>
              <option value="gain">Gain weight</option>
            </select>
          </label>
          <label>
            Target weight (kg)
            <input
              type="number"
              min={1}
              step={0.1}
              value={form.target_weight_kg}
              onChange={(e) => update("target_weight_kg", e.target.value)}
            />
          </label>
          <label>
            Daily calorie target
            <input
              type="number"
              min={1}
              step={1}
              value={form.daily_calorie_target}
              onChange={(e) => update("daily_calorie_target", e.target.value)}
            />
          </label>
        </div>
        <label>
          Dietary preferences and constraints
          <textarea
            rows={3}
            value={form.dietary_notes}
            onChange={(e) => update("dietary_notes", e.target.value)}
          />
        </label>
        {error && <p className="error">{error}</p>}
        {message && <p className="success">{message}</p>}
        <button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save profile"}
        </button>
      </form>
    </section>
  );
}
