"use client";

import { useState, type FormEvent } from "react";

import { api, messageFrom, type WeightEntry } from "@/lib/api";
import { optionalText, toInputValue } from "@/lib/forms";

interface Props {
  day: string;
  current: WeightEntry | null;
  onSaved: () => void;
}

export default function WeightForm({ day, current, onSaved }: Props) {
  const [weight, setWeight] = useState(toInputValue(current?.weight_kg ?? null));
  const [note, setNote] = useState(current?.note ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(action: () => Promise<unknown>) {
    setSaving(true);
    setError(null);
    try {
      await action();
      onSaved();
    } catch (e) {
      setError(messageFrom(e));
    } finally {
      setSaving(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    run(() => api.saveWeight(day, { weight_kg: Number(weight), note: optionalText(note) }));
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      <div className="row">
        <label>
          Weight (kg)
          <input
            required
            type="number"
            min={1}
            step={0.01}
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
          />
        </label>
        <label className="grow">
          Note
          <input
            placeholder="optional"
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
        </label>
      </div>
      {error && <p className="error">{error}</p>}
      <div className="row">
        <button type="submit" disabled={saving}>
          {current ? "Update weight" : "Log weight"}
        </button>
        {current && (
          <button
            type="button"
            className="link-button"
            disabled={saving}
            onClick={() => run(() => api.deleteWeight(day))}
          >
            Remove
          </button>
        )}
      </div>
    </form>
  );
}
