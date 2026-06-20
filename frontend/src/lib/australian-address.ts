export const AUSTRALIAN_STATES = [
  { value: "NSW", label: "New South Wales" },
  { value: "VIC", label: "Victoria" },
  { value: "QLD", label: "Queensland" },
  { value: "SA", label: "South Australia" },
  { value: "WA", label: "Western Australia" },
  { value: "TAS", label: "Tasmania" },
  { value: "ACT", label: "Australian Capital Territory" },
  { value: "NT", label: "Northern Territory" },
] as const;

export type AustralianState = (typeof AUSTRALIAN_STATES)[number]["value"];

export function isValidAustralianPostcode(value: string): boolean {
  const postcode = value.trim();
  if (!/^\d{4}$/.test(postcode)) return false;
  const num = Number(postcode);
  return num >= 200 && num <= 9999;
}

export function getPostcodeError(value: string): string | undefined {
  const trimmed = value.trim();
  if (!trimmed) return "Postcode is required";
  if (!/^\d{4}$/.test(trimmed)) return "Enter a 4-digit Australian postcode";
  if (!isValidAustralianPostcode(trimmed)) return "Enter a valid Australian postcode";
  return undefined;
}

export function isValidAustralianPhone(value: string): boolean {
  const digits = value.replace(/\D/g, "");
  return digits.length >= 8 && digits.length <= 10;
}

export function getPhoneError(value: string): string | undefined {
  const trimmed = value.trim();
  if (!trimmed) return "Phone number is required";
  if (!isValidAustralianPhone(trimmed)) {
    return "Enter a valid Australian phone number (e.g. 02 9123 4567)";
  }
  return undefined;
}

export function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}
