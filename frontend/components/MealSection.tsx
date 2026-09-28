import type { FoodEntry, MealType } from "@/lib/api";

interface Props {
  meal: MealType;
  entries: FoodEntry[];
  onDelete: (id: number) => void;
}

function macroSummary(entry: FoodEntry): string {
  const parts = [
    entry.protein_g !== null && `P ${entry.protein_g}g`,
    entry.carbs_g !== null && `C ${entry.carbs_g}g`,
    entry.fat_g !== null && `F ${entry.fat_g}g`,
  ].filter(Boolean);
  return parts.join(" · ");
}

export default function MealSection({ meal, entries, onDelete }: Props) {
  const subtotal = entries.reduce((sum, entry) => sum + entry.calories, 0);

  return (
    <div className="meal">
      <div className="meal-header">
        <h3>{meal}</h3>
        <span className="muted">{subtotal.toLocaleString()} kcal</span>
      </div>
      {entries.length === 0 ? (
        <p className="muted">Nothing logged</p>
      ) : (
        <ul className="entries">
          {entries.map((entry) => (
            <li key={entry.id}>
              <div>
                <strong>{entry.name}</strong>
                {entry.quantity && <span className="muted"> ({entry.quantity})</span>}
                <div className="muted small">{macroSummary(entry)}</div>
              </div>
              <div className="row">
                <span>{entry.calories} kcal</span>
                <button
                  type="button"
                  className="link-button"
                  onClick={() => onDelete(entry.id)}
                  aria-label={`Delete ${entry.name}`}
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
