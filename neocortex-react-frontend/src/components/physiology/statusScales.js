const band = (value, thresholds, fallback) => {
  const match = thresholds.find((entry) => value < entry.below);
  return match ? { label: match.label, tone: match.tone } : fallback;
};

export const PHYSIO_STATUS = {
  heart_rate: (value) =>
    band(
      value,
      [
        { below: 0.4, label: 'Bradycardia', tone: 'plate' },
        { below: 0.6, label: 'Normal', tone: 'affirm' },
      ],
      { label: 'Tachycardia', tone: 'signal' }
    ),

  respiratory_rate: (value) =>
    band(
      value,
      [
        { below: 0.4, label: 'Slow', tone: 'plate' },
        { below: 0.6, label: 'Normal', tone: 'affirm' },
      ],
      { label: 'Hyperventilation', tone: 'caution' }
    ),

  skin_conductance: (value) =>
    band(
      value,
      [
        { below: 0.3, label: 'Calm', tone: 'affirm' },
        { below: 0.6, label: 'Moderate', tone: 'caution' },
      ],
      { label: 'High arousal', tone: 'signal' }
    ),

  muscle_tension: (value) =>
    band(
      value,
      [
        { below: 0.4, label: 'Relaxed', tone: 'affirm' },
        { below: 0.6, label: 'Normal', tone: 'plate' },
      ],
      { label: 'Tense', tone: 'caution' }
    ),

  gut_feeling: (value) =>
    band(
      value,
      [
        { below: 0.4, label: 'Discomfort', tone: 'signal' },
        { below: 0.6, label: 'Neutral', tone: 'mute' },
      ],
      { label: 'Comfort', tone: 'affirm' }
    ),

  temperature: (value) =>
    band(
      value,
      [
        { below: 0.4, label: 'Cold', tone: 'plate' },
        { below: 0.6, label: 'Normal', tone: 'plate' },
      ],
      { label: 'Hot', tone: 'plate' }
    ),

  pain: (value) =>
    band(
      value,
      [
        { below: 0.2, label: 'None', tone: 'affirm' },
        { below: 0.5, label: 'Mild', tone: 'caution' },
        { below: 0.8, label: 'Moderate', tone: 'caution' },
      ],
      { label: 'Severe', tone: 'signal' }
    ),

  fatigue: (value) =>
    band(
      value,
      [
        { below: 0.3, label: 'Energetic', tone: 'affirm' },
        { below: 0.6, label: 'Normal', tone: 'plate' },
      ],
      { label: 'Exhausted', tone: 'caution' }
    ),
};

export const PHYSIO_DESCRIPTIONS = {
  heart_rate: 'Cardiovascular marker',
  respiratory_rate: 'Breathing pattern',
  skin_conductance: 'Stress and arousal',
  muscle_tension: 'Body tension',
  gut_feeling: 'Visceral sensation',
  temperature: 'Thermal sensation',
  pain: 'Discomfort level',
  fatigue: 'Energy level',
};
