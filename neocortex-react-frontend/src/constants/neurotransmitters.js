export const NEUROTRANSMITTERS = [
  {
    key: 'serotonin',
    code: '5HT',
    label: 'Serotonin (5HT)',
    description: 'Mood, impulse control',
    deficitKey: 'serotonin_deficit',
  },
  {
    key: 'dopamine',
    code: 'DA',
    label: 'Dopamine (DA)',
    description: 'Reward, motivation, movement',
    deficitKey: 'dopamine_deficit',
  },
  {
    key: 'noradrenaline',
    code: 'NE',
    label: 'Noradrenaline (NE)',
    description: 'Arousal, attention, stress',
    deficitKey: 'noradrenaline_deficit',
  },
  {
    key: 'acetylcholine',
    code: 'ACh',
    label: 'Acetylcholine (ACh)',
    description: 'Memory, learning',
    deficitKey: 'acetylcholine_deficit',
  },
  {
    key: 'gaba',
    code: 'GABA',
    label: 'GABA',
    description: 'Primary inhibitory NT',
    deficitKey: 'gaba_deficit',
  },
  {
    key: 'glutamate',
    code: 'Glu',
    label: 'Glutamate (Glu)',
    description: 'Primary excitatory NT',
    deficitKey: 'glutamate_deficit',
  },
];

export const EMPTY_NT_PROFILE = NEUROTRANSMITTERS.reduce(
  (profile, nt) => ({ ...profile, [nt.key]: 0.0 }),
  {}
);

export const DISEASE_CATEGORIES = [
  'mood',
  'anxiety',
  'psychosis',
  'neurodevelopmental',
  'neurodegenerative',
  'movement',
  'neurological',
  'sleep',
  'custom',
];

const readProfile = (disease) => {
  if (!disease) return {};
  if (disease.profile) return disease.profile;
  return NEUROTRANSMITTERS.reduce(
    (profile, nt) => ({ ...profile, [nt.key]: disease[nt.deficitKey] ?? disease[nt.key] }),
    {}
  );
};

export const activeDeficits = (disease) => {
  const profile = readProfile(disease);
  return NEUROTRANSMITTERS.filter(
    (nt) => profile[nt.key] !== undefined && profile[nt.key] !== null && profile[nt.key] !== 0
  ).map((nt) => ({ ...nt, value: profile[nt.key] }));
};
