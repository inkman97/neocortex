export const compactCount = (value) => {
  if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000) return `${(value / 1000).toFixed(0)}K`;
  return String(value);
};

export const percent = (value, digits = 0) => `${((value ?? 0) * 100).toFixed(digits)}%`;

export const signedPercent = (value) => `${value > 0 ? '+' : ''}${Math.round(value * 100)}%`;

export const days = (hours, digits = 1) => (hours / 24).toFixed(digits);

export const timepointHours = (timepoint) =>
  timepoint?.hours ?? timepoint?.hours_after_dose ?? 0;

export const pluralDays = (count) => `${count} ${count === 1 ? 'day' : 'days'}`;
