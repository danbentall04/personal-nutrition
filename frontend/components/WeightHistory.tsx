import type { WeightEntry } from "@/lib/api";
import { formatShortDay } from "@/lib/dates";

export default function WeightHistory({ weights }: { weights: WeightEntry[] }) {
  if (weights.length === 0) {
    return <p className="muted">No weigh-ins yet.</p>;
  }

  return (
    <table className="table">
      <thead>
        <tr>
          <th>Date</th>
          <th className="num">kg</th>
          <th>Note</th>
        </tr>
      </thead>
      <tbody>
        {weights.map((w) => (
          <tr key={w.id}>
            <td>{formatShortDay(w.measured_on)}</td>
            <td className="num">{w.weight_kg.toFixed(2)}</td>
            <td className="muted">{w.note}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
