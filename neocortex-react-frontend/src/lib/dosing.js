export const doseRangeOf = (drug) => {
  if (Array.isArray(drug.dose_range) && drug.dose_range.length === 2) {
    return { min: drug.dose_range[0], max: drug.dose_range[1] };
  }
  const typical = drug.typical_dose_mg || 10;
  return { min: Math.max(1, typical * 0.5), max: typical * 2 };
};

export const doseStepFor = (range) => (range.max > 100 ? 10 : 1);

export const initialDoseOf = (drug) => drug.typical_dose_mg || drug.dose_range?.[0] || 10;

export const slugify = (value) => value.toLowerCase().replace(/\s+/g, '_');
