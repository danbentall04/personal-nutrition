import { addDays, formatDay, todayISO } from "@/lib/dates";

interface Props {
  day: string;
  onChange: (day: string) => void;
}

export default function DayPicker({ day, onChange }: Props) {
  return (
    <div className="day-picker">
      <h1>{formatDay(day)}</h1>
      <div className="row">
        <button type="button" onClick={() => onChange(addDays(day, -1))} aria-label="Previous day">
          ←
        </button>
        <input
          type="date"
          value={day}
          onChange={(e) => e.target.value && onChange(e.target.value)}
          aria-label="Choose day"
        />
        <button type="button" onClick={() => onChange(addDays(day, 1))} aria-label="Next day">
          →
        </button>
        {day !== todayISO() && (
          <button type="button" onClick={() => onChange(todayISO())}>
            Today
          </button>
        )}
      </div>
    </div>
  );
}
