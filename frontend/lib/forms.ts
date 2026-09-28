// Form inputs hold strings; the API wants numbers or null.

export function optionalNumber(value: string): number | null {
  return value.trim() === "" ? null : Number(value);
}

export function optionalText(value: string): string | null {
  return value.trim() === "" ? null : value.trim();
}

export function toInputValue(value: number | string | null): string {
  return value === null ? "" : String(value);
}
