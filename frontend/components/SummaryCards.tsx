import Link from "next/link";
import type { ReactNode } from "react";

import type { Dashboard } from "@/lib/api";

function Stat({ label, value, detail }: { label: string; value: string; detail?: ReactNode }) {
  return (
    <div className="stat">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {detail && <div className="stat-detail">{detail}</div>}
    </div>
  );
}

export default function SummaryCards({ dashboard }: { dashboard: Dashboard }) {
  const { totals, calorie_target, calories_remaining, weight_on_day } = dashboard;

  let remainingDetail: ReactNode =<Link href="/profile">Set a daily target</Link>;
  if (calories_remaining !== null) {
    remainingDetail = calories_remaining < 0 ? "over target" : "left today";
  }

  return (
    <>
      <div className="stats">
        <Stat
          label="Calories"
          value={totals.calories.toLocaleString()}
          detail={calorie_target ? `of ${calorie_target.toLocaleString()} target` : undefined}
        />
        <Stat
          label="Remaining"
          value={calories_remaining === null ? "–" : Math.abs(calories_remaining).toLocaleString()}
          detail={remainingDetail}
        />
        <Stat label="Protein" value={`${totals.protein_g} g`} />
        <Stat label="Carbs" value={`${totals.carbs_g} g`} />
        <Stat label="Fat" value={`${totals.fat_g} g`} />
        <Stat label="Weight" value={weight_on_day ? `${weight_on_day.weight_kg} kg` : "–"} />
      </div>
      {totals.entries_missing_macros > 0 && (
        <p className="muted">
          Macro totals leave out {totals.entries_missing_macros}{" "}
          {totals.entries_missing_macros === 1 ? "entry" : "entries"} without macro data, so the
          real totals may be higher.
        </p>
      )}
    </>
  );
}
