// The dashboard, served at "/". In Next.js the folder structure under app/ is
// the routing (app/profile/page.tsx -> /profile), instead of config/routes.rb.
"use client"; // Runs in the browser, because it keeps state and handles clicks.

import { useEffect, useState } from "react";

import DayPicker from "@/components/DayPicker";
import FoodEntryForm from "@/components/FoodEntryForm";
import MealSection from "@/components/MealSection";
import SummaryCards from "@/components/SummaryCards";
import WeightForm from "@/components/WeightForm";
import WeightHistory from "@/components/WeightHistory";
import { api, MEAL_TYPES, messageFrom, type Dashboard } from "@/lib/api";
import { todayISO } from "@/lib/dates";

export default function DashboardPage() {
  // Starts as null and is set in the browser, because "today" depends on the
  // user's time zone, which the server doesn't know.
  const [day, setDay] = useState<string | null>(null);
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Bumping this number re-runs the fetch below, e.g. after saving a form.
  const [reloadKey, setReloadKey] = useState(0);
  const reload = () => setReloadKey((k) => k + 1);

  useEffect(() => {
    setDay(todayISO());
  }, []);

  useEffect(() => {
    if (!day) return;
    // If the day changes before this request finishes, ignore its result so
    // a slow response can't overwrite a newer one.
    let ignore = false;
    api
      .getDashboard(day)
      .then((data) => {
        if (!ignore) {
          setDashboard(data);
          setError(null);
        }
      })
      .catch((e) => {
        if (!ignore) setError(messageFrom(e));
      });
    return () => {
      ignore = true;
    };
  }, [day, reloadKey]);

  async function deleteFoodEntry(id: number) {
    try {
      await api.deleteFoodEntry(id);
      reload();
    } catch (e) {
      setError(messageFrom(e));
    }
  }

  if (!day) return null;

  return (
    <>
      <DayPicker day={day} onChange={setDay} />
      {error && <p className="error">{error}</p>}

      {dashboard?.day === day && (
        <>
          <SummaryCards dashboard={dashboard} />

          <div className="columns">
            <section className="card">
              <h2>Food</h2>
              <FoodEntryForm day={day} onSaved={reload} />
              {MEAL_TYPES.map((meal) => (
                <MealSection
                  key={meal}
                  meal={meal}
                  entries={dashboard.meals[meal]}
                  onDelete={deleteFoodEntry}
                />
              ))}
            </section>

            <section className="card">
              <h2>Weight</h2>
              {/* The key resets the form's inputs when the day or saved entry changes. */}
              <WeightForm
                key={`${day}-${dashboard.weight_on_day?.id ?? "new"}`}
                day={day}
                current={dashboard.weight_on_day}
                onSaved={reload}
              />
              <h3>Recent</h3>
              <WeightHistory weights={dashboard.recent_weights} />
            </section>
          </div>
        </>
      )}
    </>
  );
}
